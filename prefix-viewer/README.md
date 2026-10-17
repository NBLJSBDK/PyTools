# prefix-viewer

读取文件开头若干字节，同时以文本和十六进制打印，用来判断文件真实类型。

## 运行

**只用标准库**，不需要虚拟环境：

```powershell
cd D:\PyTools\prefix-viewer
python show-file-header.py
```

运行后按提示输入文件路径，默认读取前 64 字节。

## 环境

只用标准库，**不需要任何环境**，直接运行即可。若你习惯统一用虚拟环境，也可以用仓库根目录的 `.venv`：

```powershell
D:\PyTools\.venv\Scripts\python.exe 脚本名.py
```

## 说明

- 想改读取长度，编辑脚本最后一行 `read_file_header(file_path, num_bytes=64)`。
- 未识别的文件、只有扩展名的文件，可以用它看真实文件头（例如判断伪装成图片的可执行文件）。
