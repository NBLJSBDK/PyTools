# PyTools - Python 工具集

这是一个存放自制Python脚本工具的仓库，包含各种实用的小工具和脚本。

## 目录结构

```
PyTools/
├── 盲打练习/            # 打字练习工具
├── 文件查重/            # 文件查重工具
├── ffmpeg/             # 音视频处理工具
├── Hash/               # 文件哈希计算
├── PDF/                # PDF处理工具集
├── puterPrice/         # 硬件配置计算
└── QT例子/             # PyQt示例程序
```

## 主要功能

### 1. 盲打练习
- 功能：打字练习工具，包含成就系统和音效反馈
- 主程序：`盲打练习.pyw`
- 资源文件：音效文件存放在`misc/`目录下

### 2. 文件查重
- 功能：图片去重工具
- 主程序：`图片去重工具.py`

### 3. FFmpeg工具集
- 功能：音视频处理工具
- 包含：
  - `音频提取.py`
  - `音频压缩.py`
  - `常用指令.txt`

### 4. Hash计算
- 功能：文件哈希值计算
- 主程序：`hash.py`

### 5. PDF工具集
- 功能：PDF文件处理
- 包含：
  - `加密解密.py`
  - `水印.py`
  - `逆时针旋转.py`
  - 字体文件：`仿宋_GB2312.TTF`

### 6. 配置计算器
- 功能：硬件配置价格计算
- 包含：
  - `配置计算器.py`
  - `梦中情机.txt`（配置模板）

### 7. PyQt示例
- 功能：PyQt GUI编程示例
- 包含：
  - `进度.py`
  - `框.pyw`
  - `总演示.pyw`

## 使用说明

1. 克隆本仓库：
   ```bash
   git clone https://github.com/yourusername/PyTools.git
   ```
2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
3. 运行脚本：
   ```bash
   python 工具路径/脚本名称.py
   ```

## 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 本仓库
2. 创建新分支 (`git checkout -b feature/YourFeature`)
3. 提交更改 (`git commit -m 'Add some feature'`)
4. 推送分支 (`git push origin feature/YourFeature`)
5. 创建Pull Request

## 许可证

[MIT](LICENSE)
