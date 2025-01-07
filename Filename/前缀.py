import sys
import os
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QListWidget,
    QLabel,
)
from PyQt5.QtCore import Qt
from pypinyin import lazy_pinyin


class PrefixApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # 主布局
        main_layout = QVBoxLayout()

        # 文件选择区域
        file_layout = QHBoxLayout()
        self.file_list = QListWidget()
        self.file_list.setAcceptDrops(True)
        self.file_list.setDragEnabled(True)
        self.file_list.setSelectionMode(QListWidget.ExtendedSelection)
        self.file_list.dragEnterEvent = self.dragEnterEvent
        self.file_list.dragMoveEvent = self.dragMoveEvent
        self.file_list.dropEvent = self.dropEvent

        select_btn = QPushButton("选择文件/文件夹")
        select_btn.clicked.connect(self.select_files)

        # 清空列表按钮
        clear_btn = QPushButton("清空列表")
        clear_btn.clicked.connect(self.clear_list)

        # 前缀排序按钮
        sort_btn = QPushButton("前缀排序")
        sort_btn.clicked.connect(self.sort_prefixes)

        # 文件列表和按钮区域
        file_control_layout = QVBoxLayout()
        file_control_layout.addWidget(select_btn)
        file_control_layout.addWidget(clear_btn)
        file_control_layout.addWidget(sort_btn)

        file_layout.addWidget(QLabel("文件列表:"))
        file_layout.addWidget(self.file_list)
        file_layout.addLayout(file_control_layout)

        # 前缀输入区域
        prefix_layout = QHBoxLayout()
        self.prefix_input = QLineEdit()
        self.prefix_input.setPlaceholderText("请输入前缀")

        add_btn = QPushButton("添加前缀")
        add_btn.clicked.connect(self.add_prefix)

        remove_btn = QPushButton("删除前缀")
        remove_btn.clicked.connect(self.remove_prefix)

        prefix_layout.addWidget(QLabel("前缀:"))
        prefix_layout.addWidget(self.prefix_input)
        prefix_layout.addWidget(add_btn)
        prefix_layout.addWidget(remove_btn)

        # 添加到主布局
        main_layout.addLayout(file_layout)
        main_layout.addLayout(prefix_layout)

        self.setLayout(main_layout)
        self.setWindowTitle("文件前缀管理器")
        self.setGeometry(300, 300, 600, 400)

    def select_files(self):
        options = QFileDialog.Options()
        files, _ = QFileDialog.getOpenFileNames(
            self, "选择文件", "", "All Files (*);;", options=options
        )
        if files:
            self.file_list.addItems(files)

        dir_path = QFileDialog.getExistingDirectory(self, "选择文件夹")
        if dir_path:
            for root, dirs, files in os.walk(dir_path):
                for file in files:
                    self.file_list.addItem(os.path.join(root, file))

    def add_prefix(self):
        prefix = self.prefix_input.text().strip()
        if not prefix:
            return

        prefix = f"{prefix}-"

        has_error = False
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            file_path = item.text()
            dir_name, file_name = os.path.split(file_path)

            if prefix in file_name:
                has_error = True
                continue

            new_name = prefix + file_name
            new_path = os.path.join(dir_name, new_name)

            try:
                os.rename(file_path, new_path)
                item.setText(new_path)
            except Exception as e:
                print(f"重命名失败: {e}")
                has_error = True

        if has_error:
            self.prefix_input.setStyleSheet("border: 1px solid red;")
            self.prefix_input.setToolTip("部分文件已包含该前缀或重命名失败")
            from PyQt5.QtCore import QTimer

            QTimer.singleShot(500, lambda: self.prefix_input.setStyleSheet(""))
        else:
            self.prefix_input.setStyleSheet("")
            self.prefix_input.setToolTip("")

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()

            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if os.path.isfile(file_path):
                    self.file_list.addItem(file_path)
                elif os.path.isdir(file_path):
                    for root, dirs, files in os.walk(file_path):
                        for file in files:
                            self.file_list.addItem(os.path.join(root, file))
        else:
            event.ignore()

    def clear_list(self):
        self.file_list.clear()

    def sort_prefixes(self):
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            file_path = item.text()
            dir_name, file_name = os.path.split(file_path)

            # 分割文件名中的前缀部分
            parts = file_name.split("-")
            if len(parts) > 1:
                # 获取前缀部分
                prefixes = parts[:-1]
                # 获取文件名部分
                filename = parts[-1]

                # 使用拼音排序前缀部分
                sorted_prefixes = sorted(
                    prefixes, key=lambda x: "".join(lazy_pinyin(x)).lower()
                )

                # 重新组合文件名
                new_name = "-".join(sorted_prefixes) + "-" + filename
                new_path = os.path.join(dir_name, new_name)

                try:
                    os.rename(file_path, new_path)
                    item.setText(new_path)
                except Exception as e:
                    print(f"重命名失败: {e}")

    def remove_prefix(self):
        prefix = self.prefix_input.text().strip()
        if not prefix:
            return

        prefix = f"{prefix}-"

        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            file_path = item.text()
            dir_name, file_name = os.path.split(file_path)

            if prefix in file_name:
                new_name = file_name.replace(prefix, "")
                new_path = os.path.join(dir_name, new_name)

                try:
                    os.rename(file_path, new_path)
                    item.setText(new_path)
                except Exception as e:
                    print(f"重命名失败: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = PrefixApp()
    ex.show()
    sys.exit(app.exec_())
