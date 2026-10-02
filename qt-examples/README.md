# qt-examples

PyQt5 的布局与控件示例，用来查用法、抄片段。

## 运行

需要 PyQt5。共享环境（仓库根目录 `.venv`）：

```powershell
cd D:\PyTools\qt-examples
D:\PyTools\.venv\Scripts\python.exe qt-demo.pyw
D:\PyTools\.venv\Scripts\python.exe qt-layout-demo.pyw
D:\PyTools\.venv\Scripts\python.exe qt-progress-demo.py
```

`.pyw` 可以直接双击。

## 说明

- 这是**参考代码**，不是可用工具；写 PyQt5 界面时来抄结构。
- 三个示例互相独立，随便挑一个跑。

## 各示例

| 脚本 | 演示什么 |
|---|---|
| `qt-demo.pyw` | 综合演示：各种常用控件的摆放与信号连接 |
| `qt-layout-demo.pyw` | 布局：`QVBoxLayout` / `QHBoxLayout` / `QGridLayout` / `QFormLayout` 的用法 |
| `qt-progress-demo.py` | 进度条与标签的联动 |

> NOTE: 环境不是固定的。除共享 venv 外，也可以选**不用环境**（全局装 PyQt5）、**目录内独立 venv**（`python -m venv venv`），或依赖重时改用 **uv**。选择标准见仓库根 [AGENTS.md](../AGENTS.md) 第五节。本工具的依赖清单在根 [requirements-gui.txt](../requirements-gui.txt)。
