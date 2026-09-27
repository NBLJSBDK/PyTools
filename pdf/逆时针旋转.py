from PyPDF2 import PdfReader, PdfWriter

# 读取原始PDF
input_file = "1.pdf"
output_file = "rotated_1.pdf"

reader = PdfReader(input_file)
writer = PdfWriter()

# 遍历PDF每一页，逆时针旋转90°
for page in reader.pages:
    page.rotate(270)  # 逆时针旋转90°
    writer.add_page(page)

# 保存到新的PDF文件
with open(output_file, "wb") as f:
    writer.write(f)

print(f"文件已保存为 {output_file}")
