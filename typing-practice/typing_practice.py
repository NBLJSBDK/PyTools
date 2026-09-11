import configparser
import os
import random
import sys

from PyQt5.QtCore import QUrl, QTimer, QTime, QDateTime, Qt
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QComboBox,
    QSpinBox,
    QCheckBox,
)


class BlindTyping(QWidget):
    def __init__(self):
        super().__init__()
        self.settings = self.load_config()
        self.practice_times = self.settings["default_times"]
        self.players = []  # 存储音频播放器对象的列表
        self.encourage_sounds = [os.path.join(os.path.dirname(__file__), 'misc', 'EncourageSound', f"{i}.mp3") for i in
                                 range(1, 15)]  # 修改为14
        self.punishment_sounds = [os.path.join(os.path.dirname(__file__), 'misc', 'PunishmentSound', f"{i}.mp3") for i
                                   in range(1, 4)]
        self.EncourageSound_count = 0  # 初始化奖励声音计数器
        self.PunishmentSound_count = 0  # 初始化惩罚声音计数器
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.elapsed_time = QTime(0, 0)
        self.input_text_started = False  # 标记输入框是否开始输入文字
        self.practice_start_datetime = None
        self.practice_input_method = None
        self.practice_auto_submit = None
        self.input_method = self.settings["default_input_method"]
        self.auto_submit = self.settings["default_auto_submit"]
        self.correct_count = 0
        self.mistake_count = 0
        self.initUI()
        QApplication.instance().applicationStateChanged.connect(self.handle_application_state_changed)

    def initUI(self):
        self.words = self.load_words_from_file()
        if not self.words:
            print("File 'data.txt' contains no words.")
            sys.exit(1)

        self.current_mode = self.settings["default_mode"]
        self.current_word_index = 0
        self.practice_words = []
        self.total_word_count = 0

        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["顺序学习", "乱序巩固", "单次测速"])
        self.mode_combo.setCurrentText(self.current_mode)
        self.practice_times_spin = QSpinBox()
        self.practice_times_spin.setRange(1, 99)
        self.practice_times_spin.setValue(self.practice_times)
        self.practice_times_spin.setSuffix(" 次")
        self.input_method_combo = QComboBox()
        self.input_method_combo.addItems(self.settings["input_methods"])
        self.input_method_combo.setCurrentText(self.input_method)
        self.auto_submit_checkbox = QCheckBox("自动提交")
        self.auto_submit_checkbox.setChecked(self.auto_submit)
        self.prepare_practice_words()

        self.word_label = QLabel()
        self.input_edit = QLineEdit()
        self.count_label = QLabel()
        self.timer_label = QLabel("00:00:00")
        self.restart_button = QPushButton("重新开始")  # 添加重新开始按钮
        self.restart_button.clicked.connect(self.restart_practice)  # 点击按钮时触发重新开始方法

        self.input_edit.textChanged.connect(self.start_timer_if_needed)
        self.input_edit.textChanged.connect(self.auto_submit_if_correct)
        self.input_edit.returnPressed.connect(self.check_input)

        mode_row = QHBoxLayout()
        mode_row.addWidget(QLabel("训练模式"))
        mode_row.addWidget(self.mode_combo)
        mode_row.addWidget(QLabel("次数"))
        mode_row.addWidget(self.practice_times_spin)
        mode_row.addStretch()

        input_row = QHBoxLayout()
        input_row.addWidget(QLabel("输入法"))
        input_row.addWidget(self.input_method_combo)
        input_row.addWidget(self.auto_submit_checkbox)
        input_row.addStretch()

        controls_box = QVBoxLayout()
        controls_box.addLayout(mode_row)
        controls_box.addLayout(input_row)

        hbox = QHBoxLayout()
        hbox.addWidget(self.word_label)
        hbox.addWidget(self.count_label)

        vbox = QVBoxLayout()
        vbox.addLayout(controls_box)
        vbox.addLayout(hbox)
        vbox.addWidget(self.input_edit)
        vbox.addWidget(self.timer_label, alignment=Qt.AlignRight)  # 将计时器标签右对齐
        vbox.addWidget(self.restart_button)  # 添加重新开始按钮到布局

        self.setLayout(vbox)
        self.setWindowTitle('盲打训练')
        self.mode_combo.currentTextChanged.connect(self.change_mode)
        self.practice_times_spin.valueChanged.connect(self.change_practice_times)
        self.input_method_combo.currentTextChanged.connect(self.change_input_method)
        self.auto_submit_checkbox.toggled.connect(self.change_auto_submit)
        self.practice_times_spin.setEnabled(self.current_mode != "单次测速")
        self.update_practice_display()
        self.show()

        # 预加载声音文件
        self.init_players()

        # 播放声音
        self.play_sound(os.path.join(os.path.dirname(__file__), 'misc', 'ready', '卫星图.wav'))

    def init_players(self):
        # 创建多个音频播放器对象
        for _ in range(5):  # 创建5个播放器
            player = QMediaPlayer()
            self.players.append(player)

    def load_config(self):
        default_modes = ["顺序学习", "乱序巩固", "单次测速"]
        default_input_methods = [
            "全拼",
            "英文模式",
            "雾凇拼音",
            "中文九键",
            "自然码双拼",
            "智能ABC双拼",
            "微软双拼",
            "搜狗双拼",
            "小鹤双拼",
            "紫光双拼",
            "拼音加加双拼",
        ]
        filepath = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'config.ini'
        )
        parser = configparser.ConfigParser(interpolation=None)
        parser.optionxform = str

        try:
            parser.read(filepath, encoding='utf-8')
        except (OSError, configparser.Error) as error:
            print(f"Error while reading config.ini: {error}")

        settings = parser["默认设置"] if parser.has_section("默认设置") else {}
        mode = settings.get("default_mode", "顺序学习").strip()
        if mode not in default_modes:
            mode = "顺序学习"

        try:
            practice_times = int(settings.get("default_times", "7"))
        except ValueError:
            practice_times = 7
        practice_times = max(1, min(99, practice_times))

        true_flags = {"1", "true", "yes", "on", "启用", "开启"}
        false_flags = {"0", "false", "no", "off", "禁用", "关闭"}
        auto_submit_value = settings.get("default_auto_submit", "1").strip().lower()
        if auto_submit_value in false_flags:
            default_auto_submit = False
        elif auto_submit_value in true_flags:
            default_auto_submit = True
        else:
            default_auto_submit = True

        input_methods = []
        if parser.has_section("输入法列表"):
            for name, flag in parser["输入法列表"].items():
                if flag.strip().lower() in true_flags and name.strip():
                    input_methods.append(name.strip())
        if not input_methods:
            input_methods = default_input_methods

        input_method = settings.get("default_input_method", "自然码双拼").strip()
        if input_method not in input_methods:
            input_method = input_methods[0]

        return {
            "default_mode": mode,
            "default_times": practice_times,
            "default_input_method": input_method,
            "default_auto_submit": default_auto_submit,
            "input_methods": input_methods,
        }

    def load_words_from_file(self):
        try:
            filepath = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                'data.txt'
            )

            words = []

            with open(filepath, 'r', encoding='utf-8') as file:
                for line in file:
                    # 去掉行内注释
                    line = line.split('#', 1)[0].strip()

                    # 忽略空行和纯注释行
                    if line:
                        words.append(line)

            return words
        except FileNotFoundError:
            print("File 'data.txt' not found.")
            sys.exit(1)

    def prepare_practice_words(self):
        """根据当前模式生成统一的练习题目序列。"""
        if self.current_mode == "顺序学习":
            self.practice_words = [
                word
                for word in self.words
                for _ in range(self.practice_times)
            ]
        elif self.current_mode == "乱序巩固":
            self.practice_words = self.build_random_practice_words()
        else:
            self.practice_words = self.words.copy()

        self.total_word_count = len(self.practice_words)

    def build_random_practice_words(self):
        """随机生成题目，并尽量避免相同词连续出现。"""
        remaining = {}
        for word in self.words:
            remaining[word] = remaining.get(word, 0) + self.practice_times

        practice_words = []
        previous_word = None

        while remaining:
            candidates = [word for word in remaining if word != previous_word]
            if not candidates:
                # 只剩同一个词时无法避免连续，这是不可避免的情况。
                candidates = list(remaining)

            max_remaining = max(remaining[word] for word in candidates)
            candidates = [
                word for word in candidates
                if remaining[word] == max_remaining
            ]
            word = random.choice(candidates)
            practice_words.append(word)
            remaining[word] -= 1
            if remaining[word] == 0:
                del remaining[word]
            previous_word = word

        return practice_words

    def format_word_label(self):
        display_index = self.current_word_index + 1
        if self.current_mode == "顺序学习":
            display_index = self.current_word_index // self.practice_times + 1
        return f"{display_index}.{self.practice_words[self.current_word_index]}"

    def update_practice_display(self):
        if self.current_word_index >= self.total_word_count:
            self.word_label.setText("Practice Finished")
            self.count_label.setText("")
            return

        self.word_label.setText(self.format_word_label())
        if self.current_mode == "顺序学习":
            completed_count = self.current_word_index % self.practice_times
            self.count_label.setText(f"{completed_count}/{self.practice_times}")
        else:
            self.count_label.setText(
                f"{self.current_word_index + 1}/{self.total_word_count}"
            )

    def change_mode(self, mode):
        self.current_mode = mode
        self.practice_times_spin.setEnabled(mode != "单次测速")
        self.restart_practice()

    def change_practice_times(self, value):
        self.practice_times = value
        self.restart_practice()

    def change_input_method(self, method):
        """输入法选项只用于记录，不影响答案判定。"""
        self.input_method = method

    def change_auto_submit(self, checked):
        self.auto_submit = checked

    def check_input(self):
        if not self.input_text_started:
            return
        if self.current_word_index >= self.total_word_count:
            return

        input_text = self.input_edit.text()
        if input_text == self.practice_words[self.current_word_index]:
            self.correct_count += 1
            self.current_word_index += 1
            self.play_encourage_sound()

            if self.current_word_index == self.total_word_count:
                self.word_label.setText("Practice Finished")
                self.input_edit.setDisabled(True)
                self.count_label.setText("")
                self.timer.stop()  # 停止计时器

                # 保存最后记录的时间到achievement.txt文件中
                self.save_achievement()

            else:
                self.update_practice_display()
        else:
            # 播放惩罚声音
            self.mistake_count += 1
            self.play_punishment_sound()
            self.EncourageSound_count = 0
        self.input_edit.clear()
        self.input_edit.setFocus()

    def auto_submit_if_correct(self, text):
        if (self.auto_submit
                and self.input_text_started
                and self.current_word_index < self.total_word_count
                and text == self.practice_words[self.current_word_index]):
            self.check_input()

    def start_timer_if_needed(self, text):
        if not self.input_text_started and text:
            self.practice_start_datetime = QDateTime.currentDateTime()
            self.practice_input_method = self.input_method_combo.currentText()
            self.practice_auto_submit = self.auto_submit_checkbox.isChecked()
            self.timer.start(10)  # 在输入第一个字符后开始计时，每10毫秒更新一次
            self.input_text_started = True

    def handle_application_state_changed(self, state):
        """窗口失去前台时暂停计时，重新获得前台时继续计时。"""
        if state == Qt.ApplicationActive:
            if (self.input_text_started
                    and self.current_word_index < self.total_word_count
                    and not self.timer.isActive()):
                self.timer.start(10)
        elif self.timer.isActive():
            self.timer.stop()

    def update_timer(self):
        self.elapsed_time = self.elapsed_time.addMSecs(10)  # 每10毫秒加10毫秒
        self.timer_label.setText(self.elapsed_time.toString("mm:ss:zzz"))  # 更新计时器标签

    def restart_practice(self):
        # 重新开始练习，重置所有参数
        self.play_sound(os.path.join(os.path.dirname(__file__), 'misc', 'ready', '卫星图.wav'))
        self.current_mode = self.mode_combo.currentText()
        self.prepare_practice_words()
        self.current_word_index = 0
        self.EncourageSound_count = 0
        self.elapsed_time = QTime(0, 0)
        self.input_text_started = False
        self.practice_start_datetime = None
        self.practice_input_method = None
        self.practice_auto_submit = None
        self.correct_count = 0
        self.mistake_count = 0
        self.timer.stop()  # 停止计时器
        self.input_edit.setEnabled(True)
        self.input_edit.clear()
        self.update_practice_display()
        self.timer_label.setText("00:00:00")

    # 暂时关闭“练习未完成时禁止关闭窗口”功能；以后需要时取消下面注释即可恢复。
    # def closeEvent(self, event):
    #     if self.current_word_index == self.total_word_count:
    #         event.accept()
    #     else:
    #         self.restart_practice()
    #         event.ignore()

    def save_achievement(self):
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            end_datetime = QDateTime.currentDateTime()
            start_datetime = self.practice_start_datetime or end_datetime
            input_method = self.practice_input_method or self.input_method_combo.currentText()
            auto_submit = self.practice_auto_submit
            if auto_submit is None:
                auto_submit = self.auto_submit_checkbox.isChecked()
            auto_submit_text = "是" if auto_submit else "否"
            elapsed = self.elapsed_time.toString('mm:ss:zzz')
            repeat_count = (
                str(self.practice_times)
                if self.current_mode != "单次测速"
                else "不适用"
            )
            total_attempts = self.correct_count + self.mistake_count
            accuracy = (
                self.correct_count / total_attempts * 100
                if total_attempts
                else 0
            )
            start_text = start_datetime.toString("yyyy-MM-dd HH:mm:ss.zzz")
            end_text = end_datetime.toString("yyyy-MM-dd HH:mm:ss.zzz")
            end_short_text = end_datetime.toString("yyyy-M-d h:mm:ss")

            achievement_line = (
                f"模式={self.current_mode} 输入法={input_method} "
                f"自动提交={auto_submit_text} "
                f"重复次数={repeat_count} 记录={elapsed} "
                f"产生时间={end_short_text}\n"
            )
            log_line = (
                f"开始={start_text} 结束={end_text} 数据文件=data.txt "
                f"输入法={input_method} 自动提交={auto_submit_text} "
                f"模式={self.current_mode} "
                f"重复次数={repeat_count} 词表词数={len(self.words)} "
                f"总题数={self.total_word_count} 正确={self.correct_count} "
                f"错误={self.mistake_count} 尝试={total_attempts} "
                f"正确率={accuracy:.1f}% 用时={elapsed}\n"
            )

            with open(os.path.join(base_dir, 'achievement.txt'), 'a', encoding='utf-8') as file:
                file.write(achievement_line)
            with open(os.path.join(base_dir, 'typing_log.txt'), 'a', encoding='utf-8') as file:
                file.write(log_line)
        except Exception as e:
            print(f"Error while saving achievement: {e}")

    def play_sound(self, filepath):
        # 从已创建的播放器列表中选择一个空闲的播放器进行播放
        for player in self.players:
            if player.state() == QMediaPlayer.StoppedState:
                media_content = QMediaContent(QUrl.fromLocalFile(filepath))
                player.setMedia(media_content)
                player.play()
                break

    def play_encourage_sound(self):
        sound_count = self.EncourageSound_count % len(self.encourage_sounds)  # 修改这里
        filepath = self.encourage_sounds[sound_count]
        self.play_sound(filepath)
        self.EncourageSound_count += 1

    def play_punishment_sound(self):
        sound_count = self.PunishmentSound_count % 3  # 3是惩罚声音文件的总数
        filepath = self.punishment_sounds[sound_count]
        self.play_sound(filepath)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = BlindTyping()
    sys.exit(app.exec_())
