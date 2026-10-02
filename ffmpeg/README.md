# ffmpeg

调用 ffmpeg 做音视频处理，以及一个彩色的目录树打印小工具。

## 运行

本目录脚本**只用标准库**，不需要虚拟环境：

```powershell
cd D:\PyTools\ffmpeg
python extract-audio.py
python compress-audio.py
python flv-to-mp4.py
python mkv-to-mp4.py
python base.py
```

## 环境

只用标准库，**不需要任何环境**，直接运行即可。若你习惯统一用虚拟环境，也可以用仓库根目录的 `.venv`：

```powershell
D:\PyTools\.venv\Scripts\python.exe 脚本名.py
```

## 说明

- 需要 **ffmpeg / ffprobe 在 PATH 里**（`mkv-to-mp4.py` 还要用 `ffprobe` 读流信息）。
- 输出文件默认写在**输入文件同目录**。
- `compress-audio.py` 里的路径是写死的示例，用之前必须改。

## 各脚本

| 脚本 | 做什么 | 怎么用 |
|---|---|---|
| `extract-audio.py` | 从视频里提取音频，输出同名 `.mp3` | 运行后把视频文件拖进终端，循环处理，`Ctrl+C` 退出 |
| `compress-audio.py` | 批量重新编码文件夹里的 `.mp3` | **需要先改脚本里的 `input_folder` / `output_folder`**，再运行 |
| `flv-to-mp4.py` | FLV 转 MP4（直接复制流，不重新编码，很快） | 运行后输入或拖入文件/目录路径，目录会递归扫描 |
| `mkv-to-mp4.py` | MKV 转 MP4，并处理字幕流 | 运行后输入或拖入路径，会先列出待转换文件让你确认 |
| `base.py` | 彩色打印目录树 | 可把文件夹拖到脚本上，或运行后输入路径 |
