import sys
import os
import re
import subprocess
import json

class Color:
    BLUE = '\033[1;34m'
    GREEN = '\033[32m'
    RED = '\033[31m'
    YELLOW = '\033[33m'
    CYAN = '\033[36m'
    RESET = '\033[0m'

def get_video_info(file_path):
    """获取视频流信息，判断是否有字幕"""
    cmd = [
        'ffprobe', '-v', 'quiet', '-print_format', 'json',
        '-show_streams', file_path
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        data = json.loads(result.stdout)
        # 查找是否存在字幕流
        has_subtitle = any(s['codec_type'] == 'subtitle' for s in data.get('streams', []))
        return True, has_subtitle
    except Exception:
        return False, False

def convert_mkv_to_mp4(input_file, current_idx, total_count):
    """执行转换逻辑"""
    # 结果输出到原文件所在目录
    output_file = os.path.splitext(input_file)[0] + "_converted.mp4"
    
    print(f"\n{Color.CYAN}[{current_idx}/{total_count}] 正在处理: {os.path.basename(input_file)}{Color.RESET}")
    
    success, has_sub = get_video_info(input_file)
    if not success:
        print(f"{Color.RED}❌ 错误: 无法解析文件信息，跳过此文件。{Color.RESET}")
        return

    # ffmpeg 基础参数
    # -crf 18: 高画质  -c:a aac: 通用音频编码  -y: 覆盖已存在的输出
    cmd = ['ffmpeg', '-i', input_file, '-c:v', 'libx264', '-crf', '18', '-c:a', 'aac', '-y']

    if has_sub:
        print(f"{Color.YELLOW}   状态: 检测到内嵌字幕 -> 正在压制硬字幕(白字黑边)...{Color.RESET}")
        # 处理 FFmpeg 滤镜中的特殊字符转义 (尤其是 Windows 路径)
        safe_path = input_file.replace('\\', '/').replace(':', '\\:')
        subtitle_filter = f"subtitles='{safe_path}':force_style='OutlineColour=&H80000000,BorderStyle=3,Outline=1,Shadow=0,MarginV=20'"
        cmd.extend(['-vf', subtitle_filter])
    else:
        print(f"{Color.GREEN}   状态: 无字幕 -> 直接转码封装...{Color.RESET}")

    cmd.append(output_file)

    try:
        # 运行转换
        subprocess.run(cmd, check=True)
        print(f"{Color.GREEN}   ✅ 转换成功!{Color.RESET}")
        print(f"   📂 保存位置: {output_file}")
    except subprocess.CalledProcessError:
        print(f"{Color.RED}   ❌ 转换失败! 请检查 FFmpeg 是否安装或文件是否损坏。{Color.RESET}")

def parse_paths(line):
    """解析拖入的路径字符串"""
    pattern = r'"([^"]+)"|(\S+)'
    matches = re.findall(pattern, line)
    return [os.path.normpath(m[0] if m[0] else m[1]) for m in matches]

def find_mkv_recursive(path):
    """递归搜索所有 mkv 文件"""
    mkv_files = []
    if os.path.isfile(path) and path.lower().endswith('.mkv'):
        mkv_files.append(path)
    elif os.path.isdir(path):
        for root, _, files in os.walk(path):
            for f in files:
                if f.lower().endswith('.mkv'):
                    mkv_files.append(os.path.join(root, f))
    return mkv_files

def main():
    if os.name == 'nt': os.system('color')
    
    while True:
        print(f"\n{Color.BLUE}{'='*60}{Color.RESET}")
        print(f"{Color.BLUE}➤ 请拖入【文件】或【文件夹】并按回车 (Ctrl+C 退出):{Color.RESET}")
        try:
            line = input("-> ").strip()
        except EOFError: break
        if not line: continue

        # 1. 检测文件
        input_paths = parse_paths(line)
        all_mkv = []
        for p in input_paths:
            all_mkv.extend(find_mkv_recursive(p))

        if not all_mkv:
            print(f"{Color.RED}❌ 未发现任何 MKV 文件，请重新输入。{Color.RESET}")
            continue

        # 2. 依次输出路径名称供用户确认
        print(f"\n{Color.GREEN}🔍 检测到 {len(all_mkv)} 个待转换文件:{Color.RESET}")
        for i, mkv in enumerate(all_mkv, 1):
            print(f"   {i}. {mkv}")
        
        confirm = input(f"\n确认开始转换? (Y/N): ").strip().lower()
        if confirm != 'y':
            print(f"{Color.YELLOW}已取消操作。{Color.RESET}")
            continue

        # 3. 逐个转换
        for idx, mkv in enumerate(all_mkv, 1):
            convert_mkv_to_mp4(mkv, idx, len(all_mkv))

        print(f"\n{Color.GREEN}✨ 所有任务已处理完毕!{Color.RESET}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Color.RED}程序已手动退出。{Color.RESET}")