# hash

文件哈希校验：GUI 版算哈希，命令行版对比两个文件是否完全一致。

## 运行

需要 PyQt5。共享环境（仓库根目录 `.venv`）：

```powershell
cd D:\PyTools\hash
D:\PyTools\.venv\Scripts\python.exe hash.pyw
```

对比两个文件（**只用标准库**，可不动 venv）：

```powershell
python check_hash.py 文件A 文件B
```

也可以同时选中两个文件，直接拖到 `check_hash.py` 上。

> NOTE: 环境不是固定的。除共享 venv 外，也可以选**不用环境**（全局装 PyQt5）、**目录内独立 venv**（`python -m venv venv`），或依赖重时改用 **uv**。选择标准见仓库根 [AGENTS.md](../AGENTS.md) 第五节。本工具的依赖清单在根 [requirements-gui.txt](../requirements-gui.txt)。

## 说明

- `hash.pyw`：窗口程序，拖入文件算哈希。
- `check_hash.py`：算两个文件的 SHA-256 并直接给出 `MATCH` / `DIFFERENT`，适合核对下载文件有没有损坏。
- 大文件是分块读取的，不会撑爆内存。
