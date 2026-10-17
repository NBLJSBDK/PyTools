# day-calculator

基于 PyQt5 的天数计算器：选两个日期，算相差多少天。

## 运行

需要 PyQt5。共享环境（仓库根目录 `.venv`）：

```powershell
cd D:\PyTools\day-calculator
D:\PyTools\.venv\Scripts\python.exe day-calculator.py
```

> NOTE: 环境不是固定的。除共享 venv 外，也可以选**不用环境**（全局装 PyQt5）、**目录内独立 venv**（`python -m venv venv`），或依赖重时改用 **uv**。选择标准见仓库根 [AGENTS.md](../AGENTS.md) 第五节。本工具的依赖清单在根 [requirements-gui.txt](../requirements-gui.txt)。

## 说明

- 两个日期用日历控件选，点"计算时间"出结果。
- 是 GUI 程序，但扩展名是 `.py`，运行时会有控制台窗口。
