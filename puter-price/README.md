# puter-price

按配置单计算装机总价：读配置文件里的硬件与价格，用表格展示并可导出。

## 运行

需要 PyQt5。共享环境（仓库根目录 `.venv`）：

```powershell
cd D:\PyTools\puter-price
D:\PyTools\.venv\Scripts\python.exe price-calculator.py
```

> NOTE: 环境不是固定的。除共享 venv 外，也可以选**不用环境**（全局装 PyQt5）、**目录内独立 venv**（`python -m venv venv`），或依赖重时改用 **uv**。选择标准见仓库根 [AGENTS.md](../AGENTS.md) 第五节。本工具的依赖清单在根 [requirements-gui.txt](../requirements-gui.txt)。

## 说明

- 目录内的 `梦中情机.txt`、`max.txt` 是配置单示例，可以照格式改。
- 界面里能选择文件加载配置、编辑表格、算总价。
- 改价格不用改代码，改文本配置即可。
