import subprocess
import os

def convert_to_mp3(video_file):
    # 构造输出MP3文件名
    output_file = os.path.splitext(video_file)[0] + ".mp3"
    # 使用FFmpeg进行转换
    subprocess.call(["ffmpeg", "-i", video_file, "-vn", "-acodec", "libmp3lame", "-q:a", "0", output_file])
    print(f"已完成转换: {output_file}")

def main():
    print("拖入视频文件到命令行来开始处理，按下 Ctrl+C 可以退出。")
    try:
        while True:
            # 获取用户拖入的文件
            video_file = input().strip('"')
            if os.path.isfile(video_file):
                convert_to_mp3(video_file)
            else:
                print(f"文件不存在: {video_file}")
    except KeyboardInterrupt:
        print("\n已退出。")

if __name__ == "__main__":
    main()
