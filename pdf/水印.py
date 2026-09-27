from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
import os

# 注册中文字体
font_path = "仿宋_GB2312.TTF"  # 替换为你的中文字体路径，例如"SimSun.ttf" 或"NotoSansSC-Regular.otf"
pdfmetrics.registerFont(TTFont("ChineseFont", font_path))


def create_watermark(
    text,
    font="ChineseFont",
    font_size=12,
    color=(0.5, 0.5, 0.5, 0.5),
    angle=45,
    spacing=80,
):
    """
    创建水印PDF，支持中文字体
    """
    packet = BytesIO()
    c = canvas.Canvas(packet, pagesize=letter)
    c.setFont(font, font_size)
    c.setFillColor(Color(*color))

    width, height = letter
    for x in range(0, int(width), spacing):
        for y in range(0, int(height), spacing):
            c.saveState()
            c.translate(x, y)
            c.rotate(angle)
            c.drawString(0, 0, text)
            c.restoreState()

    c.save()
    packet.seek(0)
    return packet


def add_watermark_to_pdf(input_pdf_path, output_pdf_path, watermark_params):
    watermark_text = watermark_params.get("text", "Sample Watermark")
    font = watermark_params.get("font", "ChineseFont")
    font_size = watermark_params.get("font_size", 12)
    color = watermark_params.get("color", (0.5, 0.5, 0.5, 0.5))
    angle = watermark_params.get("angle", 45)
    spacing = watermark_params.get("spacing", 80)

    watermark_pdf = create_watermark(
        watermark_text, font, font_size, color, angle, spacing
    )

    reader = PdfReader(input_pdf_path)
    writer = PdfWriter()

    watermark_reader = PdfReader(watermark_pdf)
    watermark_page = watermark_reader.pages[0]

    for page in reader.pages:
        page.merge_page(watermark_page)
        writer.add_page(page)

    with open(output_pdf_path, "wb") as output_pdf:
        writer.write(output_pdf)


def process_pdfs_in_directory(directory):
    input_directory = os.path.join(directory, "input")  # 指定从 "input" 文件夹读取文件
    output_directory = os.path.join(directory, "output")  # 输出到 "output" 文件夹

    # 如果 "input" 或 "output" 文件夹不存在，创建它们
    os.makedirs(input_directory, exist_ok=True)
    os.makedirs(output_directory, exist_ok=True)

    # 遍历 "input" 文件夹中的所有 PDF 文件
    for file_name in os.listdir(input_directory):
        if file_name.lower().endswith(".pdf"):
            # 构造输入文件路径和输出文件路径（保持文件名不变）
            input_pdf_path = os.path.join(input_directory, file_name)
            output_pdf_path = os.path.join(
                output_directory, file_name
            )  # 输出文件与源文件同名

            # 设置水印参数
            watermark_params = {
                "text": os.path.splitext(file_name)[0],  # 使用去掉后缀的文件名作为水印
                "font": "ChineseFont",  # 中文字体
                "font_size": 5,
                "color": (0.5, 0.5, 0.5, 0.5),
                "angle": 45,
                "spacing": 200,
            }

            print(f"Processing: {file_name} -> {output_pdf_path}")
            add_watermark_to_pdf(input_pdf_path, output_pdf_path, watermark_params)


current_directory = os.getcwd()
process_pdfs_in_directory(current_directory)
