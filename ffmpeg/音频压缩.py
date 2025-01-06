import os
import subprocess

def compress_mp3(input_folder, output_folder):
    # 确保输出文件夹存在
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # 遍历输入文件夹中的所有文件
    for filename in os.listdir(input_folder):
        if filename.endswith('.mp3'):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename)
            
            # 构建ffmpeg命令
            command = [
                'ffmpeg',
                '-i', input_path,
                '-codec:a', 'libmp3lame',
                '-qscale:a', '0',
                output_path
            ]
            
            # 执行ffmpeg命令
            subprocess.run(command)
            print(f"Compressed {filename}")

input_folder = 'C:/Users/nbljsbdk/Desktop/破碎资源文件/assets/sounds'  # 替换为你的输入文件夹路径
output_folder = 'C:/Users/nbljsbdk/Desktop/破碎资源文件/assets/sounds/123'  # 替换为你的输出文件夹路径

compress_mp3(input_folder, output_folder)
