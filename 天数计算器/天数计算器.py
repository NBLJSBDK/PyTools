import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QDateEdit, QLabel, QDialog
from PyQt5.QtCore import QDate


class DateCalculator(QWidget):
    def __init__(self):
        super().__init__()

        # 初始化窗口
        self.setWindowTitle("日期计算器")
        self.setGeometry(100, 100, 300, 200)

        # 创建布局
        layout = QVBoxLayout()

        # 创建初始日期选择框
        self.start_date_label = QLabel("选择初始日期:")
        self.start_date_edit = QDateEdit(QDate.currentDate())
        self.start_date_edit.setDisplayFormat("yyyy-MM-dd")

        # 创建目标日期选择框
        self.end_date_label = QLabel("选择目标日期:")
        self.end_date_edit = QDateEdit(QDate.currentDate())
        self.end_date_edit.setDisplayFormat("yyyy-MM-dd")

        # 创建按钮
        self.calculate_button = QPushButton("计算时间")
        self.result_label = QLabel("")

        # 连接按钮事件
        self.calculate_button.clicked.connect(self.calculate_days)

        # 布局管理
        form_layout = QVBoxLayout()
        form_layout.addWidget(self.start_date_label)
        form_layout.addWidget(self.start_date_edit)
        form_layout.addWidget(self.end_date_label)
        form_layout.addWidget(self.end_date_edit)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.calculate_button)

        layout.addLayout(form_layout)
        layout.addLayout(button_layout)
        layout.addWidget(self.result_label)

        self.setLayout(layout)

    def calculate_days(self):
        # 获取选择的日期
        start_date = self.start_date_edit.date()
        end_date = self.end_date_edit.date()

        # 检查是否是同一天
        if start_date == end_date:
            self.result_label.setText("初始日期和目标日期是同一天")
        else:
            # 计算两个日期之间的天数差
            days_diff = start_date.daysTo(end_date)
    
            # 计算相差的年数和天数
            years = days_diff // 365  # 计算年数
            remaining_days = days_diff % 365  # 计算剩余的天数
    
            # 输出结果
            self.result_label.setText(f"从初始日期到目标日期相差 {days_diff} 天 ({years}年{remaining_days}天)")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DateCalculator()
    window.show()
    sys.exit(app.exec_())
