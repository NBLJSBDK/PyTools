import os
import shutil
import hashlib
import json
from datetime import datetime
from pathlib import Path
from tqdm import tqdm  # 用于显示进度条

CONFIG_FILE = "photo_organizer_config.json"
LOG_DIR = "log"

# 初始化日志文件
def init_logger():
    os.makedirs(LOG_DIR, exist_ok=True)
    log_file = os.path.join(LOG_DIR, f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    return log_file

# 写日志
def log_message(log_file, level, message):
    with open(log_file, "a", encoding="utf-8") as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        f.write(f"{timestamp}|{level}|照片整理|{message}\n")

# 加载配置
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# 保存配置
def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=4)

# 获取文件的日期信息
def get_file_date(file_path, fallback_method):
    try:
        import exifread
        with open(file_path, 'rb') as f:
            tags = exifread.process_file(f, stop_tag="EXIF DateTimeOriginal", details=False)
            date_taken = tags.get("EXIF DateTimeOriginal")
            if date_taken:
                return datetime.strptime(str(date_taken), "%Y:%m:%d %H:%M:%S")
    except Exception:
        pass

    # 根据备选方法获取时间
    stat = os.stat(file_path)
    if fallback_method == 2:
        return datetime.fromtimestamp(stat.st_mtime)
    elif fallback_method == 3:
        return datetime.fromtimestamp(stat.st_ctime)
    return None

# 生成目标路径
def generate_target_path(base_dir, date, structure):
    if structure == 1:
        return os.path.join(base_dir, f"{date.year}", f"{date.month:02}")
    elif structure == 2:
        return os.path.join(base_dir, f"{date.year}", f"{date.month}")
    elif structure == 3:
        return os.path.join(base_dir, f"{date.year}", f"{date.year}{date.month:02}")
    elif structure == 4:
        return os.path.join(base_dir, f"{date.year}{date.month:02}")
    elif structure == 5:
        return os.path.join(base_dir, f"{date.year}", f"{date.month:02}", f"{date.day:02}")
    elif structure == 6:
        return os.path.join(base_dir, f"{date.year}", f"{date.month:02}{date.day:02}")
    elif structure == 7:
        return os.path.join(base_dir, f"{date.year}{date.month:02}{date.day:02}")
    elif structure == 8:
        return os.path.join(base_dir, f"{date.year}")
    else:
        raise ValueError("Invalid directory structure.")

# 比较文件内容是否相同
def files_are_identical(file1, file2):
    hash1 = hashlib.md5()
    hash2 = hashlib.md5()

    with open(file1, "rb") as f1, open(file2, "rb") as f2:
        while chunk := f1.read(8192):
            hash1.update(chunk)
        while chunk := f2.read(8192):
            hash2.update(chunk)

    return hash1.digest() == hash2.digest()

