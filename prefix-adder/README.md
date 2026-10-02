# prefix-adder

批量给文件名加前缀，中文文件名可以先自动转成拼音再当前缀。

## 运行

需要 PyQt5 与 `pypinyin`。共享环境（仓库根目录 `.venv`）：

```powershell
cd D:\PyTools\prefix-adder
D:\PyTools\.venv\Scripts\python.exe add-prefix.py
```

> NOTE: 环境不是固定的。除共享 venv 外，也可以选**不用环境**（全局装 PyQt5）、**目录内独立 venv**（`python -m venv venv`），或依赖重时改用 **uv**。选择标准见仓库根 [AGENTS.md](../AGENTS.md) 第五节。本工具的依赖清单在根 [requirements-gui.txt](../requirements-gui.txt)。

## 说明

- 窗口里可以选**多个文件**或**一整个文件夹**。
- 前缀可用中文，脚本用 `pypinyin` 转拼音，也会给出已有前缀的提示。
- 改名是就地进行的，重要目录建议先备份。
