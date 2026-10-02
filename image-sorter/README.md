# image-sorter

按哈希和规则整理图片：可递归扫描、按目录结构或时间归档、自动去重、处理重名冲突，并记录日志。

## 运行

需要 `tqdm`。共享环境（仓库根目录 `.venv`）：

```powershell
cd D:\PyTools\image-sorter
D:\PyTools\.venv\Scripts\python.exe sort-photos.py
```

> NOTE: 环境不是固定的。除共享 venv 外，也可以选**不用环境**（全局装 PyQt5）、**目录内独立 venv**（`python -m venv venv`），或依赖重时改用 **uv**。选择标准见仓库根 [AGENTS.md](../AGENTS.md) 第五节。本工具的依赖清单在根 [requirements-gui.txt](../requirements-gui.txt)。

## 说明

- 首次运行会**交互式问几项配置**（源文件夹、是否含子目录、目标文件夹、目录结构、整理方法、冲突处理方式），答案保存在同目录的 `photo_organizer_config.json`。
- 之后再运行，直接回车即沿用上次配置；输入任意字符可重新配置。
- 每次运行都会在 `log\` 下生成一个带时间戳的日志文件，记录动了哪些文件。
- 配置里的"整理方法"决定按什么规则归档，改配置或重跑都能调整。
