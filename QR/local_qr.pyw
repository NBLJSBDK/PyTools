import sys
from io import BytesIO
import qrcode
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QTextEdit, QLabel, QRadioButton, QButtonGroup, 
                             QGroupBox, QGridLayout, QComboBox, QSpinBox, QCheckBox)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt

class AdvancedQRCodeApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('高级本地二维码生成器')
        self.resize(800, 600)

        # 总体垂直布局 (上半部分：输入输出；下半部分：参数设置)
        main_layout = QVBoxLayout()

        # === 上半部分：左右布局 ===
        top_layout = QHBoxLayout()
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("在此处输入文本...\n修改下方参数，二维码会实时更新。")
        self.text_input.textChanged.connect(self.update_qr_code)

        self.qr_label = QLabel("等待输入...")
        self.qr_label.setAlignment(Qt.AlignCenter)
        self.qr_label.setMinimumSize(300, 300)
        self.qr_label.setStyleSheet("background-color: #f8f9fa; border: 1px solid #dee2e6;")

        top_layout.addWidget(self.text_input, stretch=1)
        top_layout.addWidget(self.qr_label, stretch=1)
        main_layout.addLayout(top_layout, stretch=2)

        # === 下半部分：5行参数设置 ===
        settings_group = QGroupBox("生成参数微调区")
        grid = QGridLayout()

        # 1. 码制 (Barcode Format)
        grid.addWidget(QLabel("码制："), 0, 0)
        self.format_group = QButtonGroup(self)
        formats = ["QR Code", "汉信码 (需额外库)", "PDF417 (需额外库)", "Data Matrix (需额外库)"]
        for i, fmt in enumerate(formats):
            rb = QRadioButton(fmt)
            if i == 0:
                rb.setChecked(True) # 默认选中 QR Code
            else:
                rb.setEnabled(False) # 其他暂时禁用，防止报错
            self.format_group.addButton(rb, i)
            grid.addWidget(rb, 0, i + 1)

        # 2. 容错率 (Error Correction)
        grid.addWidget(QLabel("容错率："), 1, 0)
        self.ec_group = QButtonGroup(self)
        ecs = [("7% (L)", qrcode.constants.ERROR_CORRECT_L), 
               ("15% (M)", qrcode.constants.ERROR_CORRECT_M), 
               ("25% (Q)", qrcode.constants.ERROR_CORRECT_Q), 
               ("30% (H)", qrcode.constants.ERROR_CORRECT_H)]
        for i, (text, val) in enumerate(ecs):
            rb = QRadioButton(text)
            if i == 1: rb.setChecked(True) # 默认 15% 容错
            rb.setProperty("ec_val", val)  # 保存真实对应的值
            rb.clicked.connect(self.update_qr_code)
            self.ec_group.addButton(rb, i)
            grid.addWidget(rb, 1, i + 1)

        # 3. 尺寸 (Size)
        grid.addWidget(QLabel("显示尺寸："), 2, 0)
        self.size_group = QButtonGroup(self)
        sizes = [300, 400, 500, 600]
        for i, size in enumerate(sizes):
            rb = QRadioButton(f"{size}x{size}px")
            if i == 0: rb.setChecked(True) # 默认 300
            rb.setProperty("size_val", size)
            rb.clicked.connect(self.update_qr_code)
            self.size_group.addButton(rb, i)
            grid.addWidget(rb, 2, i + 1)

        # 4. 码版本 (Version)
        grid.addWidget(QLabel("码版本："), 3, 0)
        version_layout = QHBoxLayout()
        self.auto_version_cb = QCheckBox("根据内容自动调整")
        self.auto_version_cb.setChecked(True)
        self.auto_version_cb.stateChanged.connect(self.toggle_version_box)
        
        self.version_combo = QComboBox()
        for v in range(1, 41):
            self.version_combo.addItem(f"版本 {v}")
        self.version_combo.setEnabled(False) # 默认自动，所以手动选择框置灰
        self.version_combo.currentIndexChanged.connect(self.update_qr_code)

        version_layout.addWidget(self.auto_version_cb)
        version_layout.addWidget(self.version_combo)
        version_layout.addStretch()
        grid.addLayout(version_layout, 3, 1, 1, 4) # 跨列显示

        # 5. 码边距 (Border Margin)
        grid.addWidget(QLabel("码边距："), 4, 0)
        self.margin_group = QButtonGroup(self)
        for i in range(1, 5):
            rb = QRadioButton(f"{i} 个色块")
            if i == 4: rb.setChecked(True) # qrcode库默认边距是4
            rb.setProperty("margin_val", i)
            rb.clicked.connect(self.update_qr_code)
            self.margin_group.addButton(rb, i)
            grid.addWidget(rb, 4, i)

        settings_group.setLayout(grid)
        main_layout.addWidget(settings_group, stretch=0)
        self.setLayout(main_layout)

    def toggle_version_box(self, state):
        # 如果勾选了自动，则禁用下拉框；否则启用
        self.version_combo.setEnabled(state != Qt.Checked)
        self.update_qr_code()

    def update_qr_code(self):
        text = self.text_input.toPlainText()
        if not text:
            self.qr_label.clear()
            self.qr_label.setText("等待输入...")
            return

        # --- 获取用户面板选择的参数 ---
        # 获取容错率
        ec_val = self.ec_group.checkedButton().property("ec_val")
        # 获取边距
        margin_val = self.margin_group.checkedButton().property("margin_val")
        # 获取版本 (如果是自动，传 None 给 qrcode 库)
        version_val = None if self.auto_version_cb.isChecked() else self.version_combo.currentIndex() + 1
        # 获取目标显示尺寸
        target_size = self.size_group.checkedButton().property("size_val")

        try:
            # 配置并生成二维码
            qr = qrcode.QRCode(
                version=version_val,
                error_correction=ec_val,
                box_size=10, 
                border=margin_val,
            )
            qr.add_data(text)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")

            # 转换为 Qt 图像
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            qimage = QImage.fromData(buffer.getvalue())
            pixmap = QPixmap.fromImage(qimage)

            # 根据用户选择的尺寸进行缩放
            scaled_pixmap = pixmap.scaled(
                target_size, target_size, 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )
            self.qr_label.setPixmap(scaled_pixmap)

        except Exception as e:
            # 如果文本太多，但用户手动选择了很小的版本，会抛出异常
            self.qr_label.clear()
            self.qr_label.setText(f"生成失败：\n数据过多，当前版本或容错率无法容纳。")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = AdvancedQRCodeApp()
    ex.show()
    sys.exit(app.exec_())
    