# 主处理逻辑
def process_photos(config):
    log_file = init_logger()
    source_dir = config["source_dir"]
    include_subdirs = config["include_subdirs"]
    target_dir = config["target_dir"]
    dir_structure = config["dir_structure"]
    action = config["action"]
    fallback_method = config["fallback_method"]
    conflict_resolution = config["conflict_resolution"]

    # 遍历源文件夹
    if include_subdirs:
        files = [os.path.join(root, file) for root, _, filenames in os.walk(source_dir) for file in filenames]
    else:
        files = [os.path.join(source_dir, file) for file in os.listdir(source_dir) if os.path.isfile(os.path.join(source_dir, file))]

    log_message(log_file, "INFO", f"总文件数：{len(files)}")
    processed_count = 0

    for file in tqdm(files, desc="Processing files"):
        date = get_file_date(file, fallback_method)
        if not date:
            log_message(log_file, "WARNING", f"跳过文件：{file}，无法获取日期信息。")
            continue

        target_path = generate_target_path(target_dir, date, dir_structure)
        os.makedirs(target_path, exist_ok=True)

        target_file = os.path.join(target_path, os.path.basename(file))

        if os.path.exists(target_file):
            if conflict_resolution == 1:  # 智能处理
                if files_are_identical(file, target_file):
                    log_message(log_file, "INFO", f"文件已存在且内容相同，跳过：{file}")
                    continue
                base, ext = os.path.splitext(target_file)
                counter = 1
                while os.path.exists(new_name := f"{base} ({counter}){ext}"):
                    counter += 1
                target_file = new_name
            elif conflict_resolution == 2:  # 跳过
                log_message(log_file, "INFO", f"文件已存在，跳过：{file}")
                continue

        if action == 1:  # 复制
            shutil.copy2(file, target_file)
            log_message(log_file, "INFO", f"复制 {file} 到 {target_file}")
        elif action == 2:  # 移动
            shutil.move(file, target_file)
            log_message(log_file, "INFO", f"移动 {file} 到 {target_file}")

        processed_count += 1

    log_message(log_file, "INFO", f"处理完成，共处理了 {processed_count}/{len(files)} 个文件。")
    print(f"\n处理完成，共处理了 {processed_count}/{len(files)} 个文件。")

# 主程序入口
def main():
    while True:
        config = load_config()

        print("-------------------------")
        source_dir = input(f"源文件夹({config.get('source_dir', '')}): ") or config.get("source_dir")
        include_subdirs = input(f"是否包括子文件夹(1是 2否)({config.get('include_subdirs', 1)}): ") or config.get("include_subdirs", 1)
        include_subdirs = int(include_subdirs) == 1
        print("-------------------------")
        target_dir = input(f"目标文件夹({config.get('target_dir', '')}): ") or config.get("target_dir")
        print("-------------------------")

        if not os.path.exists(CONFIG_FILE):
            print("配置文件不存在，将进入配置步骤。")
            use_last_config = False
        else:
            user_input = input("输入回车使用配置开始处理  输入任意字符进入配置步骤: ")
            use_last_config = user_input == ""

        if not use_last_config:
            print("\n选择整理后的目录结构（以2020年3月1日为例）：")
            print("1. \\\\2020\\03\\")
            print("2. \\\\2020\\3\\")
            print("3. \\\\2020\\202003\\")
            print("4. \\\\202003\\")
            print("5. \\\\2020\\03\\01\\")
            print("6. \\\\2020\\0301\\")
            print("7. \\\\20200301\\")
            print("8. \\\\2020\\")
            dir_structure = int(input(f"选择目录结构({config.get('dir_structure', 1)}): ") or config.get("dir_structure", 1))

            print("-------------------------")
            print("整理文件的方法")
            print("1. 复制")
            print("2. 移动")
            action = int(input(f"选择整理方法({config.get('action', 1)}): ") or config.get("action", 1))

            print("-------------------------")
            print("如果文件没有拍摄时间")
            print("1. 跳过")
            print("2. 根据修改时间整理")
            print("3. 根据创建时间整理")
            fallback_method = int(input(f"选择处理方法({config.get('fallback_method', 1)}): ") or config.get("fallback_method", 1))

            print("-------------------------")
            print("目标文件夹存在同名文件时")
            print("1. 智能处理(推荐)")
            print("2. 跳过")
            conflict_resolution = int(input(f"选择冲突处理方法({config.get('conflict_resolution', 1)}): ") or config.get("conflict_resolution", 1))

            config = {
                "source_dir": source_dir,
                "include_subdirs": include_subdirs,
                "target_dir": target_dir,
                "dir_structure": dir_structure,
                "action": action,
                "fallback_method": fallback_method,
                "conflict_resolution": conflict_resolution,
            }
            save_config(config)

        process_photos(config)
        print("-------------------------")
        if input("是否继续整理其他文件？(回车继续，输入任意字符退出): "):
            break

if __name__ == "__main__":
    main()
