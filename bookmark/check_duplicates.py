import sys
from collections import defaultdict
from bs4 import BeautifulSoup

def extract_urls_and_positions(file_path):
    """
    从 HTML 书签文件中提取网址及其在书签层级中的位置，以及所在行数。
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    urls_and_positions = []
    
    # 查找所有包含书签链接的 <A> 标签
    all_links = soup.find_all('a', href=True)

    for link in all_links:
        url = link.get('href')
        if not url:
            continue

        # 获取当前 <A> 标签所在的行号
        # line_number = link.sourceline
        
        # 找到包含该 <a> 标签的最内层 <DL> 标签（也就是所在文件夹）
        current_node = link
        folder_dl = None
        while current_node:
            if current_node.name == 'dl':
                folder_dl = current_node
                break
            current_node = current_node.parent

        # 在该文件夹 <DL> 中统计当前书签是第几个 <a> 标签
        line_number = 1
        if folder_dl:
            count = 0
            for tag in folder_dl.find_all('a', href=True, recursive=True):
                # 只统计直接子级的 a，不统计嵌套的 DL 中的 a
                if tag.find_parent('dl') == folder_dl:
                    count += 1
                    if tag == link:
                        line_number = count
                        break





        # 构建当前书签的路径
        path_segments = []
        current_node = link.parent # 从 <A> 标签的父级开始向上回溯

        while current_node:
            if current_node.name == 'dl' and current_node.parent and current_node.parent.name == 'dt':
                # 如果是 <DL><p><DT><H3>...</H3> 结构，则 H3 是文件夹名称
                h3_tag = current_node.parent.find('h3')
                if h3_tag and h3_tag.string:
                    path_segments.insert(0, h3_tag.string.strip())
            
            # 检查是否有顶级的 H1 标签作为根目录的名称
            if current_node.name == 'html': # 达到文档根目录
                h1_tag = current_node.find('h1')
                if h1_tag and h1_tag.string and h1_tag.string.strip() == "Bookmarks": # 假设顶级标题是 "Bookmarks"
                    # 避免将 "Bookmarks" 加入路径，如果它是默认的根目录名
                    pass
            
            current_node = current_node.parent

        # 格式化路径，如果路径为空，表示在根目录
        position = "根目录"
        if path_segments:
            position = " - ".join(path_segments)

        # 添加行数信息
        urls_and_positions.append((url, position, line_number))
            
    return urls_and_positions

def find_duplicates(urls_and_positions):
    """
    查找重复的网址，并记录它们的出现次数和所有位置。
    """
    # 使用 defaultdict 存储每个 URL 的所有位置
    url_info = defaultdict(lambda: {"count": 0, "positions": []})

    for url, position, line_number in urls_and_positions:
        url_info[url]["count"] += 1
        url_info[url]["positions"].append((position, line_number))
    
    # 筛选出重复的网址
    duplicates = {url: info for url, info in url_info.items() if info["count"] > 1}
    
    return duplicates

def main():
    if len(sys.argv) != 2:
        print("用法: python check_duplicates.py <bookmarks.html>")
        sys.exit(1)

    file_path = sys.argv[1]
    try:
        urls_and_positions = extract_urls_and_positions(file_path)
        duplicates = find_duplicates(urls_and_positions)

        if not duplicates:
            print("没有发现重复的网址。")
        else:
            duplicate_count = len(duplicates)
            print(f"发现 {duplicate_count} 个重复网址：\n")
            for url, info in duplicates.items():
                print(f"{url} —— 出现次数: {info['count']}")
                for i, (position, line_number) in enumerate(info['positions']):
                    print(f"    位置 {i + 1}: {position} 行数: {line_number}")

    except FileNotFoundError:
        print(f"错误：文件 '{file_path}' 未找到。请确保文件路径正确。")
    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    main()
 