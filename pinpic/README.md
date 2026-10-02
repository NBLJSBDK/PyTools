# Pinpic

把一张图片贴在桌面最上层的小工具，支持 Linux、macOS、Windows（需要 PySide6）。

```bash
python pinpic.py 图片路径
```

也可以把图片直接拖到 `pinpic.py` 图标上。程序会自动脱离启动它的终端，关闭终端不会影响贴图。

- 左键按住：拖动贴图
- 滚动：以鼠标位置为中心放大/缩小
- `Ctrl` + 滚动：调节透明度（15%～100%）
- 中键：恢复初始大小，鼠标下的图片内容保持不动
- 右键：最小化贴图，保留任务栏图标
- `Esc`：关闭贴图

启动后会在右下角系统托盘显示 Pinpic 图标，同时在底部任务管理器显示窗口图标。
单击托盘图标可隐藏/显示贴图，右键图标可勾选“任务管理器”和“置顶”，
也可以选择透明度或退出。

如需固定到 KDE 的“已固定应用”，请在任务管理器中的 Pinpic 图标上右键，选择“固定到任务管理器”。

退出请使用托盘菜单中的“退出 Pinpic”，或按 `Esc` 关闭贴图。

## 环境

需要 PySide6，依赖声明见同目录的 `requirements.txt`（`PySide6>=6.6`）。

默认用本目录的独立环境（`install.sh` 创建 `venv/`）：

```bash
./install.sh
```

Windows 上这两个脚本跑不了，可以自己建环境：

```powershell
python -m venv venv
.\venv\Scripts\python.exe -m pip install PySide6
.\venv\Scripts\python.exe pinpic.py 图片路径
```

> NOTE: 环境不固定，也可以不用独立环境（全局装 PySide6）、或用仓库根目录的共享 `.venv`、或改用 uv，判断标准见仓库根 [AGENTS.md](../AGENTS.md) 第五节。

## 说明

- 首次使用先运行 `./install.sh`，之后用 `./run.sh 图片路径` 启动。
- 用项目自己的环境直接运行：`./.venv/bin/python pinpic.py 图片路径`；想继续用 `python pinpic.py`，先 `source .venv/bin/activate`。
- `install.sh` 与 `run.sh` 是为 **Linux** 写的：除了创建 `venv`，还会把系统 fcitx5 的 Qt 输入法插件软链进环境，并检查 GStreamer 解码器；`run.sh` 使用 `venv/bin/python`。
