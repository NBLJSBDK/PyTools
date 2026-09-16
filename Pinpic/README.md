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

首次使用先安装依赖：

```bash
./install.sh
```

运行：

```bash
./run.sh 图片路径
```

运行时使用项目自己的环境：

```bash
./.venv/bin/python pinpic.py 图片路径
```

如果希望继续使用 `python pinpic.py 图片路径`，请先在当前终端激活环境：

```bash
source .venv/bin/activate
python pinpic.py 图片路径
```
