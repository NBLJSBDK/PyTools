import sys
import os
import hashlib
from PIL import Image
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, QDialog,
                            QFileDialog, QListWidget, QMessageBox, QCheckBox,
                            QHBoxLayout, QLabel, QLineEdit, QListWidgetItem,
                            QScrollArea, QRadioButton)
from PyQt5.QtCore import Qt, QThreadPool, QRunnable, pyqtSignal, QObject
from PyQt5.QtGui import QDragEnterEvent, QDropEvent, QPixmap

class ImageAnalyzer(QRunnable):
    def __init__(self, file_path, callback):
        super().__init__()
        self.file_path = file_path
        self.callback = callback

    def run(self):
        try:
            # 计算多种哈希值
            img_hash = hashlib.md5()
            with open(self.file_path, 'rb') as f:
                img_hash.update(f.read())
            img_hash = img_hash.hexdigest()

            perceptual_hash = self.calculate_perceptual_hash(self.file_path)
            combined_hash = f"{img_hash}_{perceptual_hash}"
            self.callback(self.file_path, combined_hash)
        except Exception as e:
            print(f"Error processing {self.file_path}: {str(e)}")

    def calculate_perceptual_hash(self, file_path):
        # 使用感知哈希算法
        hash_size = 16
        with Image.open(file_path) as img:
            img = img.convert("L").resize((hash_size, hash_size), Image.Resampling.LANCZOS)
            pixels = list(img.getdata())
            avg = sum(pixels) / len(pixels)
            bits = "".join(['1' if pixel > avg else '0' for pixel in pixels])
            return hex(int(bits, 2))[2:].zfill(16)

