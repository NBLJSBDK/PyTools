# shot-cp

常驻后台监听全局热键 `Ctrl+V`，把剪贴板里的图片存成当前目录下的时间戳 PNG。

## 运行

需要 `pynput` 与 `Pillow`。共享环境（仓库根目录 `.venv`）：

```powershell
cd D:\PyTools\shot-cp
D:\PyTools\.venv\Scripts\python.exe clip2file.py
```

启动后保持窗口开着，按 `Ctrl+V` 即保存，`Ctrl+C` 退出。

> NOTE: 环境不是固定的。除共享 venv 外，也可以选**不用环境**（全局装 PyQt5）、**目录内独立 venv**（`python -m venv venv`），或依赖重时改用 **uv**。选择标准见仓库根 [AGENTS.md](../AGENTS.md) 第五节。本工具的依赖清单在根 [requirements-gui.txt](../requirements-gui.txt)。

## 说明

- 文件名格式为 `20261002_153012_123.png`（精确到毫秒），保存在**脚本所在目录**。
- 剪贴板里没有图片时会提示，不会生成空文件。
- 脚本上半部分还留着一份**鼠标右键触发**的旧实现（整段被注释），现在启用的是 `Ctrl+V` 版本。
- 是全局热键，**会抢占所有程序的 Ctrl+V**，不用时记得关掉。
