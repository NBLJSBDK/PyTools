import sys

from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QTableWidget, \
    QTableWidgetItem, QMessageBox, QDesktopWidget, QHBoxLayout, QFileDialog, QLineEdit


class NumericTableWidgetItem(QTableWidgetItem):
    def __init__(self, value=''):
        super().__init__(value)

    def __lt__(self, other):
        try:
            return float(self.text()) < float(other.text())
        except ValueError:  # 如果转换失败，则按照字符串比较
            return self.text() < other.text()

    def setData(self, role, value):
        if role == Qt.EditRole:
            try:
                value = float(value)
            except ValueError:
                value = 0.0
        super().setData(role, value)

    def editor(self):
        editor = QLineEdit(self.text())
        editor.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        return editor


class MachinePriceCalculator(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("机器价格计算器")

        # 获取屏幕尺寸信息
        screen = QDesktopWidget().screenGeometry()
        window_size = 820, 750
        window_position = int((screen.width() - window_size[0]) / 2), int((screen.height() - window_size[1]) / 2)

        self.setGeometry(window_position[0], window_position[1], *window_size)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.total_price_label = QLabel("总价格：0")
        self.total_price_label.setStyleSheet("font-size: 40px;")
        self.layout.addWidget(self.total_price_label)

        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(6)  # 总共六列
        self.table_widget.setHorizontalHeaderLabels(["硬件类型", "具体型号", "价格", "数量", "价格", "操作"])  # 表头
        self.layout.addWidget(self.table_widget)

        button_layout = QHBoxLayout()

        button_layout_1 = QHBoxLayout()
        self.add_row_button = QPushButton("添加行数")
        self.add_row_button.clicked.connect(self.add_row)
        button_layout_1.addWidget(self.add_row_button)

        self.reset_button = QPushButton("恢复默认")
        self.reset_button.clicked.connect(self.reset_to_default)
        button_layout_1.addWidget(self.reset_button)

        self.calculate_button = QPushButton("确认计算")
        self.calculate_button.clicked.connect(self.calculate_total_price)
        button_layout_1.addWidget(self.calculate_button)

        self.layout.addLayout(button_layout_1)

        button_layout_2 = QHBoxLayout()
        self.export_to_clipboard_button = QPushButton("导出到剪切板")
        self.export_to_clipboard_button.clicked.connect(self.export_to_clipboard)
        button_layout_2.addWidget(self.export_to_clipboard_button)

        self.import_from_clipboard_button = QPushButton("从剪切板导入")
        self.import_from_clipboard_button.clicked.connect(self.import_from_clipboard)
        button_layout_2.addWidget(self.import_from_clipboard_button)

        self.export_to_file_button = QPushButton("导出到文件")
        self.export_to_file_button.clicked.connect(self.show_export_dialog)
        button_layout_2.addWidget(self.export_to_file_button)

        self.import_from_file_button = QPushButton("从文件导入")
        self.import_from_file_button.clicked.connect(self.show_import_dialog)
        button_layout_2.addWidget(self.import_from_file_button)

        self.layout.addLayout(button_layout_2)

        self.add_default_rows()

        # tab键功能修改
        self.table_widget.installEventFilter(self)

    def add_default_rows(self):
        default_rows = [
            ["CPU", "", "0", "1"],
            ["主板", "", "0", "1"],
            ["内存", "", "0", "1"],
            ["GPU", "", "0", "1"],
            ["硬盘", "", "0", "1"],
            ["电源", "", "0", "1"],
            ["机箱", "", "0", "1"],
            ["散热", "", "0", "1"],
            ["屏幕", "", "0", "1"],
            ["键盘", "", "0", "1"],
            ["鼠标", "", "0", "1"],
            ["音箱", "", "0", "1"]
        ]

        for row_data in default_rows:
            self.add_row(row_data)

    def add_row(self, row_data=None):
        row_position = self.table_widget.rowCount()
        self.table_widget.insertRow(row_position)

        if row_data:
            for column, data in enumerate(row_data):
                if column == 2 or column == 3:  # 价格和数量列
                    item = NumericTableWidgetItem(data)
                else:
                    item = QTableWidgetItem(data)
                self.table_widget.setItem(row_position, column, item)

        delete_button = QPushButton("删除")
        delete_button.clicked.connect(lambda _, row=row_position: self.delete_row(row))
        self.table_widget.setCellWidget(row_position, 5, delete_button)

        total_price_item = QTableWidgetItem()
        total_price_item.setFlags(total_price_item.flags() & ~Qt.ItemIsEditable)
        self.table_widget.setItem(row_position, 4, total_price_item)

        self.table_widget.cellChanged.connect(self.calculate_total_price)
        self.table_widget.cellChanged.connect(self.update_item_total_price)

    def delete_row(self, row):
        sender_button = self.sender()
        if sender_button:
            index = self.table_widget.indexAt(sender_button.pos())
            if index.isValid():
                row = index.row()
        self.table_widget.removeRow(row)

    def update_item_total_price(self, row, column):
        if column in (2, 3):  # 价格或数量更改时更新单个物品总价
            price_item = self.table_widget.item(row, 2)
            quantity_item = self.table_widget.item(row, 3)
            total_price_item = self.table_widget.item(row, 4)  # 获取总价单元格
            if price_item and quantity_item and total_price_item:
                price = float(price_item.text())
                quantity = int(quantity_item.text())
                item_total_price = price * quantity
                total_price_item.setText(str(item_total_price))  # 更新现有总价单元格的文本

    def calculate_total_price(self):
        total_price = 0
        for row in range(self.table_widget.rowCount()):
            price_item = self.table_widget.item(row, 2)
            quantity_item = self.table_widget.item(row, 3)
            if price_item and quantity_item:
                price = float(price_item.text())
                quantity = int(quantity_item.text())
                total_price += price * quantity
        self.total_price_label.setText("总价格：{}".format(total_price))

    def reset_to_default(self):
        self.table_widget.clearContents()
        self.table_widget.setRowCount(0)
        self.add_default_rows()
        self.total_price_label.setText("总价格：0")

    def export_to_clipboard(self):
        config_text = self.generate_config_text()
        total_price = self.total_price_label.text()
        config_text += f"\n{total_price}"
        clipboard = QApplication.clipboard()
        clipboard.setText(config_text)
        QMessageBox.information(self, "导出成功", "配置已成功导出到剪切板！")

    def show_export_dialog(self):
        file_dialog = QFileDialog(self)
        file_path, _ = file_dialog.getSaveFileName(self, "导出到文件", "", "Text files (*.txt)")
        if file_path:
            config_text = self.generate_config_text()
            total_price = self.total_price_label.text()
            config_text += f"\n{total_price}"
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(config_text)
            QMessageBox.information(self, "导出成功", f"配置已成功导出到文件：{file_path}")

    def import_from_file(self, file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            config_text = file.read()
        self.load_config_text(config_text)

    def import_from_clipboard(self):
        clipboard = QApplication.clipboard()
        config_text = clipboard.text()
        self.load_config_text(config_text)

    def show_import_dialog(self):
        file_dialog = QFileDialog(self)
        file_path, _ = file_dialog.getOpenFileName(self, "选择配置文件", "", "Text files (*.txt)")
        if file_path:
            self.import_from_file(file_path)

    def load_config_text(self, config_text):
        rows = config_text.strip().split('\n')
        # 如果最后一行是总价格信息，则忽略该行
        if rows[-1].startswith("总价格"):
            rows = rows[:-1]
        # 移除所有的空行
        rows = [row for row in rows if row.strip()]
        self.table_widget.setRowCount(len(rows))
        for i, row in enumerate(rows):
            columns = row.strip().split('\t')
            for j, data in enumerate(columns):
                item = QTableWidgetItem(data)
                self.table_widget.setItem(i, j, item)
            # 添加删除按钮
            delete_button = QPushButton("删除")
            delete_button.clicked.connect(lambda _, row=i: self.delete_row(row))
            self.table_widget.setCellWidget(i, 5, delete_button)
        self.calculate_total_price()

        # 设置总价列为只读
        for row in range(self.table_widget.rowCount()):
            total_price_item = self.table_widget.item(row, 4)
            if total_price_item:
                total_price_item.setFlags(total_price_item.flags() & ~Qt.ItemIsEditable)  # 设置为只读

    def generate_config_text(self):
        config_text = ""
        for row in range(self.table_widget.rowCount()):
            for column in range(self.table_widget.columnCount()):
                item = self.table_widget.item(row, column)
                if item:
                    config_text += item.text() + "\t"
                else:
                    config_text += "\t"
            config_text += "\n"
        return config_text

    def eventFilter(self, obj, event):
        if obj == self.table_widget and event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Tab:
                current_item = self.table_widget.currentItem()
                if current_item:
                    current_row = current_item.row()
                    current_column = current_item.column()
                    if current_column == 3:  # 如果当前焦点在数量列
                        next_row = current_row + 1
                        if next_row < self.table_widget.rowCount():  # 检查是否有下一行
                            next_item = self.table_widget.item(next_row, 1)  # 下一行的第二列（硬件具体型号）作为焦点
                            if next_item:
                                self.table_widget.setCurrentItem(next_item)
                        else:
                            self.table_widget.setCurrentCell(0, 1)  # 移动到第一行的第一列
                        return True
            elif event.key() == Qt.Key_Backtab:  # Shift+Tab
                current_item = self.table_widget.currentItem()
                if current_item:
                    current_row = current_item.row()
                    current_column = current_item.column()
                    if current_column == 1:  # 如果当前焦点在具体型号列
                        prev_row = current_row - 1
                        if prev_row >= 0:  # 检查是否有上一行
                            prev_item = self.table_widget.item(prev_row, 3)  # 上一行的数量列作为焦点
                            if prev_item:
                                self.table_widget.setCurrentItem(prev_item)
                        else:
                            self.table_widget.setCurrentCell(self.table_widget.rowCount() - 1, 3)
                        return True
        return super().eventFilter(obj, event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MachinePriceCalculator()
    window.show()
    sys.exit(app.exec_())
