import subprocess
import os

def convert_flv_to_mp4(video_file):
    output_file = os.path.splitext(video_file)[0] + ".mp4"
    command = [
        "ffmpeg", "-i", video_file,
        "-c:v", "copy", "-c:a", "copy",
        output_file
    ]
    try:
        subprocess.run(command, check=True)
        print(f"✔ 已完成转换: {output_file}")
    except subprocess.CalledProcessError:
        print(f"✘ 转换失败: {video_file}")

def process_input(path):
    if os.path.isfile(path):
        if path.lower().endswith(".flv"):
            convert_flv_to_mp4(path)
        else:
            print(f"跳过非 FLV 文件: {path}")
    elif os.path.isdir(path):
        print(f"扫描目录: {path}")
        for root, _, files in os.walk(path):
            for f in files:
                if f.lower().endswith(".flv"):
                    full_path = os.path.join(root, f)
                    convert_flv_to_mp4(full_path)
    else:
        print(f"无效路径: {path}")

def main():
    print("拖入 FLV 文件或目录到命令行来批量转换为 MP4，按 Ctrl+C 可以退出。")
    try:
        while True:
            user_input = input("请输入/拖入文件或目录路径: ").strip('"').strip()
            if user_input:
                process_input(user_input)
    except KeyboardInterrupt:
        print("\n已退出。")

if __name__ == "__main__":
    main()
