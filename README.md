# PyTools

个人自用的 Python 小工具集合。17 个工具各占一个目录、互不依赖，按需单独运行。

- **规模**：32 个脚本，约 4200 行 Python
- **界面**：多数是命令行脚本；部分用 PyQt5 做窗口；贴图工具用 PySide6
- **环境**：不强制。只用标准库的直接跑，要依赖的用 `venv` 或 `uv`
- **许可证**：[GPL-3.0](LICENSE)

## 工具一览

| 工具 | 用途 | 入口 | 依赖 |
|---|---|---|---|
| [asr](asr/README.md) | 录音转带时间戳文稿（腾讯云识别） | 命令行 | 腾讯云 SDK、ffmpeg |
| [typing-practice](typing-practice/README.md) | 盲打训练，含词表、音效、成绩统计 | GUI | PyQt5 |
| [pdf](pdf/README.md) | 拼接、取页、旋转、水印、加解密 | GUI + 命令行 | PyPDF2、pypdf、reportlab |
| [ffmpeg](ffmpeg/README.md) | 音频提取、压缩、转封装、目录树打印 | 命令行 | 外部 ffmpeg |
| [pinpic](pinpic/README.md) | 把图片钉在桌面最上层 | GUI | PySide6 |
| [puter-price](puter-price/README.md) | 按配置单算装机价格 | GUI | PyQt5 |
| [hash](hash/README.md) | 文件哈希校验、两文件对比 | GUI + 命令行 | PyQt5（对比脚本仅标准库） |
| [qr](qr/README.md) | 本地生成二维码，实时预览 | GUI | PyQt5、qrcode |
| [hex-to-string](hex-to-string/README.md) | 串口 HEX 回显转 UTF-8 | GUI | PyQt5 |
| [image-sorter](image-sorter/README.md) | 按哈希与规则整理图片，自动去重 | 命令行 | exifread、tqdm |
| [file-dedup](file-dedup/README.md) | 按内容查重，确认后移动重复项 | 命令行 | 仅标准库 |
| [prefix-adder](prefix-adder/README.md) | 批量给文件名加前缀（支持拼音） | GUI | PyQt5、pypinyin |
| [prefix-viewer](prefix-viewer/README.md) | 读文件头字节，判断真实类型 | 命令行 | 仅标准库 |
| [bookmark](bookmark/README.md) | 从书签 HTML 里找出重复网址 | 命令行 | beautifulsoup4 |
| [day-calculator](day-calculator/README.md) | 两个日期算相差天数 | GUI | PyQt5 |
| [shot-cp](shot-cp/README.md) | 按 `Ctrl+V` 把剪贴板图片存成 PNG | 常驻运行 | pynput、Pillow |
| [qt-examples](qt-examples/README.md) | PyQt5 布局与控件示例（参考代码） | GUI | PyQt5 |

每个工具目录里都有一份 `README.md`，写明怎么装、怎么跑、输出在哪。

## 快速开始

```powershell
# 1) 只用标准库的工具，直接跑
python file-dedup\find-duplicates.py

# 2) 需要依赖的工具：先建共享环境，再跑
cd D:\PyTools
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-gui.txt
.\.venv\Scripts\python.exe qr\local_qr.pyw

# 3) 依赖较重的 asr 用 uv 管理
cd asr
uv sync
uv run python main.py 录音.mp3
```

## 环境

**环境不固定，按依赖轻重选；同一个工具不要混用多种方式。**

| 方式 | 什么时候用 | 怎么用 |
|---|---|---|
| 不用环境 | 只用标准库 | `python 脚本路径` |
| 共享 venv | 依赖少（几个纯 Python 包，或有预编译包的库） | 仓库根 `.venv` + [requirements-gui.txt](requirements-gui.txt) |
| 独立 venv | 需要与其它工具隔离 | 工具目录内 `python -m venv venv` |
| uv 工程 | 依赖重、需要精确锁版本或跨平台复现 | `pyproject.toml` + `uv.lock` |

判断"重不重"看三点：第三方依赖数量、是否需要现场编译（带 C 扩展的包）、依赖树深度。

当前分工：`ffmpeg`、`file-dedup`、`prefix-viewer`、`hash/check_hash.py` 直接运行；需要 PyQt5 等少量依赖的用共享 venv；`asr` 用 uv；`typing-practice`、`pinpic` 各自带 `install.sh` / `run.sh`（Linux 脚本，Windows 上需自行建环境）。

> NOTE: 依赖声明必须进仓库（`requirements-gui.txt`、目录内的 `requirements.txt`、或 `uv.lock`）；**环境本身不入库**——它含本机绝对路径、跨平台不可移植，换机器靠重装而不是拷贝。

## 目录结构

```text
PyTools/
├── asr/                  语音转文字（uv 管理）
├── bookmark/             书签重复检测
├── day-calculator/       天数计算器
├── ffmpeg/               音视频处理
├── file-dedup/           文件查重
├── hash/                 文件哈希校验
├── hex-to-string/        HEX 转字符串
├── image-sorter/         图片整理
├── pdf/                  PDF 工具集
├── pinpic/               桌面贴图
├── prefix-adder/         批量加前缀
├── prefix-viewer/        查看文件头字节
├── puter-price/          装机价格计算
├── qr/                   本地二维码
├── qt-examples/          PyQt5 示例
├── shot-cp/              剪贴板图片保存
└── typing-practice/      盲打训练

根目录另有：AGENTS.md（协作约定）、requirements.txt（历史依赖合集）、
requirements-gui.txt（GUI 工具依赖）、.gitattributes（行尾规则）、
.gitignore、LICENSE
```

## 说明

- **Python 版本**：多数工具在 3.10+ 可用；`asr` 声明 `>=3.10`。
- **外部程序**：`ffmpeg` 目录下的脚本与 `asr` 都要求 `ffmpeg` / `ffprobe` 在 `PATH` 里。
- **平台**：以 Windows 为主要使用环境；`typing-practice`、`pinpic` 的环境脚本是 Linux 专属，`asr/splitter.py` 目前依赖 WSL（详见 [AGENTS.md](AGENTS.md) 第七节）。
- **密钥**：`asr` 需要腾讯云密钥，写在 `asr/api_keys.json`（已被忽略，不会提交）。
- **约定**：命名、环境选择、提交规范等，见 [AGENTS.md](AGENTS.md)。

## 许可证

[GPL-3.0](LICENSE)
