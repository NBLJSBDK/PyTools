import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout, QPushButton, QLabel, QLineEdit

# PyQt5 中常用的布局有以下几种：

# 垂直布局（QVBoxLayout）：按照垂直方向排列部件。
# 水平布局（QHBoxLayout）：按照水平方向排列部件。
# 网格布局（QGridLayout）：按照网格形式排列部件。
# 表单布局（QFormLayout）：用于创建简单的表单，每行包含一个标签和一个输入部件。
# 常用的部件包括但不限于：

# QPushButton：按钮部件，用于触发操作或事件。
# QLabel：标签部件，用于显示文本或图像。
# QLineEdit：单行文本输入框，用于接收用户输入。
# QTextEdit：多行文本输入框，用于接收多行文本输入。
# QComboBox：下拉框部件，提供一组选项供用户选择。
# QCheckBox：复选框部件，用于表示二选一的选项。
# QRadioButton：单选按钮部件，用于表示互斥的选项。
# QProgressBar：进度条部件，用于显示任务进度。
# QSlider：滑动条部件，用于调整数值。
# QSpinBox：微调框部件，用于输入整数值。
# QDateTimeEdit：日期时间编辑框，用于输入日期和时间。
# QCalendarWidget：日历部件，用于选择日期。
# QListWidget：列表部件，用于显示列表数据。
# QTableWidget：表格部件，用于显示表格数据。
# QTreeWidget：树形部件，用于显示树形结构数据。
# 这些部件可以根据实际需要进行组合和布局，创建出丰富多样的用户界面。

class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # 竖直布局
        vbox = QVBoxLayout()
        vbox.addWidget(QPushButton('Button 1'))
        vbox.addWidget(QPushButton('Button 2'))

        # 水平布局
        hbox = QHBoxLayout()
        hbox.addWidget(QPushButton('Button 3'))
        hbox.addWidget(QPushButton('Button 4'))

        # 网格布局
        grid = QGridLayout()
        grid.addWidget(QPushButton('Button 5'), 0, 0)
        grid.addWidget(QPushButton('Button 6'), 0, 1)
        grid.addWidget(QPushButton('Button 7'), 1, 0)
        grid.addWidget(QPushButton('Button 8'), 1, 1)

        # 表单布局
        form = QFormLayout()
        form.addRow('Label 1:', QLineEdit())
        form.addRow('Label 2:', QLineEdit())

        # 水平布局包含 hbox 和 form
        hbox_form = QHBoxLayout()
        hbox_form.addLayout(hbox)
        hbox_form.addLayout(form)

        # 将布局添加到主布局中
        main_layout = QVBoxLayout()
        main_layout.addLayout(vbox)
        main_layout.addLayout(hbox_form)
        main_layout.addLayout(grid)

        self.setLayout(main_layout)
        self.setWindowTitle('PyQt Layout Example')
        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
