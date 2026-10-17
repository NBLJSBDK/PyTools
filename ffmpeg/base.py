import sys
import os
import re

class Color:
    BLUE = '\033[1;34m'
    GREEN = '\033[32m'
    RED = '\033[31m'
    CYAN = '\033[36m'
    RESET = '\033[0m'

def print_tree(path, indent="", is_last=True):
    # 使用 abspath 和 normpath 彻底解决路径转义和相对路径问题
    path = os.path.normpath(os.path.abspath(path.strip()))
    
    if not os.path.exists(path):
        print(f"{indent}{Color.RED}❌ 路径不存在: {path}{Color.RESET}")
        return

    marker = "└── " if is_last else "├── "
    name = os.path.basename(path)
    if not name: name = path 

    if os.path.isdir(path):
        print(f"{indent}{marker}{Color.BLUE}{name}/{Color.RESET}")
        new_indent = indent + ("    " if is_last else "│   ")
        try:
            items = sorted(os.listdir(path))
            items = [item for item in items if not item.startswith('.')]
            for i, item in enumerate(items):
                print_tree(os.path.join(path, item), new_indent, i == len(items) - 1)
        except PermissionError:
            print(f"{new_indent}{Color.RED}└── [拒绝访问]{Color.RESET}")
    else:
        print(f"{indent}{marker}{Color.GREEN}{name}{Color.RESET}")

def parse_paths(line):
    """
    针对带空格路径的终极解析逻辑
    """
    # 这个正则会优先匹配引号内的内容，如果没有引号，则匹配到下一个空格为止
    # 这样就算文件夹名字叫 "New Folder"，只要带了引号，就能完整识别
    pattern = r'"([^"]+)"|(\S+)'
    matches = re.findall(pattern, line)
    paths = []
    for m in matches:
        path = m[0] if m[0] else m[1]
        paths.append(path)
    return paths

def main():
    if os.name == 'nt':
        os.system('color') 

    # 优先处理直接拖入图标的参数（系统会自动加引号）
    args = sys.argv[1:]

    while True:
        if not args:
            print(f"\n{Color.CYAN}➤ 提示: 文件夹名有空格时，请确保路径带有引号 (Windows 拖入通常自带):{Color.RESET}")
            try:
                line = input("-> ").strip()
            except EOFError: break
            if not line: continue
            args = parse_paths(line)

        print(f"\n{Color.CYAN}--- Tree View ---{Color.RESET}")
        for i, path in enumerate(args):
            print_tree(path, is_last=(i == len(args) - 1))

        args = [] 

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Color.RED}已安全退出。{Color.RESET}")