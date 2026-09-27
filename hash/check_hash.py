import hashlib
import sys
import os

def get_file_hash(file_path):
    """计算文件的 SHA-256 哈希值"""
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            # 分块读取，防止大文件撑爆内存
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    # sys.argv[0] 是脚本路径，随后的才是拖入的文件
    files = sys.argv[1:]

    if len(files) < 2:
        print("提示：请同时选中两个文件并拖入此脚本。")
    else:
        file1, file2 = files[0], files[1]
        
        print(f"正在对比:\n1: {os.path.basename(file1)}\n2: {os.path.basename(file2)}\n")

        hash1 = get_file_hash(file1)
        hash2 = get_file_hash(file2)

        print(f"Hash 1: {hash1}")
        print(f"Hash 2: {hash2}")
        print("-" * 30)

        if hash1 == hash2:
            print("结果：文件内容完全一致！ (MATCH)")
        else:
            print("结果：文件内容不同。 (DIFFERENT)")

    print("\n按回车键退出...")
    input()

if __name__ == "__main__":
    main()