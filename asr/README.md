# asr

把录音转成带时间戳的文字稿：长音频先按静音切分，再调腾讯云语音识别接口逐段识别。

## 依赖与环境

这是本仓库**依赖最重**的工具，用 **uv** 管理（`pyproject.toml` + `uv.lock`）：

```powershell
cd D:\PyTools\asr
uv sync            # 按 uv.lock 创建环境并安装依赖
```

## 配置密钥

复制模板并填入腾讯云密钥（该文件已被 git 忽略，不会提交）：

```powershell
copy api_keys.json.example api_keys.json
```

需要填 `app_id`、`secret_id`、`secret_key`，用 COS 上传时还要 `cos_bucket`、`cos_region`。

## 运行

```powershell
uv run python main.py 录音.mp3
```

也可以把音频文件直接拖到 `main.py` 上，或双击 `asr.bat`。

常用参数：

| 参数 | 作用 |
|---|---|
| `--speaker 2` | 角色分离，指定人数（面试录音常用 2） |
| `--dialect canton` | 方言：`canton`、`sichuan`、`shanghai`、`nanjing`、`hakka`、`minnan` |
| `--no-timestamps` | 只输出纯文本，不要时间戳 |
| `--merge` / `--separate` | 多个文件合并成一份 / 各出一份（不加会交互询问） |
| `--key 1` | 使用 `api_keys.json` 里第 2 个密钥 |
| `-o 输出.txt` | 指定输出文件 |

## 输出位置

- 转写结果写到**音频文件同目录**的同名 `.txt`。
- 切分出的音频片段放在 `output\<音频名>\`，该目录已被 git 忽略（当前占约 878 MB，可自行清理）。

## 已知限制

- **只能在 WSL 下运行**：`splitter.py` 把 `FFMPEG` / `FFPROBE` 写死为 `/mnt/c/...`，并靠 `wslpath` 转换路径。想在 Windows 原生运行需先改掉这两处。
- 需要 **ffmpeg / ffprobe** 可用，用于静音检测与切分。
- `crash.log` 记录上次启动参数，方便排查拖拽闪退，已被忽略。
