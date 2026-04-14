import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton, QMessageBox

class HexToUtf8Converter(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HEX → UTF-8 Converter (混合串口回显)")
        self.setGeometry(100, 100, 700, 400)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        label = QLabel(
            "左边输入串口回显 HEX（空格或连续），右边显示 UTF-8 + 未解码 HEX")
        layout.addWidget(label)

        h_layout = QHBoxLayout()
        self.hex_input = QTextEdit()
        self.hex_input.setPlaceholderText(
            "例如: 8C E2 9C EC 0D 0A 12 83 6F EC ...")
        self.utf8_output = QTextEdit()
        self.utf8_output.setReadOnly(True)

        h_layout.addWidget(self.hex_input)
        h_layout.addWidget(self.utf8_output)
        layout.addLayout(h_layout)

        btn_convert = QPushButton("转换")
        btn_convert.clicked.connect(self.convert_hex_to_utf8)
        layout.addWidget(btn_convert)

        self.setLayout(layout)

    def convert_hex_to_utf8(self):
        hex_text = self.hex_input.toPlainText().replace(" ", "").replace("\n", "")
        if len(hex_text) % 2 != 0:
            hex_text = hex_text[:-1]  # 去掉最后一个不完整字节

        try:
            b = bytes.fromhex(hex_text)
            output = ""
            i = 0
            while i < len(b):
                # 尝试解码一个 UTF-8 字符
                for length in range(1, 5):  # UTF-8 最多4字节
                    if i + length <= len(b):
                        try:
                            chunk = b[i:i + length].decode('utf-8')
                            output += chunk
                            i += length
                            break
                        except UnicodeDecodeError:
                            if length == 4:
                                # 无法解码，显示 HEX
                                output += f"[{b[i]:02X}]"
                                i += 1
                    else:
                        output += f"[{b[i]:02X}]"
                        i += 1
                        break
            self.utf8_output.setPlainText(output)
        except Exception as e:
            QMessageBox.warning(self, "错误", f"无法处理 HEX:\n{e}")
            self.utf8_output.setPlainText("")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HexToUtf8Converter()
    window.show()
    sys.exit(app.exec_())
