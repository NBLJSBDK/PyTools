import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout, QPushButton, QLabel, QLineEdit


class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # 创建主布局
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # 表单布局，用于放置比较按钮和输入框
        form = QFormLayout()

        # 创建一个用于用户输入要比较的哈希值的QLineEdit
        self.hash_line_edit = QLineEdit()
        form.addRow('对比', self.hash_line_edit)

        # 创建一个用于触发比较的QPushButton
        compare_button = QPushButton("比较")
        # compare_button.clicked.connect(self.compare_hashes)
        form.addRow(compare_button)

        # 将表单布局添加到主布局中
        main_layout.addLayout(form)

        self.setWindowTitle('PyQt Layout Example')
        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
