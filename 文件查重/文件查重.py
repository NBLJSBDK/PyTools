import os
import hashlib
import shutil


def calculate_file_hash(file_path, chunk_size=8192):
    """计算文件的哈希值"""
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        while chunk := f.read(chunk_size):
            hasher.update(chunk)
    return hasher.hexdigest()


def group_files_by_size(root_dir):
    """按文件大小分组"""
    size_map = {}
    for root, _, files in os.walk(root_dir):
        for file in files:
            file_path = os.path.join(root, file)
            file_size = os.path.getsize(file_path)
            if file_size not in size_map:
                size_map[file_size] = []
            size_map[file_size].append(file_path)
    return size_map


def process_duplicates(size_map, duplicates_dir):
    """处理重复文件"""
    if not os.path.exists(duplicates_dir):
        os.makedirs(duplicates_dir)
    
    duplicate_groups = []
    # 统计总的需要计算哈希的文件数量
    total_files = sum(len(files) for files in size_map.values() if len(files) > 1)
    processed_files = 0  # 已处理文件计数

    # 生成重复文件树状结构文本并提示用户确认
    for size,files in size_map.items():
        if len(files) < 2:
            continue  # 跳过只有一个文件的分组
        
        # 计算哈希值并分组
        hash_map = {}
        for file in files:
            file_hash = calculate_file_hash(file)
            if file_hash not in hash_map:
                hash_map[file_hash] = []
            hash_map[file_hash].append(file)

            # 更新处理进度
            processed_files += 1
            print(f"Hash已经处理({processed_files}/{total_files})")
        
        # 生成重复文件树状结构文本
        for file_list in hash_map.values():
            if len(file_list) < 2:
                continue

            # 按创建时间排序，保留最早创建的文件
            file_list.sort(key=lambda x: os.path.getctime(x))
            duplicate_groups.append(file_list)
            
    # 生成 duplicates_tree.txt 文件
    tree_file = generate_duplicates_tree(duplicates_dir, duplicate_groups)
    
    # 打印并提示用户确认
    print(f"组列表已生成，请确认后输入 Y 移动，N 取消操作。\n查看文件：{tree_file}")
    user_input = input("请输入 Y 或 N: ").strip().lower()

    # 根据用户输入决定是否移动文件
    if user_input == 'y':
        for group in duplicate_groups:
            for duplicate in group[1:]:  # 跳过第一个文件（保留最早创建的）
                new_path = os.path.join(duplicates_dir, os.path.basename(duplicate))
                shutil.move(duplicate, new_path)
        print("文件已移动！")
    else:
        print("操作已取消。")
    
    return duplicate_groups


def generate_duplicates_tree(duplicates_dir, duplicate_groups):
    """生成重复文件树状结构文本"""
    tree_file = os.path.join(duplicates_dir, 'duplicates_tree.txt')
    with open(tree_file, 'w', encoding='utf-8') as f:
        for idx, group in enumerate(duplicate_groups, start=1):
            f.write(f"重复组 {idx}:\n")
            for file in group:
                f.write(f"  {file}\n")
            f.write("\n")

    return tree_file


def process_directories(directories):
    """处理多个文件夹"""
    for root_dir in directories:
        root_dir = root_dir.strip('"')  # 去掉可能的引号
        if not os.path.isdir(root_dir):
            print(f"错误：路径无效或不是文件夹：{root_dir}")
            continue
        
        duplicates_dir = os.path.join(root_dir, '待处理重复文件')
        print(f"开始处理文件夹：{root_dir}")
        
        # 执行查重逻辑
        size_map = group_files_by_size(root_dir)
        process_duplicates(size_map, duplicates_dir)
        
        print(f"查重完成！重复文件已移动到目录：{duplicates_dir}")
        print(f"详细重复信息已记录在 {os.path.join(duplicates_dir, 'duplicates_tree.txt')}")


def main():
    print("请输入文件夹路径，或将一个或多个路径拖入窗口后回车：")
    while True:
        input_paths = input().strip()
        if not input_paths:
            print("未输入任何路径，程序退出。")
            break
        
        # 分割多个路径（以空格区分）
        directories = input_paths.split()
        process_directories(directories)
        print("\n处理完成！可以继续拖入文件夹路径，或直接按回车退出。")


if __name__ == "__main__":
    main()
