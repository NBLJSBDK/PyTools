# hex-to-string

串口调试用的转换工具：把串口回显的 HEX 转成 UTF-8 文本，同时列出没能解码的部分。

## 运行

需要 PyQt5。共享环境（仓库根目录 `.venv`）：

```powershell
cd D:\PyTools\hex-to-string
D:\PyTools\.venv\Scripts\python.exe hex-to-text.pyw
```

或直接双击 `hex-to-text.pyw`（`.pyw` 双击不弹控制台窗口）。

> NOTE: 环境不是固定的。除共享 venv 外，也可以选**不用环境**（全局装 PyQt5）、**目录内独立 venv**（`python -m venv venv`），或依赖重时改用 **uv**。选择标准见仓库根 [AGENTS.md](../AGENTS.md) 第五节。本工具的依赖清单在根 [requirements-gui.txt](../requirements-gui.txt)。

## 说明

- 左边输入框粘贴 HEX（空格分隔或连续都行），右边实时显示 UTF-8 结果 + 未解码的 HEX。
- 专门为"串口回显里混着中文和裸字节"的场景做的。
