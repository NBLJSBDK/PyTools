import sys
from io import BytesIO
import qrcode
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QTextEdit, QLabel, QRadioButton, QButtonGroup, 
                             QGroupBox, QGridLayout, QComboBox, QCheckBox, QLineEdit)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt

class AdvancedQRCodeApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('高级本地二维码生成器 (含尺寸验证)')
        # 稍微加宽一点窗口，确保自定义输入框有足够空间
        self.resize(850, 600)

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

        # === 下半部分：参数设置 ===
        settings_group = QGroupBox("生成参数微调区")
        grid = QGridLayout()

        # 1. 码制 (保持不变)
        grid.addWidget(QLabel("码制："), 0, 0)
        self.format_group = QButtonGroup(self)
        formats = ["QR Code", "汉信码 (需额外库)", "PDF417 (需额外库)", "Data Matrix (需额外库)"]
        for i, fmt in enumerate(formats):
            rb = QRadioButton(fmt)
            if i == 0: rb.setChecked(True)
            else: rb.setEnabled(False)
            self.format_group.addButton(rb, i)
            grid.addWidget(rb, 0, i + 1)

        # 2. 容错率 (保持不变)
        grid.addWidget(QLabel("容错率："), 1, 0)
        self.ec_group = QButtonGroup(self)
        ecs = [("7% (L)", qrcode.constants.ERROR_CORRECT_L), 
               ("15% (M)", qrcode.constants.ERROR_CORRECT_M), 
               ("25% (Q)", qrcode.constants.ERROR_CORRECT_Q), 
               ("30% (H)", qrcode.constants.ERROR_CORRECT_H)]
        for i, (text, val) in enumerate(ecs):
            rb = QRadioButton(text)
            if i == 1: rb.setChecked(True)
            rb.setProperty("ec_val", val)
            rb.clicked.connect(self.update_qr_code)
            self.ec_group.addButton(rb, i)
            grid.addWidget(rb, 1, i + 1)

        # 3. 尺寸 (【核心升级区域】)
        grid.addWidget(QLabel("显示尺寸："), 2, 0)
        self.size_group = QButtonGroup(self)
        sizes = [300, 400, 500, 600]
        
        # 添加固定的尺寸单选按钮
        for i, size in enumerate(sizes):
            rb = QRadioButton(f"{size}x{size}px")
            if i == 0: rb.setChecked(True)
            rb.setProperty("size_val", size)
            rb.clicked.connect(self.update_qr_code)
            self.size_group.addButton(rb, i)
            grid.addWidget(rb, 2, i + 1)

        # 添加“自定义”选项和输入框的组合布局
        custom_layout = QHBoxLayout()
        self.custom_size_rb = QRadioButton("自定义:")
        self.custom_size_rb.setProperty("size_val", -1) # 用 -1 作为自定义的特殊标记
        self.custom_size_rb.clicked.connect(self.update_qr_code)
        
        self.custom_size_input = QLineEdit()
        self.custom_size_input.setPlaceholderText("100-2000")
        self.custom_size_input.setFixedWidth(80)
        self.custom_size_input.setEnabled(False) # 默认不选中，所以输入框置灰禁用
        
        # 联动逻辑：点击“自定义”单选按钮时，才启用输入框
        self.custom_size_rb.toggled.connect(self.custom_size_input.setEnabled)
        # 联动逻辑：输入框内容改变时，实时更新二维码
        self.custom_size_input.textChanged.connect(self.update_qr_code)

        custom_layout.addWidget(self.custom_size_rb)
        custom_layout.addWidget(self.custom_size_input)
        
        self.size_group.addButton(self.custom_size_rb, len(sizes))
        grid.addLayout(custom_layout, 2, len(sizes) + 1) # 放在最后一列

        # 4. 码版本 (保持不变)
        grid.addWidget(QLabel("码版本："), 3, 0)
        version_layout = QHBoxLayout()
        self.auto_version_cb = QCheckBox("根据内容自动调整")
        self.auto_version_cb.setChecked(True)
        self.auto_version_cb.stateChanged.connect(self.toggle_version_box)
        
        self.version_combo = QComboBox()
        for v in range(1, 41): self.version_combo.addItem(f"版本 {v}")
        self.version_combo.setEnabled(False)
        self.version_combo.currentIndexChanged.connect(self.update_qr_code)

        version_layout.addWidget(self.auto_version_cb)
        version_layout.addWidget(self.version_combo)
        version_layout.addStretch()
        grid.addLayout(version_layout, 3, 1, 1, 4)

        # 5. 码边距 (保持不变)
        grid.addWidget(QLabel("码边距："), 4, 0)
        self.margin_group = QButtonGroup(self)
        for i in range(1, 5):
            rb = QRadioButton(f"{i} 个色块")
            if i == 4: rb.setChecked(True)
            rb.setProperty("margin_val", i)
            rb.clicked.connect(self.update_qr_code)
            self.margin_group.addButton(rb, i)
            grid.addWidget(rb, 4, i)

        settings_group.setLayout(grid)
        main_layout.addWidget(settings_group, stretch=0)
        self.setLayout(main_layout)

    def toggle_version_box(self, state):
        self.version_combo.setEnabled(state != Qt.Checked)
        self.update_qr_code()

    def update_qr_code(self):
        text = self.text_input.toPlainText()
        if not text:
            self.qr_label.clear()
            self.qr_label.setStyleSheet("background-color: #f8f9fa; border: 1px solid #dee2e6;")
            self.qr_label.setText("等待输入...")
            return

        # === 获取并验证尺寸参数 ===
        target_size = self.size_group.checkedButton().property("size_val")
        
        # 如果等于 -1，说明用户选择了“自定义”
        if target_size == -1:
            try:
                # 尝试将输入的内容转换为整数
                custom_val = int(self.custom_size_input.text())
                
                # 校验合理范围：100px 到 2000px
                if custom_val < 100 or custom_val > 2000:
                    raise ValueError("Out of range") # 抛出异常，交给下面的 except 处理
                    
                target_size = custom_val # 验证通过，赋给最终尺寸变量
                
            except ValueError:
                # 捕获异常：如果输入的不是纯数字，或者超出了范围，显示警告
                self.qr_label.clear()
                self.qr_label.setStyleSheet("background-color: #ffeeba; border: 2px solid #ffc107; color: #856404; font-weight: bold;")
                self.qr_label.setText("⚠️ 尺寸输入错误：\n\n请输入 100 到 2000 之间的有效整数！")
                return

        # 恢复正常的显示样式（防止之前出错变黄后改不回来）
        self.qr_label.setStyleSheet("background-color: #f8f9fa; border: 1px solid #dee2e6;")

        ec_val = self.ec_group.checkedButton().property("ec_val")
        margin_val = self.margin_group.checkedButton().property("margin_val")
        version_val = None if self.auto_version_cb.isChecked() else self.version_combo.currentIndex() + 1

        try:
            qr = qrcode.QRCode(
                version=version_val,
                error_correction=ec_val,
                box_size=10, 
                border=margin_val,
            )
            qr.add_data(text)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")

            buffer = BytesIO()
            img.save(buffer, format="PNG")
            qimage = QImage.fromData(buffer.getvalue())
            pixmap = QPixmap.fromImage(qimage)

            scaled_pixmap = pixmap.scaled(
                target_size, target_size, 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )
            self.qr_label.setPixmap(scaled_pixmap)

        except Exception as e:
            self.qr_label.clear()
            self.qr_label.setStyleSheet("background-color: #f8d7da; border: 2px solid #f5c6cb; color: #721c24; font-weight: bold;")
            self.qr_label.setText(f"❌ 生成失败：\n\n数据过多，当前版本或容错率无法容纳。")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = AdvancedQRCodeApp()
    ex.show()
    sys.exit(app.exec_())