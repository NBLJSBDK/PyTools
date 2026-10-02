# PyTools - Python 工具集

这是一个存放自制Python脚本工具的仓库，包含各种实用的小工具和脚本。

## 目录结构

```
PyTools/
├── asr/                  # 语音转文字（腾讯云 ASR）
├── bookmark/             # 书签重复检测
├── day-calculator/       # 天数计算器
├── ffmpeg/               # 音视频处理工具
├── file-dedup/           # 文件查重工具
├── hash/                 # 文件哈希计算
├── hex-to-string/        # HEX 转字符串
├── image-sorter/         # 图片整理
├── pdf/                  # PDF 处理工具集
├── pinpic/               # 桌面贴图
├── prefix-adder/         # 批量加前缀
├── prefix-viewer/        # 查看文件头字节
├── puter-price/          # 硬件配置价格计算
├── qr/                   # 本地二维码生成
├── qt-examples/          # PyQt 示例程序
├── shot-cp/              # 剪贴板图片保存
└── typing-practice/      # 盲打训练工具
```

## 主要功能

### 1. 语音转文字（腾讯云 ASR）
- 功能:调用腾讯云一句话识别接口，将录音转写为带时间戳的文稿
- 项目目录:`asr/`
- 主程序:`asr/main.py`，Windows 下可双击 `asr/asr.bat`，也可把音频文件拖到 `main.py` 上
- 依赖声明:`asr/pyproject.toml` 与 `asr/uv.lock`（需自行创建虚拟环境并安装）
- 密钥配置:复制 `asr/api_keys.json.example` 为 `asr/api_keys.json` 后填入腾讯云密钥，该文件已被忽略，不会提交
- 长音频:`asr/splitter.py` 用 ffmpeg 静音检测自动切分，单段不超过 55 秒
- 参数:`--speaker 2` 角色分离、`--dialect canton` 等方言、`--no-timestamps` 纯文本、`--merge/--separate` 多文件处理
- 输出位置:转写结果写到音频同目录的 `.txt`，切分片段存放在 `asr/output/<音频名>/`（该目录已被忽略）

### 2. 盲打训练
- 功能:PyQt5 打字练习工具，包含多种训练模式、配置、日志和音效反馈
- 项目目录:`typing-practice/`
- 启动脚本:`typing-practice/run.sh`
- 主程序:`typing-practice/typing_practice.py`
- 配置文件:`typing-practice/config.ini`
- 训练词表:`typing-practice/dict/` 下的 `.txt` 文件，可在程序的“词表”选择框中切换，支持整行注释、行尾注释和空行
- 训练记录:`typing-practice/typing_log.csv` 和 `typing-practice/achievement.txt`
- 统计字段:目标字数、实际提交字数、正确字数和每分钟输入字数
- 逐题记录:`typing-practice/typing_detail_log.csv`，包含题目显示时间、正确提交时间、提交间隔和错误尝试次数
- 卡顿分析:第 1 题作为热身题保留逐题记录但不参与提交间隔、卡顿、慢题和慢词统计
- 输入行为:空白回车不会计错、播放惩罚音或启动计时
- 配置保存:程序退出时保存当前训练模式、次数、输入法和自动提交设置
- 资源文件:音效文件存放在`typing-practice/misc/`目录下

盲打训练支持顺序学习、乱序巩固和单次测速三种模式，也支持输入法记录、自动提交和失焦暂停。

### 3. 文件查重
- 功能:按内容查找重复文件，确认后可移动
- 主程序:`file-dedup/find-duplicates.py`

### 4. FFmpeg工具集
- 功能:音视频处理工具
- 包含:
  - `extract-audio.py`（提取音频）
  - `compress-audio.py`（压缩音频）
  - `flv-to-mp4.py`（FLV 转 MP4）

### 5. Hash计算
- 功能:文件哈希值计算
- 主程序:`hash/hash.pyw`

