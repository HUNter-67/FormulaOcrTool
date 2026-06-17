from __future__ import annotations

import sys
import tempfile
from io import BytesIO
from pathlib import Path

from PIL import Image
from PySide6.QtCore import QObject, QRunnable, Qt, QThreadPool, Signal, Slot
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.ocr import FormulaRecognizer, RecognitionResult
from app.screenshot import ScreenshotOverlay


class WorkerSignals(QObject):
    finished = Signal(object)
    failed = Signal(str)


class RecognizeWorker(QRunnable):
    def __init__(self, recognizer: FormulaRecognizer, image_path: Path) -> None:
        super().__init__()
        self.signals = WorkerSignals()
        self.recognizer = recognizer
        self.image_path = image_path

    @Slot()
    def run(self) -> None:
        try:
            result = self.recognizer.recognize_path(self.image_path)
        except Exception as exc:
            self.signals.failed.emit(str(exc))
            return
        self.signals.finished.emit(result)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("本地公式识别工具")
        self.resize(900, 650)

        self.recognizer = FormulaRecognizer()
        self.thread_pool = QThreadPool.globalInstance()
        self.last_image_path: Path | None = None
        self.overlay: ScreenshotOverlay | None = None
        self.temp_dir = Path(tempfile.gettempdir()) / "formula_ocr_tool"
        self.temp_dir.mkdir(parents=True, exist_ok=True)

        QApplication.instance().setProperty("last_capture_path", str(self.temp_dir / "last_capture.png"))

        self.status_label = QLabel("准备就绪。首次源码识别可能会联网下载模型，打包版会使用内置离线模型。")
        self.preview_label = QLabel("图片预览")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumHeight(220)
        self.preview_label.setStyleSheet("border: 1px solid #cccccc; background: #fafafa; color: #666666;")

        self.render_label = QLabel("公式预览")
        self.render_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.render_label.setMinimumHeight(120)
        self.render_label.setStyleSheet("border: 1px solid #cccccc; background: #ffffff; color: #666666;")

        self.latex_edit = QTextEdit()
        self.latex_edit.setPlaceholderText("识别出的 LaTeX 会显示在这里")

        self.capture_button = QPushButton("截图识别")
        self.open_button = QPushButton("选择图片识别")
        self.copy_button = QPushButton("复制 LaTeX")
        self.retry_button = QPushButton("重试识别")

        self.capture_button.clicked.connect(self.capture_region)
        self.open_button.clicked.connect(self.open_image)
        self.copy_button.clicked.connect(self.copy_latex)
        self.retry_button.clicked.connect(self.retry_last)

        button_row = QHBoxLayout()
        button_row.addWidget(self.capture_button)
        button_row.addWidget(self.open_button)
        button_row.addWidget(self.copy_button)
        button_row.addWidget(self.retry_button)
        button_row.addStretch()

        layout = QVBoxLayout()
        layout.addLayout(button_row)
        layout.addWidget(self.status_label)
        layout.addWidget(self.preview_label, 1)
        layout.addWidget(self.render_label, 1)
        layout.addWidget(QLabel("LaTeX 输出"))
        layout.addWidget(self.latex_edit, 2)

        root = QWidget()
        root.setLayout(layout)
        self.setCentralWidget(root)

    def capture_region(self) -> None:
        self.status_label.setText("拖拽选择公式区域，按 Esc 取消。")
        self.hide()
        QApplication.processEvents()
        self.overlay = ScreenshotOverlay()
        self.overlay.captured.connect(self._on_capture)
        self.overlay.canceled.connect(self._on_capture_canceled)
        self.overlay.showFullScreen()

    def open_image(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "选择公式图片",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.webp);;All Files (*)",
        )
        if path:
            self.start_recognition(Path(path))

    def retry_last(self) -> None:
        if not self.last_image_path or not self.last_image_path.exists():
            QMessageBox.information(self, "没有可重试的图片", "请先截图或选择一张图片。")
            return
        self.start_recognition(self.last_image_path)

    def copy_latex(self) -> None:
        latex = self.latex_edit.toPlainText().strip()
        if not latex:
            QMessageBox.information(self, "没有内容", "当前没有可复制的 LaTeX。")
            return
        QApplication.clipboard().setText(latex)
        self.status_label.setText("LaTeX 已复制到剪贴板。")

    def _on_capture(self, path: str) -> None:
        self.show()
        self.raise_()
        self.activateWindow()
        self.start_recognition(Path(path))

    def _on_capture_canceled(self) -> None:
        self.show()
        self.raise_()
        self.activateWindow()
        self.status_label.setText("已取消截图。")

    def start_recognition(self, image_path: Path) -> None:
        self.last_image_path = image_path
        self.status_label.setText("正在加载模型并识别，请稍候...")
        self._set_buttons_enabled(False)
        self._show_image(Image.open(image_path))

        worker = RecognizeWorker(self.recognizer, image_path)
        worker.signals.finished.connect(self._recognition_finished)
        worker.signals.failed.connect(self._recognition_failed)
        self.thread_pool.start(worker)

    def _recognition_finished(self, result: RecognitionResult) -> None:
        self._set_buttons_enabled(True)
        self.latex_edit.setPlainText(result.latex)
        QApplication.clipboard().setText(result.latex)
        self._show_image(result.image)
        self._render_latex_preview(result.latex)
        self.status_label.setText("识别完成，LaTeX 已自动复制到剪贴板。")

    def _recognition_failed(self, message: str) -> None:
        self._set_buttons_enabled(True)
        self.status_label.setText("识别失败。")
        QMessageBox.critical(self, "识别失败", message)

    def _show_image(self, image: Image.Image) -> None:
        image = image.convert("RGBA")
        data = image.tobytes("raw", "RGBA")
        qimage = QImage(data, image.width, image.height, QImage.Format.Format_RGBA8888).copy()
        pixmap = QPixmap.fromImage(qimage)
        pixmap = pixmap.scaled(
            self.preview_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.preview_label.setPixmap(pixmap)

    def _render_latex_preview(self, latex: str) -> None:
        try:
            import matplotlib

            matplotlib.use("Agg")
            import matplotlib.pyplot as plt

            expression = latex.strip()
            if not expression:
                self.render_label.setText("公式预览")
                return
            if not (expression.startswith("$") and expression.endswith("$")):
                expression = f"${expression}$"

            fig = plt.figure(figsize=(8, 1.8), dpi=150)
            fig.patch.set_facecolor("white")
            fig.text(0.5, 0.5, expression, ha="center", va="center", fontsize=22)
            buffer = BytesIO()
            fig.savefig(buffer, format="png", bbox_inches="tight", pad_inches=0.2)
            plt.close(fig)
            buffer.seek(0)

            image = Image.open(buffer).convert("RGBA")
            data = image.tobytes("raw", "RGBA")
            qimage = QImage(data, image.width, image.height, QImage.Format.Format_RGBA8888).copy()
            pixmap = QPixmap.fromImage(qimage)
            pixmap = pixmap.scaled(
                self.render_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self.render_label.setPixmap(pixmap)
        except Exception:
            self.render_label.setText("公式预览渲染失败，但 LaTeX 文本已保留。")

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        if self.last_image_path and self.last_image_path.exists():
            try:
                self._show_image(Image.open(self.last_image_path))
            except Exception:
                pass

    def _set_buttons_enabled(self, enabled: bool) -> None:
        self.capture_button.setEnabled(enabled)
        self.open_button.setEnabled(enabled)
        self.retry_button.setEnabled(enabled)
        self.copy_button.setEnabled(enabled)


def main() -> int:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
