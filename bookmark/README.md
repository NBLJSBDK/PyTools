# bookmark

用 BeautifulSoup 解析浏览器导出的书签 HTML，找出里面重复的网址。

## 运行

需要 `beautifulsoup4`。共享环境（仓库根目录 `.venv`）：

```powershell
cd D:\PyTools\bookmark
D:\PyTools\.venv\Scripts\python.exe check_duplicates.py <书签文件.html>
```

> NOTE: 环境不是固定的。除共享 venv 外，也可以选**不用环境**（全局装 PyQt5）、**目录内独立 venv**（`python -m venv venv`），或依赖重时改用 **uv**。选择标准见仓库根 [AGENTS.md](../AGENTS.md) 第五节。本工具的依赖清单在根 [requirements-gui.txt](../requirements-gui.txt)。

## 说明

- 参数是**浏览器导出的书签 HTML**（Chrome / Edge 的"导出书签"结果），不是浏览器自己的数据库。
- 输出重复网址，以及它们在书签层级里的位置。
- 没给参数时脚本会打印用法提示。
