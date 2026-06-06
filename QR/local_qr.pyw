import sys
from io import BytesIO
import qrcode
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QTextEdit, QLabel
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt

class QRCodeGeneratorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # 设置窗口标题和初始大小
        self.setWindowTitle('本地二维码生成器 (离线安全版)')
        self.resize(600, 350)

        # 创建水平布局 (左边输入，右边显示)
        main_layout = QHBoxLayout()

        # 左侧：文本输入框
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("在此处输入需要转换的文本...\n二维码会实时生成。")
        self.text_input.setStyleSheet("font-size: 14px; padding: 10px;")
        
        # 绑定信号：当文本内容发生改变时，触发生成二维码的槽函数
        self.text_input.textChanged.connect(self.update_qr_code)

        # 右侧：用于显示二维码的标签
        self.qr_label = QLabel()
        self.qr_label.setAlignment(Qt.AlignCenter) # 居中对齐
        self.qr_label.setMinimumSize(300, 300)     # 设置最小尺寸以防挤压
        self.qr_label.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc;")

        # 将组件添加到布局中
        main_layout.addWidget(self.text_input, stretch=1)
        main_layout.addWidget(self.qr_label, stretch=1)

        self.setLayout(main_layout)

    def update_qr_code(self):
        # 获取输入框的纯文本内容
        text = self.text_input.toPlainText()

        # 如果输入为空，清空右侧显示
        if not text:
            self.qr_label.clear()
            self.qr_label.setText("等待输入...")
            return

        # 配置并生成二维码
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L, # L级别容错率约7%
            box_size=10,
            border=2,
        )
        qr.add_data(text)
        qr.make(fit=True)

        # 生成 PIL 图像
        img = qr.make_image(fill_color="black", back_color="white")

        # 将 PIL 图像转换为字节流，再转换为 PyQt 可识别的 QPixmap
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        qimage = QImage.fromData(buffer.getvalue())
        pixmap = QPixmap.fromImage(qimage)

        # 缩放图像以适应 Label 大小，并保持宽高比，开启平滑缩放
        scaled_pixmap = pixmap.scaled(
            self.qr_label.size(), 
            Qt.KeepAspectRatio, 
            Qt.SmoothTransformation
        )
        
        # 将生成的图像设置到 Label 上
        self.qr_label.setPixmap(scaled_pixmap)

    # 监听窗口重绘事件（例如拉伸窗口时），让二维码自动适应大小
    def resizeEvent(self, event):
        self.update_qr_code()
        super().resizeEvent(event)

if __name__ == '__main__':
    # 初始化 Qt 应用
    app = QApplication(sys.argv)
    
    # 实例化并显示主窗口
    ex = QRCodeGeneratorApp()
    ex.show()
    
    # 进入应用主循环
    sys.exit(app.exec_())
    