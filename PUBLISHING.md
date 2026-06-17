# 发布到 GitHub

这个项目的 exe 文件较大，不要直接提交到 Git 仓库。推荐流程是：源码进仓库，exe 作为 GitHub Release 附件。

## 1. 提交源码

在安装 Git 后，在项目目录执行：

```powershell
git init
git branch -M main
git remote add origin https://github.com/HUNter-67/FormulaOcrTool.git
git add .
git commit -m "Initial FormulaOcrTool source release"
git push -u origin main
```

`.gitignore` 已经排除了 `dist/`、`build/`、`*.exe`、`__pycache__/` 等生成文件。

## 2. 发布 exe

1. 打开 https://github.com/HUNter-67/FormulaOcrTool/releases
2. 点击 `Create a new release`
3. Tag 填 `v1.0.0`
4. Title 填 `FormulaOcrTool v1.0.0`
5. 上传本地文件：`dist\FormulaOcrTool.exe`
6. 点击 `Publish release`

## 3. 推荐 Release 文案

```markdown
## FormulaOcrTool v1.0.0

Windows 本地公式 OCR 工具，支持截图识别和本地图片识别，输出 LaTeX 并自动复制到剪贴板。

### 使用方法

下载 `FormulaOcrTool.exe` 后双击运行。

### 注意

- 首次启动可能较慢，因为单文件 exe 需要解包运行依赖。
- Windows 安全提示或杀软提示时，请确认文件来源是本仓库 Release 页面。
- 建议在 Windows 10/11 上使用。
```
