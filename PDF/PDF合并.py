import sys
import os
from PyPDF2 import PdfMerger

def merge_pdfs(pdf_paths, output_path="merged.pdf"):
    merger = PdfMerger()
    for path in pdf_paths:
        print(f"正在添加: {path}")
        merger.append(path)
    merger.write(output_path)
    merger.close()
    print(f"合并完成，输出文件：{output_path}")

def main():
    if len(sys.argv) < 2:
        print("请将 PDF 文件拖入本程序后回车。")
        input("按回车退出...")
        return

    # 获取拖入的文件路径（Windows 下带引号，去掉）
    pdf_files = [arg.strip('"') for arg in sys.argv[1:] if arg.lower().endswith('.pdf')]

    if not pdf_files:
        print("未检测到有效的 PDF 文件。")
        input("按回车退出...")
        return

    merge_pdfs(pdf_files)

if __name__ == "__main__":
    main()
