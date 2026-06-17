from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from PIL import ImageGrab
from PySide6.QtCore import QPoint, QRect, Qt, Signal
from PySide6.QtGui import QColor, QGuiApplication, QPainter, QPen
from PySide6.QtWidgets import QApplication, QWidget


@dataclass
class CaptureResult:
    image_path: str


class ScreenshotOverlay(QWidget):
    captured = Signal(str)
    canceled = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setCursor(Qt.CursorShape.CrossCursor)

        geometry = QGuiApplication.primaryScreen().virtualGeometry()
        self.setGeometry(geometry)

        self._start: Optional[QPoint] = None
        self._end: Optional[QPoint] = None

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._start = event.position().toPoint()
            self._end = self._start
            self.update()

    def mouseMoveEvent(self, event) -> None:
        if self._start is not None:
            self._end = event.position().toPoint()
            self.update()

    def mouseReleaseEvent(self, event) -> None:
        if event.button() != Qt.MouseButton.LeftButton or self._start is None or self._end is None:
            return

        rect = QRect(self._start, self._end).normalized()
        self.hide()
        QApplication.processEvents()

        if rect.width() < 8 or rect.height() < 8:
            self.canceled.emit()
            self.close()
            return

        device_ratio = self.devicePixelRatioF()
        left = int((self.x() + rect.left()) * device_ratio)
        top = int((self.y() + rect.top()) * device_ratio)
        right = int((self.x() + rect.right()) * device_ratio)
        bottom = int((self.y() + rect.bottom()) * device_ratio)

        image = ImageGrab.grab(bbox=(left, top, right, bottom), all_screens=True)
        path = QApplication.instance().property("last_capture_path")
        if not path:
            path = "last_capture.png"
        image.save(path)
        self.captured.emit(path)
        self.close()

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key.Key_Escape:
            self.canceled.emit()
            self.close()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 90))

        if self._start is None or self._end is None:
            return

        rect = QRect(self._start, self._end).normalized()
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
        painter.fillRect(rect, QColor(0, 0, 0, 0))
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
        painter.setPen(QPen(QColor(20, 120, 255), 2))
        painter.drawRect(rect)
