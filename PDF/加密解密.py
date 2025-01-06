import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QLineEdit, QLabel, QMessageBox
from PyQt5.QtCore import Qt
from PyPDF2 import PdfReader, PdfWriter

class PDFDecryptor(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('PDF 加密解密器')
        self.setGeometry(300, 300, 400, 200)

        layout = QVBoxLayout()

        self.label = QLabel('拖入 PDF 文件：')
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("border: 1px dashed gray;")
        self.label.setAcceptDrops(True)
        self.setAcceptDrops(True)
        layout.addWidget(self.label)

        self.file_button = QPushButton('选择 PDF 文件')
        self.file_button.clicked.connect(self.select_pdf)
        layout.addWidget(self.file_button)

        self.password_label = QLabel('输入密码：')
        layout.addWidget(self.password_label)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        button_layout = QHBoxLayout()

        self.encrypt_button = QPushButton('开始加密')
        self.encrypt_button.clicked.connect(self.encrypt_pdf)
        button_layout.addWidget(self.encrypt_button)

        self.decrypt_button = QPushButton('开始解密')
        self.decrypt_button.clicked.connect(self.decrypt_pdf)
        button_layout.addWidget(self.decrypt_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if file_path.endswith('.pdf'):
                self.label.setText(f'文件：{file_path}')
                self.file_path = file_path
            else:
                QMessageBox.warning(self, '错误', '请拖入 PDF 文件！')

    def select_pdf(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, '选择 PDF 文件', '', 'PDF Files (*.pdf)', options=options)
        if file_path:
            self.label.setText(f'文件：{file_path}')
            self.file_path = file_path

    def decrypt_pdf(self):
        if not hasattr(self, 'file_path') or not self.file_path:
            QMessageBox.warning(self, '错误', '请先选择文件！')
            return

        password = self.password_input.text()
        if not password:
            QMessageBox.warning(self, '错误', '请输入密码！')
            return

        output_path = self.file_path.replace('.pdf', '_jiemi.pdf')

        try:
            reader = PdfReader(self.file_path)
            if reader.is_encrypted:
                if not reader.decrypt(password):
                    QMessageBox.critical(self, '错误', '密码错误！')
                    return

                writer = PdfWriter()
                for page in reader.pages:
                    writer.add_page(page)

                with open(output_path, 'wb') as f:
                    writer.write(f)

                QMessageBox.information(self, '成功', f'解密完成！文件保存为：{output_path}')
            else:
                QMessageBox.information(self, '提示', '文件未加密，无需解密！')
        except Exception as e:
            QMessageBox.critical(self, '错误', f'解密失败：{e}')

    def encrypt_pdf(self):
        if not hasattr(self, 'file_path') or not self.file_path:
            QMessageBox.warning(self, '错误', '请先选择文件！')
            return

        password = self.password_input.text()
        if not password:
            QMessageBox.warning(self, '错误', '请输入密码！')
            return

        output_path = self.file_path.replace('.pdf', '_jiami.pdf')

        try:
            reader = PdfReader(self.file_path)
            writer = PdfWriter()

            for page in reader.pages:
                writer.add_page(page)

            writer.encrypt(password)

            with open(output_path, 'wb') as f:
                writer.write(f)

            QMessageBox.information(self, '成功', f'加密完成！文件保存为：{output_path}')
        except Exception as e:
            QMessageBox.critical(self, '错误', f'加密失败：{e}')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    decryptor = PDFDecryptor()
    decryptor.show()
    sys.exit(app.exec_())