### 6. PDF工具集
- 功能:PDF文件处理
- 包含:
  - `merge-pdf.py`（命令行，把 PDF 文件拖到脚本上运行）
  - `pdf-merger.pyw`（tkinter 图形界面，支持拖拽、排序后拼接）
  - `extract-pages.py`（提取指定页码范围）
  - `pdf-password.pyw`（加密解密，拖拽界面）
  - `watermark.py`（加水印）
  - `rotate-pages.py`（旋转页面）
  - `mkv-to-mp4.py`（MKV 转 MP4，处理字幕）
  - 字体文件:`仿宋_GB2312.TTF`

### 7. 配置计算器
- 功能:硬件配置价格计算
- 包含:
  - `price-calculator.py`
  - `梦中情机.txt`（配置模板）

### 8. PyQt示例
- 功能:PyQt GUI编程示例
- 包含:
  - `qt-progress-demo.py`（进度条）
  - `qt-layout-demo.pyw`（布局）
  - `qt-demo.pyw`（综合演示）

## 环境与依赖

本仓库的工具按依赖轻重分三类，**不要混用**：

| 类型 | 适用工具 | 怎么装 |
|---|---|---|
| 共享 venv（推荐） | 所有要 PyQt5 或少量依赖的 GUI/命令行工具 | 在仓库根目录建一个 `.venv`，装 [requirements-gui.txt](requirements-gui.txt) |
| uv 工程 | `asr` | 在 `asr/` 下 `uv sync`（依赖腾讯云 SDK 与 COS，用 `uv.lock` 锁定版本） |
| 独立环境 | `typing-practice`、`pinpic` | 各自目录内的 `install.sh` 创建自己的 `venv` |

建共享 venv：

```powershell
cd D:\PyTools
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-gui.txt
```

之后运行任何 GUI 工具都用这个解释器，例如：

```powershell
.\.venv\Scripts\python.exe qr\local_qr.pyw
```

**只用标准库的工具**（`ffmpeg/`、`file-dedup/`、`prefix-viewer/`、`hash/check_hash.py`）连 venv 都不用，直接 `python 脚本路径` 即可。

## 使用说明

1. 克隆本仓库:
   ```bash
   git clone https://github.com/yourusername/PyTools.git
   ```
2. 按上面的「环境与依赖」建好共享 venv。
3. 运行盲打训练（独立环境）:
   ```bash
   cd typing-practice
   ./run.sh
   ```
4. 运行其他脚本:
   ```powershell
   python 工具目录/脚本名.py
   ```

## 工具文档索引

每个工具目录里都有一份简短说明（装什么、怎么跑、输出在哪）：

| 工具 | 说明文档 |
|---|---|
| asr | [asr/README.md](asr/README.md) |
| bookmark | [bookmark/README.md](bookmark/README.md) |
| day-calculator | [day-calculator/README.md](day-calculator/README.md) |
| ffmpeg | [ffmpeg/README.md](ffmpeg/README.md) |
| file-dedup | [file-dedup/README.md](file-dedup/README.md) |
| hash | [hash/README.md](hash/README.md) |
| hex-to-string | [hex-to-string/README.md](hex-to-string/README.md) |
| image-sorter | [image-sorter/README.md](image-sorter/README.md) |
| pdf | [pdf/README.md](pdf/README.md) |
| pinpic | [pinpic/README.md](pinpic/README.md) |
| prefix-adder | [prefix-adder/README.md](prefix-adder/README.md) |
| prefix-viewer | [prefix-viewer/README.md](prefix-viewer/README.md) |
| puter-price | [puter-price/README.md](puter-price/README.md) |
| qr | [qr/README.md](qr/README.md) |
| qt-examples | [qt-examples/README.md](qt-examples/README.md) |
| shot-cp | [shot-cp/README.md](shot-cp/README.md) |
| typing-practice | [typing-practice/README.md](typing-practice/README.md) |

## 贡献指南

欢迎贡献代码！请遵循以下步骤:

1. Fork 本仓库
2. 创建新分支 (`git checkout -b feature/YourFeature`)
3. 提交更改 (`git commit -m 'Add some feature'`)
4. 推送分支 (`git push origin feature/YourFeature`)
5. 创建Pull Request

## 许可证

[MIT](LICENSE)
