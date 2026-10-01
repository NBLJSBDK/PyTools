import sys
import os
from PyPDF2 import PdfReader, PdfWriter

# 1. 获取输入 PDF
if len(sys.argv) > 1:
    input_pdf = sys.argv[1]
else:
    input_pdf = "input.pdf"

if not os.path.isfile(input_pdf):
    raise FileNotFoundError(f"找不到文件: {input_pdf}")

# 2. 读取 PDF
reader = PdfReader(input_pdf)
total_pages = len(reader.pages)

print(f"PDF 总页数: {total_pages}")

# 3. 输入起止页码（1-based）
try:
    start_page = int(input("请输入起始页码: "))
    end_page = int(input("请输入结束页码: "))
except ValueError:
    raise ValueError("页码必须是整数")

# 4. 合法性校验
if start_page < 1 or end_page < 1:
    raise ValueError("页码必须 >= 1")

if start_page > end_page:
    raise ValueError("起始页不能大于结束页")

if end_page > total_pages:
    raise ValueError("结束页超出 PDF 总页数")

# 5. 输出文件名
base, _ = os.path.splitext(input_pdf)
output_pdf = f"{base}_{start_page}-{end_page}.pdf"

# 6. 提取页面
writer = PdfWriter()
for i in range(start_page - 1, end_page):
    writer.add_page(reader.pages[i])

with open(output_pdf, "wb") as f:
    writer.write(f)

print(f"处理完成: {output_pdf}")
