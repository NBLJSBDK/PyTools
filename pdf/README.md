# pdf

PDF 处理工具集：拼接、提取页面、旋转、加水印、加密解密，另有一个 Photoshop 批处理脚本。

### 运行

```powershell
# 图形界面（可双击）
D:\PyTools\.venv\Scripts\python.exe pdf-merger.pyw      # 拖拽排序后拼接
D:\PyTools\.venv\Scripts\python.exe pdf-password.pyw    # 加密 / 解密

# 命令行
D:\PyTools\.venv\Scripts\python.exe merge-pdf.py 1.pdf 2.pdf 3.pdf
D:\PyTools\.venv\Scripts\python.exe extract-pages.py 输入.pdf
D:\PyTools\.venv\Scripts\python.exe rotate-pages.py
D:\PyTools\.venv\Scripts\python.exe watermark.py
```

### 环境

本目录带有自己的 `requirements.txt`（PyPDF2、reportlab、PyQt5）。共享环境（仓库根目录 `.venv`）：

```powershell
D:\PyTools\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

> NOTE: 环境不固定，也可以在本目录建独立 venv 或改用 uv，判断标准见仓库根 [AGENTS.md](../AGENTS.md) 第五节。

## 各脚本

| 脚本 | 做什么 | 入口 |
|---|---|---|
| `pdf-merger.pyw` | 拼接：拖入多个 PDF，可上下排序后保存 | 双击 / GUI |
| `pdf-password.pyw` | 给 PDF 加密，或解密已加密的 PDF | 双击 / GUI，支持拖入 |
| `merge-pdf.py` | 命令行拼接，输出 `merged.pdf` | 把多个 PDF 拖到脚本上 |
| `extract-pages.py` | 取出指定页码范围，输出 `原名_起-止.pdf` | 拖入 PDF，运行后输入起止页 |
| `rotate-pages.py` | 每页旋转 90° | 无参数，直接运行 |
| `watermark.py` | 用**文件名当水印文字**，批量给 PDF 加水印 | 无参数，直接运行 |
| `批量把照片调成扫描效果.js` | Photoshop 批处理脚本（不是 Python） | Photoshop 里运行 |

## 说明

- `watermark.py` **必须和字体 `仿宋_GB2312.TTF` 在同一目录**，字体名写死在脚本第 11 行，换字体要改代码。
- `watermark.py` 与 `rotate-pages.py` 的输入输出是**写死的相对路径**：`watermark.py` 读同目录的 PDF，`rotate-pages.py` 固定读 `1.pdf` 写 `rotated_1.pdf`，用之前先确认或改代码。
- `merge-pdf.py` 与 `pdf-merger.pyw` 都能拼接，区别是一个命令行、一个拖拽界面。
- `pdf-merger.pyw` 出错会把堆栈写到同目录的 `startup_error.log`（已被 git 忽略）。
