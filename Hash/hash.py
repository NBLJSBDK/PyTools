import sys
import time
from PyQt5.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLineEdit,
    QMainWindow,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QTextEdit,
    QProgressBar,
    QCheckBox,
    QGridLayout,
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QDragEnterEvent, QDropEvent
import hashlib
import os
import datetime
import zlib


class HashCalculator(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Hash计算")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.text_edit = QTextEdit()
        self.text_edit.setAcceptDrops(True)
        self.text_edit.setPlaceholderText("将文件拖放到此处以计算哈希值")
        self.text_edit.dragEnterEvent = self.dragEnterEvent
        self.text_edit.dropEvent = self.dropEvent
        # ---------------------------
        # 设置俩进度条的布局
        self.progress_bar_layout = QGridLayout()
        # 当前文件计算进度
        self.progress_bar_files = QProgressBar()
        self.progress_bar_files.setTextVisible(True)
        # 已经处理个数
        self.progress_bar_current = QProgressBar()
        self.progress_bar_current.setTextVisible(True)
        # 采用网格布局
        self.progress_bar_layout.addWidget(QLabel("当前文件计算进度:"), 0, 0)
        self.progress_bar_layout.addWidget(self.progress_bar_files, 0, 1)
        self.progress_bar_layout.addWidget(QLabel("完成个数:"), 1, 0)
        self.progress_bar_layout.addWidget(self.progress_bar_current, 1, 1)
        # ---------------------------
        # 清除文本框
        self.button_layout = QGridLayout()
        self.button_layout.addWidget(
            QPushButton("清除文本框", clicked=self.clear_text_edit)
        )
        # ---------------------------
        # 对比HASH
        self.compare_layout = QHBoxLayout()
        self.input_compare = QLineEdit()
        self.paste_button = QPushButton("粘贴", clicked=self.pasteFromClipboard)
        self.clear_comparetext_button = QPushButton(
            "清除", clicked=self.clear_comparetext
        )
        self.compare_button = QPushButton("对比", clicked=self.compareHash)
        self.compare_layout.addWidget(self.input_compare)
        self.compare_layout.addWidget(self.paste_button)
        self.compare_layout.addWidget(self.clear_comparetext_button)
        self.compare_layout.addWidget(self.compare_button)
        # ---------------------------
        # 功能控制
        self.checkbox_layout = QGridLayout()
        # MD5
        self.checkbox_md5 = QCheckBox("MD5")
        self.checkbox_md5.setChecked(True)
        self.checkbox_layout.addWidget(self.checkbox_md5, 0, 0)
        # SHA1
        self.checkbox_sha1 = QCheckBox("SHA1")
        self.checkbox_sha1.setChecked(True)
        self.checkbox_layout.addWidget(self.checkbox_sha1, 0, 1)
        # CRC32
        self.checkbox_crc32 = QCheckBox("CRC32")
        self.checkbox_crc32.setChecked(True)
        self.checkbox_layout.addWidget(self.checkbox_crc32, 0, 2)
        # 添加用于开启或关闭时间显示功能的复选框
        self.checkbox_time = QCheckBox("显示修改时间")
        self.checkbox_time.setChecked(True)
        self.checkbox_layout.addWidget(self.checkbox_time, 0, 3)
        # SHA224
        self.checkbox_sha224 = QCheckBox("SHA224")
        self.checkbox_sha224.setChecked(False)
        self.checkbox_layout.addWidget(self.checkbox_sha224, 1, 0)
        # SHA256
        self.checkbox_sha256 = QCheckBox("SHA256")
        self.checkbox_sha256.setChecked(False)
        self.checkbox_layout.addWidget(self.checkbox_sha256, 1, 1)
        # SHA384
        self.checkbox_sha384 = QCheckBox("SHA384")
        self.checkbox_sha384.setChecked(False)
        self.checkbox_layout.addWidget(self.checkbox_sha384, 1, 2)
        # SHA512
        self.checkbox_sha512 = QCheckBox("SHA512")
        self.checkbox_sha512.setChecked(False)
        self.checkbox_layout.addWidget(self.checkbox_sha512, 1, 3)

        # 总布局调整
        self.layout.addWidget(self.text_edit)
        self.layout.addLayout(self.progress_bar_layout)
        self.layout.addLayout(self.checkbox_layout)
        self.layout.addLayout(self.button_layout)
        self.layout.addLayout(self.compare_layout)
        # 创建工作线程
        self.worker = HashWorker()
        self.worker.hashFinished.connect(self.handle_hash_finished)
        self.worker.progressUpdated.connect(self.update_progress_bar_current)
        self.worker.schedulesUpdated.connect(self.update_progress_bar_files)
        self.worker.checkbox_time = self.checkbox_time
        self.worker.checkbox_md5 = self.checkbox_md5
        self.worker.checkbox_sha1 = self.checkbox_sha1
        self.worker.checkbox_crc32 = self.checkbox_crc32
        self.worker.checkbox_sha224 = self.checkbox_sha224
        self.worker.checkbox_sha256 = self.checkbox_sha256
        self.worker.checkbox_sha384 = self.checkbox_sha384
        self.worker.checkbox_sha512 = self.checkbox_sha512

    # 判断拖拽
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    # 获取URL并且开始计算哈希
    def dropEvent(self, event: QDropEvent):
        files = [url.toLocalFile() for url in event.mimeData().urls()]
        self.worker.calculate_hashes(files)

    # 更新第一个进度条，显示当前处理的文件进度
    def update_progress_bar_current(self, progress):
        self.progress_bar_current.setValue(progress)
    # 当前文件计算进度
    def update_progress_bar_files(self, schedules):
        self.progress_bar_files.setValue(schedules)
    

    # 清除文本框内容
    def clear_text_edit(self):
        self.text_edit.clear()
        self.progress_bar_files.setValue(0)
        self.progress_bar_current.setValue(0)

    # 复制内容到对比框
    def pasteFromClipboard(self):
        clipboard = QApplication.clipboard()
        self.input_compare.setText(clipboard.text())

    # 清除文本框内容
    def clear_comparetext(self):
        self.input_compare.clear()

    # 对比HASH
    def compareHash(self):
        compare_value = self.input_compare.text().strip().upper()
        if not compare_value:
            return
        hash_lines = self.text_edit.toPlainText().split("\n")
        # 遍历每一行,并且保存"行"和"行对应的内容"到i,line
        for i, line in enumerate(hash_lines):
            if compare_value in line:
                # 初始化"文件名称行"的变量
                file_line_index = None
                # 逆序遍历找到文件行
                for j in range(i, -1, -1):
                    if "文件:" in hash_lines[j]:
                        file_line_index = j
                        break
                # 如果找到了文件行
                if file_line_index is not None:
                    # .split(":") 将 文件行用":"分割为多个部分并形成列表
                    # [1:] 将 取出索引为1开始（不包括索引为0的部分）到最后一个元素的子列表
                    # ":".join(...) 将 用":"分割后的列表的子列表用冒号重新连接起来,重新组合文件名
                    # .strip() 去除字符串两段空格
                    file_name = ":".join(
                        hash_lines[file_line_index].split(":")[1:]
                    ).strip()
                    self.text_edit.append(
                        f"与 {file_name} 的 {line.split(':')[0].strip()} 值相同"
                    )
                    return
        self.text_edit.append("未找到相同hash值")

    # 哈希计算完成处理
    def handle_hash_finished(self, result):
        self.text_edit.append(result)

    # 关闭窗口时终止工作线程
    def closeEvent(self, event):
        self.worker.stop()
        event.accept()


class HashWorker(QThread):
    # 槽函数,传递信息用的
    hashFinished = pyqtSignal(str)
    # 新增的信号，用于实时更新处理个数
    progressUpdated = pyqtSignal(int)
    schedulesUpdated = pyqtSignal(int)

    def __init__(self):
        super().__init__()

        self.stopped = False
        self.checkbox_time = None
        self.checkbox_md5 = None
        self.checkbox_sha1 = None
        self.checkbox_crc32 = None
        self.checkbox_sha224 = None
        self.checkbox_sha256 = None
        self.checkbox_sha384 = None
        self.checkbox_sha512 = None

    def stop(self):
        self.stopped = True

    def calculate_hashes(self, files):
        self.files = files
        self.start()

    def run(self):
        total_files = len(self.files)
        for i, file_path in enumerate(self.files, start=1):
            if self.stopped:
                return

            if not os.path.isfile(file_path):
                self.hashFinished.emit(
                    f"警告：{file_path} 不是一个有效的文件，跳过计算。\n"
                )
                continue
            else:
                file_name = file_path
                file_size = os.path.getsize(file_path)

                modified_time = ""
                md5_hash = ""
                sha1_hash = ""
                sha224_hash = ""
                sha256_hash = ""
                sha384_hash = ""
                sha512_hash = ""
                crc32_hash = ""

                # if self.stopped:
                #     return

                if self.checkbox_time.isChecked():
                    modified_time = datetime.datetime.fromtimestamp(
                        os.path.getmtime(file_path)
                    ).strftime("%Y年%m月%d日, %H:%M:%S")
                if self.checkbox_md5.isChecked():
                    md5_hash = f"MD5: {self.calculate_hash(file_path, 'md5').upper()}\n"
                if self.checkbox_sha1.isChecked():
                    sha1_hash = (
                        f"SHA1: {self.calculate_hash(file_path, 'sha1').upper()}\n"
                    )
                if self.checkbox_sha224.isChecked():
                    sha224_hash = (
                        f"SHA224: {self.calculate_hash(file_path, 'sha224').upper()}\n"
                    )
                if self.checkbox_sha256.isChecked():
                    sha256_hash = (
                        f"SHA256: {self.calculate_hash(file_path, 'sha256').upper()}\n"
                    )
                if self.checkbox_sha384.isChecked():
                    sha384_hash = (
                        f"SHA384: {self.calculate_hash(file_path, 'sha384').upper()}\n"
                    )
                if self.checkbox_sha512.isChecked():
                    sha512_hash = (
                        f"SHA512: {self.calculate_hash(file_path, 'sha512').upper()}\n"
                    )
                if self.checkbox_crc32.isChecked():
                    crc32_hash = f"CRC32: {self.calculate_crc32(file_path).upper()}\n"

                result = (
                    f"文件: {file_name}\n"
                    f"大小: {file_size} 字节\n"
                    f"{'' if modified_time == '' else f'修改时间: {modified_time}\n'}"
                    f"{md5_hash}{sha1_hash}{sha224_hash}{sha256_hash}{sha384_hash}{sha512_hash}{crc32_hash}"
                )
                self.hashFinished.emit(result)
                # 计算并发送当前文件处理进度
                progress = int((i / total_files) * 100)
                self.progressUpdated.emit(progress)

    def calculate_hash(self, file_path, algorithm):
        file_size = os.path.getsize(file_path)  # 获取文件大小
        hasher = hashlib.new(algorithm)
        progress_generator = self.schedule(file_size)  # 创建生成器对象，传递文件大小
        next(progress_generator)  # 启动生成器
        with open(file_path, "rb") as file:
            total_read = 0  # 记录已读取的字节数
            while True:
                data = file.read(4096)
                if not data:
                    break
                hasher.update(data)
                total_read += len(data)  # 更新已读取的字节数
                progress_generator.send(total_read)  # 发送当前时间和已读取的字节数给生成器
                hasher.update(data)
        return hasher.hexdigest()

    def calculate_crc32(self, file_path):
        file_size = os.path.getsize(file_path)  # 获取文件大小
        progress_generator = self.schedule(file_size)  # 创建生成器对象，传递文件大小
        next(progress_generator)  # 启动生成器
        crc = 0
        with open(file_path, "rb") as file:
            total_read = 0  # 记录已读取的字节数
            while True:
                data = file.read(4096)
                if not data:
                    break
                total_read += len(data)  # 更新已读取的字节数
                progress_generator.send(total_read)  # 发送当前时间和已读取的字节数给生成器
                crc = zlib.crc32(data, crc)
        return "%08X" % (crc & 0xFFFFFFFF)
    

    def schedule(self,file_size):
        tenth_size = file_size // 10
        progress_point = tenth_size 
        while True:
            total_read = yield
            if total_read >= progress_point:
                    schedules = int((total_read / file_size) * 100)  # 计算处理进度
                    self.schedulesUpdated.emit(schedules)
                    progress_point += tenth_size  # 更新输出进度的点


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HashCalculator()
    window.show()
    sys.exit(app.exec_())
