# FormulaOcrTool

一个 Windows 本地公式 OCR 小工具：截图或选择公式图片后，识别图片中的公式并输出 LaTeX，方便复制到 Word、MathType 或其他编辑器。可直接在Release里下载打包好的exe文件，exe无需安装python也能运行，下载后无需联网，适合在不能联网的工作机中使用。

## 功能

- 截图识别：拖拽框选屏幕上的公式区域。
- 图片识别：选择本地 `png/jpg/jpeg/bmp/webp` 图片。
- 自动复制：识别完成后自动把 LaTeX 复制到剪贴板。
- 公式预览：使用 matplotlib 渲染 LaTeX 预览。(有时候会出现渲染失败的问题,但不影响输出LaTeX)
- 注意！！！对一些希腊字母的识别不是很准确需要手动检查修改


## 源码运行

建议使用 Python 3.12 或 3.13。安装 Python 时请勾选：

```text
Add python.exe to PATH
```

首次安装依赖：

```powershell
.\setup_env.ps1
```

如果 Python 没有加入 PATH，但你知道 `python.exe` 的路径：

```powershell
.\setup_env.ps1 -PythonExe "C:\Path\To\python.exe"
```

启动：

```powershell
.\run.bat
```

检查环境：

```powershell
.\check_env.bat
```

## 打包 exe

生成单文件 Windows exe：

```powershell
.\build_exe.ps1
```

输出文件：

```text
dist\FormulaOcrTool.exe
```

打包脚本会：

- 使用 `%LOCALAPPDATA%\FormulaOcrTool\venv313` 虚拟环境。
- 安装/确认 PyInstaller 和 CPU 版 PyTorch。
- 校验 pix2tex 模型文件是否齐全。
- 把 pix2tex 模型目录和运行依赖打入单文件 exe。

注意：生成的 exe 体积较大，不建议提交进 Git 仓库。请通过 GitHub Releases 上传。



## 项目结构

```text
app/
  main.py                 # PySide6 GUI 主程序
  ocr.py                  # pix2tex 模型加载与识别
  image_preprocess.py     # 公式图片预处理
  latex_postprocess.py    # LaTeX 输出后处理
  screenshot.py           # 截图框选
  check_env.py            # 环境检查
scripts/
  prepare_model_cache.py  # 打包前校验 pix2tex 模型文件
build_exe.ps1             # 单文件 exe 打包脚本
FormulaOcrTool.spec       # PyInstaller 配置
setup_env.ps1             # 首次安装环境
run.bat                   # 启动工具
check_env.bat             # 检查环境
requirements.txt          # Python 依赖
```

## 说明

pix2tex 的首次模型准备可能需要联网。打包后的 exe 会内置 pix2tex 模型文件，适合离线分发，但建议在干净 Windows 电脑上做一次实机验证。
