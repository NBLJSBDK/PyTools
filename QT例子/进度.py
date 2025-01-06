from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QProgressBar, QLabel

class MyWidget(QWidget):
    def __init__(self):
        super().__init__()

        # 创建水平布局
        self.layout = QHBoxLayout()

        # 创建 QLabel 来显示文本 "进度："
        self.label_progress = QLabel("进度:")

        # 创建进度条
        self.progress_bar_current = QProgressBar()
        self.progress_bar_current.setTextVisible(True)

        
        self.layout.addWidget(self.label_progress)
        self.layout.addWidget(self.progress_bar_current)

        
        # 设置水平布局到窗口
        self.setLayout(self.layout)

if __name__ == '__main__':
    app = QApplication([])
    widget = MyWidget()
    widget.show()
    app.exec_()
