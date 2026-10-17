# qr

本地二维码生成器，改参数实时预览，不上传任何内容。

## 运行

需要 PyQt5 与 `qrcode`。共享环境（仓库根目录 `.venv`）：

```powershell
cd D:\PyTools\qr
D:\PyTools\.venv\Scripts\python.exe local_qr.pyw
```

或直接双击 `local_qr.pyw`。

> NOTE: 环境不是固定的。除共享 venv 外，也可以选**不用环境**（全局装 PyQt5）、**目录内独立 venv**（`python -m venv venv`），或依赖重时改用 **uv**。选择标准见仓库根 [AGENTS.md](../AGENTS.md) 第五节。本工具的依赖清单在根 [requirements-gui.txt](../requirements-gui.txt)。

## 说明

- 输入文本即时生成二维码，不需要点生成按钮。
- 支持自定义尺寸等参数，并带尺寸合法性校验。
- 纯本地生成，不联网。
