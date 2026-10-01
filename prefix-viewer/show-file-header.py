def read_file_header(file_path, num_bytes=64):
    try:
        with open(file_path, 'rb') as f:
            # 读取文件的前num_bytes字节
            header = f.read(num_bytes)
            # 输出前num_bytes字节内容
            print(f"File header (first {num_bytes} bytes):")
            print(header)
            print(f"\nHexadecimal representation:")
            # 以16进制打印
            print(header.hex())
    except Exception as e:
        print(f"Error reading file: {e}")

# 输入文件路径
file_path = input("Enter the file path: ")
# 你可以调整读取的字节数，例如读取前128个字节
read_file_header(file_path, num_bytes=64)



input("Press Enter to exit...")