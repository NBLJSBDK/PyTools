# typing-practice

盲打（打字）训练工具：多种训练模式、词表选择、音效反馈、逐题耗时与卡顿分析，训练记录写入 CSV。

## 运行

依赖 PyQt5。目前提供的是 Linux 脚本：

```bash
./install.sh        # 首次：创建 venv 并安装 PyQt5
./run.sh            # 启动，日志写到 /tmp/typing-practice.log
```

**Windows 上直接运行**（不依赖那两个 sh 脚本，代码本身跨平台）：

```powershell
cd D:\PyTools\typing-practice
python -m venv venv
.\venv\Scripts\python.exe -m pip install PyQt5==5.15.10
.\venv\Scripts\python.exe typing_practice.py
```

## 环境

需要 PyQt5。可选两种：

**本目录独立环境（原始用法，Linux 脚本）**

```bash
./install.sh
```

**仓库根目录共享 `.venv`**

```powershell
D:\PyTools\.venv\Scripts\python.exe typing_practice.py
```

> NOTE: 环境不固定，也可以全局装 PyQt5 直接跑，或改用 uv，判断标准见仓库根 [AGENTS.md](../AGENTS.md) 第五节。

## 说明

- `install.sh` / `run.sh` 是 **Linux 专属**：用 `venv/bin/python`、`export QT_IM_MODULE=fcitx`、日志重定向到 `/tmp/`。
- Windows 上用 venv 安装时，**建议只钉 `PyQt5==5.15.10`**，不要按根 `requirements.txt` 钉死 `PyQt5-sip==12.13.0`（那个版本对较新的 Python 需要现场编译）。
- 是 GUI 程序，运行时会带一个控制台窗口。

## 使用

- **词表**：`dict\` 下的 `.txt`，在界面"词表"下拉框里切换，支持整行注释、行尾注释和空行。
- **模式**：顺序学习、乱序巩固、单次测速。
- **配置**：`config.ini` 存默认模式、次数、输入法、自动提交等；程序退出时自动保存当前设置。
- **记录**：`typing_log.csv`（每局汇总）与 `typing_detail_log.csv`（逐题时间、提交间隔、错误次数）。
- **成就**：`achievement.txt` 记录里程碑。
- 第 1 题作为热身题，保留逐题记录但**不参与**提交间隔、卡顿、慢题和慢词统计。
- 音效在 `misc\EncourageSound\`（14 个）与 `misc\PunishmentSound\`（3 个）。