class ImageDeduplicator(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.image_hashes = {}
        self.duplicates = {}
        self.thread_pool = QThreadPool()
        self.total_images = 0
        self.processed_images = 0

    def initUI(self):
        self.setWindowTitle('图片去重工具')
        self.setGeometry(300, 300, 600, 400)
        self.setAcceptDrops(True)

        layout = QVBoxLayout()

        # 路径输入框
        self.path_input = QLineEdit(self)
        self.path_input.setPlaceholderText("拖放图片/文件夹到这里或点击选择")
        self.path_input.setReadOnly(True)
        layout.addWidget(self.path_input)

        # 选择按钮
        self.select_btn = QPushButton('选择图片或文件夹', self)
        self.select_btn.clicked.connect(self.select_files_or_folder)
        layout.addWidget(self.select_btn)

        # 状态标签
        self.status_label = QLabel('请选择或拖放图片/文件夹')
        layout.addWidget(self.status_label)

        # 重复图片列表
        self.duplicate_list = QListWidget()
        self.duplicate_list.itemDoubleClicked.connect(self.show_group_detail)
        layout.addWidget(self.duplicate_list)

        # 操作按钮布局
        btn_layout = QHBoxLayout()
        
        # 全局删除按钮
        self.global_delete_btn = QPushButton('删除所有非保留项', self)
        self.global_delete_btn.clicked.connect(self.global_delete)
        self.global_delete_btn.setEnabled(False)
        btn_layout.addWidget(self.global_delete_btn)

        # 刷新按钮
        self.refresh_btn = QPushButton('刷新', self)
        self.refresh_btn.clicked.connect(lambda: self.analyze_images(self.path_input.text()))
        btn_layout.addWidget(self.refresh_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择图片文件夹")
        if folder:
            self.path_input.setText(folder)
            self.analyze_images(folder)
            
    def select_files_or_folder(self):
        # 同时支持选择文件和文件夹
        options = QFileDialog.Options()
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "选择图片或文件夹",
            "",
            "图片文件 (*.jpg *.jpeg *.png *.bmp *.gif *.webp *.tiff);;所有文件 (*)",
            options=options
        )
        
        if files:
            # 如果选择了文件
            self.path_input.setText("; ".join(files))
            self.analyze_images(files)
        else:
            # 如果没有选择文件，尝试选择文件夹
            folder = QFileDialog.getExistingDirectory(self, "选择图片文件夹")
            if folder:
                self.path_input.setText(folder)
                self.analyze_images(folder)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls:
            paths = [url.toLocalFile() for url in urls]
            # 如果是文件夹
            if len(paths) == 1 and os.path.isdir(paths[0]):
                self.path_input.setText(paths[0])
                self.analyze_images(paths[0])
            # 如果是图片文件
            else:
                # 过滤出图片文件
                valid_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp', '.tiff']
                image_files = [f for f in paths if any(f.lower().endswith(ext) for ext in valid_extensions)]
                if image_files:
                    self.path_input.setText("; ".join(image_files))
                    self.analyze_images(image_files)

    def analyze_images(self, paths):
        self.image_hashes.clear()
        self.duplicates.clear()
        self.duplicate_list.clear()
        self.total_images = 0
        self.processed_images = 0

        # 支持的图片格式
        valid_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp', '.tiff']

        # 如果传入的是字符串，可能是文件夹路径
        if isinstance(paths, str):
            if os.path.isdir(paths):
                # 遍历文件夹中的图片
                for root, _, files in os.walk(paths):
                    for file in files:
                        if any(file.lower().endswith(ext) for ext in valid_extensions):
                            self.total_images += 1
                            file_path = os.path.join(root, file)
                            analyzer = ImageAnalyzer(file_path, self.process_image_result)
                            self.thread_pool.start(analyzer)
            else:
                # 单个文件
                if any(paths.lower().endswith(ext) for ext in valid_extensions):
                    self.total_images += 1
                    analyzer = ImageAnalyzer(paths, self.process_image_result)
                    self.thread_pool.start(analyzer)
        elif isinstance(paths, list):
            # 多个文件
            for file_path in paths:
                if any(file_path.lower().endswith(ext) for ext in valid_extensions):
                    self.total_images += 1
                    analyzer = ImageAnalyzer(file_path, self.process_image_result)
                    self.thread_pool.start(analyzer)

        if self.total_images == 0:
            self.status_label.setText("没有找到有效的图片文件")
            return

        # 启动定时器更新进度
        self.status_label.setText(f"正在分析图片 (0/{self.total_images})")
        self.startTimer(100)

    def timerEvent(self, event):
        """定时器事件，用于更新进度"""
        if self.processed_images < self.total_images:
            self.status_label.setText(f"正在分析图片 ({self.processed_images}/{self.total_images})")
        else:
            self.killTimer(event.timerId())
            self.show_results()

    def process_image_result(self, file_path, combined_hash):
        """处理单个图片的分析结果"""
        if combined_hash in self.image_hashes:
            if combined_hash not in self.duplicates:
                self.duplicates[combined_hash] = [self.image_hashes[combined_hash]]
            self.duplicates[combined_hash].append(file_path)
        else:
            self.image_hashes[combined_hash] = file_path
        
        self.processed_images += 1

    def show_results(self):
        """显示分析结果"""
        if self.duplicates:
            self.status_label.setText(f"找到 {len(self.duplicates)} 组重复图片")
            for img_hash, files in self.duplicates.items():
                item = QListWidgetItem()
                # 初始化selected_files属性
                item.selected_files = set()
                # 默认选择文件名最短的图片
                shortest_name = min(len(os.path.basename(f)) for f in files)
                for file in files:
                    if len(os.path.basename(file)) == shortest_name:
                        item.selected_files.add(file)
                # 设置显示文本
                item.setText(f"重复图片组 ({len(files)} 张，已保留 {len(item.selected_files)} 张)")
                item.setData(Qt.UserRole, files)
                self.duplicate_list.addItem(item)
            self.global_delete_btn.setEnabled(True)
        else:
            self.status_label.setText("未找到重复图片")
            self.global_delete_btn.setEnabled(False)

    def update_retain_count(self, item):
        """更新保留数量显示"""
        files = item.data(Qt.UserRole)
        retain_count = len(item.selected_files)
        item.setText(f"重复图片组 ({len(files)} 张，已保留 {retain_count} 张)")

    def show_group_detail(self, item):
        """显示单个重复组的详细选择界面"""
        files = item.data(Qt.UserRole)
        dialog = QDialog(self)
        dialog.setWindowTitle("选择要保留的图片")
        dialog.setMinimumSize(800, 600)
        layout = QVBoxLayout()

        label = QLabel(f"该组共有 {len(files)} 张重复图片，请选择要保留的图片：")
        layout.addWidget(label)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        content_layout = QVBoxLayout()

        # 初始化选择状态
        selected_files = set(item.selected_files) if hasattr(item, 'selected_files') else set()
        shortest_name = min(len(os.path.basename(f)) for f in files)

        for file in files:
            hbox = QHBoxLayout()

            checkbox = QCheckBox("保留此图片")
            if file in selected_files or len(os.path.basename(file)) == shortest_name:
                checkbox.setChecked(True)
                selected_files.add(file)

            checkbox.stateChanged.connect(lambda state, f=file, sf=selected_files: self.update_selected_file(f, state, sf))

            pixmap = QPixmap(file)
            if not pixmap.isNull():
                label = QLabel()
                label.setPixmap(pixmap.scaled(200, 200, Qt.KeepAspectRatio))
                label.mousePressEvent = lambda event, cb=checkbox: cb.toggle()
                hbox.addWidget(label)

            info = QLabel(f"{os.path.basename(file)}\n{os.path.getsize(file)/1024:.1f}KB")
            info.setCursor(Qt.PointingHandCursor)
            info.mousePressEvent = lambda event, cb=checkbox: cb.toggle()
            info.mouseDoubleClickEvent = lambda event, f=file: os.startfile(f)
            hbox.addWidget(info)

            hbox.addWidget(checkbox)

            content_layout.addLayout(hbox)

        content.setLayout(content_layout)
        scroll.setWidget(content)
        layout.addWidget(scroll)

        btn_layout = QHBoxLayout()

        delete_btn = QPushButton('删除当前组', dialog)
        delete_btn.clicked.connect(lambda: self.delete_group(files, dialog))
        btn_layout.addWidget(delete_btn)

        close_btn = QPushButton('关闭', dialog)
        close_btn.clicked.connect(dialog.accept)
        btn_layout.addWidget(close_btn)

        layout.addLayout(btn_layout)
        dialog.setLayout(layout)

        # 在对话框关闭前保存选择状态
        def save_and_close():
            item.selected_files = selected_files
            self.update_retain_count(item)
            # 强制刷新列表项显示
            self.duplicate_list.takeItem(self.duplicate_list.row(item))
            self.duplicate_list.insertItem(self.duplicate_list.row(item), item)
            dialog.accept()
            
        close_btn.clicked.disconnect()
        close_btn.clicked.connect(save_and_close)
        
        dialog.exec_()

    def update_selected_file(self, file, state, selected_files):
        """更新选择的文件"""
        if state == Qt.Checked:
            selected_files.add(file)
        else:
            selected_files.discard(file)

    def delete_group(self, files, dialog):
        """删除当前组中未选择的图片"""
        # 获取当前item
        current_item = self.duplicate_list.currentItem()
        if not hasattr(current_item, 'selected_files'):
            return
            
        files_to_delete = [f for f in files if f not in current_item.selected_files]
        if files_to_delete:
            confirm = QMessageBox.question(self, "确认删除",
                                         f"确定要删除 {len(files_to_delete)} 张图片吗？",
                                         QMessageBox.Yes | QMessageBox.No)
            if confirm == QMessageBox.Yes:
                for file in files_to_delete:
                    try:
                        os.remove(file)
                    except Exception as e:
                        print(f"Error deleting {file}: {str(e)}")
                dialog.close()
                self.analyze_images(self.path_input.text())
                QMessageBox.information(self, "完成", "删除操作已完成")

    def global_delete(self):
        """全局删除所有非保留项"""
        total_to_delete = 0
        files_to_delete = []
        
        # 遍历所有重复组
        for i in range(self.duplicate_list.count()):
            item = self.duplicate_list.item(i)
            files = item.data(Qt.UserRole)
            
            # 获取该组的选择状态
            selected_files = set()
            # 检查是否有用户选择记录
            if hasattr(item, 'selected_files'):
                selected_files = item.selected_files
            else:
                # 如果没有用户选择，则默认保留文件名最短的
                for file in files:
                    if len(os.path.basename(file)) == min(len(os.path.basename(f)) for f in files):
                        selected_files.add(file)
            
            # 添加要删除的文件
            for file in files:
                if file not in selected_files:
                    files_to_delete.append(file)
                    total_to_delete += 1

        if total_to_delete == 0:
            QMessageBox.information(self, "提示", "没有需要删除的图片")
            return

        confirm = QMessageBox.question(self, "确认删除",
                                     f"确定要删除所有 {total_to_delete} 张重复图片吗？",
                                     QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            # 删除文件
            for file in files_to_delete:
                try:
                    os.remove(file)
                except Exception as e:
                    print(f"Error deleting {file}: {str(e)}")
            
            # 重新分析图片
            self.analyze_images(self.path_input.text())
            QMessageBox.information(self, "完成", f"已删除 {total_to_delete} 张重复图片")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ImageDeduplicator()
    ex.show()
    sys.exit(app.exec_())
