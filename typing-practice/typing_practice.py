import csv
import configparser
from functools import cmp_to_key
import os
import random
import statistics
import sys
import time
from datetime import datetime

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
    QMessageBox,
)


class BlindTyping(QWidget):
    STALL_FACTOR = 2.0
    TOP_N = 10

    def __init__(self):
        super().__init__()
        self.settings = self.load_config()
        self.practice_times = self.settings["default_times"]
        self.dict_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "dict",
        )
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
        self.current_word_file = self.settings["default_word_file"]
        self.correct_count = 0
        self.mistake_count = 0
        self.correct_character_count = 0
        self.input_character_count = 0
        self.session_id = None
        self.session_records = []
        self.question_shown_at = None
        self.correct_submit_at = None
        self.question_shown_datetime = None
        self.current_question_attempts = 0
        self.current_question_errors = 0
        self.detail_log_saved = False
        self.initUI()
        QApplication.instance().applicationStateChanged.connect(self.handle_application_state_changed)

    def initUI(self):
        self.word_files = self.list_word_files()
        if not self.word_files:
            self.report_word_file_error(
                f"词表目录不存在或没有 .txt 文件：{self.dict_dir}"
            )
            sys.exit(1)

        if self.current_word_file not in self.word_files:
            self.report_word_file_error(
                f"配置中的词表不存在：{self.current_word_file}"
            )
            self.current_word_file = self.word_files[0]

        self.words = self.load_words_from_file(self.current_word_file)
        if not self.words:
            self.report_word_file_error(
                f"词表没有可训练内容：{self.current_word_file}"
            )
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
        self.word_file_combo = QComboBox()
        self.word_file_combo.addItems(self.word_files)
        self.word_file_combo.setCurrentText(self.current_word_file)
        self.input_method_combo = QComboBox()
        self.input_method_combo.addItems(self.settings["input_methods"])
        self.input_method_combo.setCurrentText(self.input_method)
        self.auto_submit_checkbox = QCheckBox("自动提交")
        self.auto_submit_checkbox.setChecked(self.auto_submit)
        self.prepare_practice_words()
        self.start_new_session()

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

        word_file_row = QHBoxLayout()
        word_file_row.addWidget(QLabel("词表"))
        word_file_row.addWidget(self.word_file_combo)
        word_file_row.addStretch()

        input_row = QHBoxLayout()
        input_row.addWidget(QLabel("输入法"))
        input_row.addWidget(self.input_method_combo)
        input_row.addWidget(self.auto_submit_checkbox)
        input_row.addStretch()

        controls_box = QVBoxLayout()
        controls_box.addLayout(word_file_row)
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
        self.word_file_combo.currentTextChanged.connect(self.change_word_file)
        self.input_method_combo.currentTextChanged.connect(self.change_input_method)
        self.auto_submit_checkbox.toggled.connect(self.change_auto_submit)
        self.practice_times_spin.setEnabled(self.current_mode != "单次测速")
        self.update_practice_display()
        self.show()

        # 预加载声音文件
        self.init_players()

        # 播放声音
        self.play_sound(os.path.join(os.path.dirname(__file__), 'misc', 'ready', '卫星图.wav'))

    def start_new_session(self):
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_records = []
        self.question_shown_at = None
        self.correct_submit_at = None
        self.question_shown_datetime = None
        self.current_question_attempts = 0
        self.current_question_errors = 0
        self.detail_log_saved = False

    @staticmethod
    def format_timestamp(value):
        return value.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

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
        word_file = settings.get("default_word_file", "data.txt").strip()
        if not word_file:
            word_file = "data.txt"

        return {
            "default_mode": mode,
            "default_times": practice_times,
            "default_input_method": input_method,
            "default_auto_submit": default_auto_submit,
            "default_word_file": word_file,
            "input_methods": input_methods,
        }

    @staticmethod
    def natural_compare(left, right):
        left_index = 0
        right_index = 0

        while left_index < len(left) and right_index < len(right):
            left_char = left[left_index]
            right_char = right[right_index]
            left_is_digit = left_char.isdigit()
            right_is_digit = right_char.isdigit()

            if left_is_digit and right_is_digit:
                left_end = left_index
                right_end = right_index
                while left_end < len(left) and left[left_end].isdigit():
                    left_end += 1
                while right_end < len(right) and right[right_end].isdigit():
                    right_end += 1

                left_number = int(left[left_index:left_end])
                right_number = int(right[right_index:right_end])
                if left_number != right_number:
                    return -1 if left_number < right_number else 1
                left_index = left_end
                right_index = right_end
                continue

            if left_is_digit != right_is_digit:
                return 1 if left_is_digit else -1

            left_folded = left_char.casefold()
            right_folded = right_char.casefold()
            if left_folded != right_folded:
                return -1 if left_folded < right_folded else 1
            left_index += 1
            right_index += 1

        if len(left) != len(right):
            return -1 if len(left) < len(right) else 1
        if left == right:
            return 0
        return -1 if left < right else 1

    def list_word_files(self):
        try:
            filenames = [
                entry.name
                for entry in os.scandir(self.dict_dir)
                if entry.is_file() and entry.name.lower().endswith(".txt")
            ]
        except OSError as error:
            print(f"Error while reading word list directory: {error}")
            return []
        return sorted(filenames, key=cmp_to_key(self.natural_compare))

    def get_word_file_path(self, filename):
        if not filename or os.path.basename(filename) != filename:
            return None
        return os.path.join(self.dict_dir, filename)

    def report_word_file_error(self, message):
        print(message)
        QMessageBox.critical(self, "词表错误", message)

    def load_words_from_file(self, filename):
        filepath = self.get_word_file_path(filename)
        if filepath is None:
            return []

        words = []
        try:
            with open(filepath, "r", encoding="utf-8") as file:
                for line in file:
                    # 去掉行内注释
                    line = line.split("#", 1)[0].strip()

                    # 忽略空行和纯注释行
                    if line:
                        words.append(line)
        except FileNotFoundError:
            return []
        return words

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
        self.target_character_count = sum(
            len(word) for word in self.practice_words
        )

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
            self.question_shown_at = None
            self.question_shown_datetime = None
            self.word_label.setText("Practice Finished")
            self.count_label.setText("")
            return

        self.word_label.setText(self.format_word_label())
        self.question_shown_at = time.perf_counter()
        self.question_shown_datetime = datetime.now()
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

    def change_word_file(self, filename):
        filepath = self.get_word_file_path(filename)
        if filepath is None or not os.path.isfile(filepath):
            self.report_word_file_error(f"选择的词表不存在：{filename}")
            self.word_file_combo.blockSignals(True)
            self.word_file_combo.setCurrentText(self.current_word_file)
            self.word_file_combo.blockSignals(False)
            return

        words = self.load_words_from_file(filename)
        if not words:
            self.report_word_file_error(f"选择的词表没有可训练内容：{filename}")
            self.word_file_combo.blockSignals(True)
            self.word_file_combo.setCurrentText(self.current_word_file)
            self.word_file_combo.blockSignals(False)
            return

        self.current_word_file = filename
        self.words = words
        self.restart_practice()

    def change_practice_times(self, value):
        self.practice_times = value
        self.restart_practice()

    def change_input_method(self, method):
        """输入法选项只用于记录，不影响答案判定。"""
        self.input_method = method

    def change_auto_submit(self, checked):
        self.auto_submit = checked

    def save_config(self):
        filepath = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "config.ini",
        )
        values = {
            "default_mode": self.mode_combo.currentText(),
            "default_times": str(self.practice_times_spin.value()),
            "default_input_method": self.input_method_combo.currentText(),
            "default_word_file": self.current_word_file,
            "default_auto_submit": (
                "1" if self.auto_submit_checkbox.isChecked() else "0"
            ),
        }

        try:
            with open(filepath, "r", encoding="utf-8") as file:
                lines = file.readlines()

            section = None
            updated = set()
            output = []
            for line in lines:
                stripped = line.strip()
                if stripped.startswith("[") and stripped.endswith("]"):
                    section = stripped[1:-1].strip()

                if section == "默认设置" and "=" in line and not stripped.startswith("#"):
                    key = line.split("=", 1)[0].strip()
                    if key in values:
                        newline = "\n" if line.endswith("\n") else ""
                        output.append(f"{key} = {values[key]}{newline}")
                        updated.add(key)
                        continue
                output.append(line)

            missing = [key for key in values if key not in updated]
            if missing:
                raise ValueError(f"config.ini 缺少默认设置: {', '.join(missing)}")

            with open(filepath, "w", encoding="utf-8") as file:
                file.writelines(output)
        except (OSError, ValueError) as error:
            print(f"Error while saving config.ini: {error}")

    def check_input(self):
        if self.current_word_index >= self.total_word_count:
            return

        input_text = self.input_edit.text()
        if not input_text.strip():
            self.input_edit.clear()
            self.input_edit.setFocus()
            return
        if not self.input_text_started:
            return

        question_index = self.current_word_index
        question_text = self.practice_words[question_index]
        self.current_question_attempts += 1
        self.input_character_count += len(input_text)
        if input_text == question_text:
            self.correct_count += 1
            self.correct_character_count += len(input_text)
            self.correct_submit_at = time.perf_counter()
            correct_submit_at = self.correct_submit_at
            correct_submit_datetime = datetime.now()
            shown_at = self.question_shown_at or correct_submit_at
            shown_datetime = self.question_shown_datetime or correct_submit_datetime
            duration_seconds = max(0.0, correct_submit_at - shown_at)
            self.session_records.append({
                "session_id": self.session_id,
                "index": question_index + 1,
                "text": question_text,
                "shown_at": self.format_timestamp(shown_datetime),
                "submitted_at": self.format_timestamp(correct_submit_datetime),
                "duration_seconds": duration_seconds,
                "duration_ms": round(duration_seconds * 1000, 3),
                "error_attempts": self.current_question_errors,
                "attempts": self.current_question_attempts,
                "first_try_correct": self.current_question_attempts == 1,
            })
            self.current_word_index += 1
            self.play_encourage_sound()
            self.current_question_attempts = 0
            self.current_question_errors = 0

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
            self.current_question_errors += 1
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
        if not self.input_text_started and text.strip():
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
        self.start_new_session()
        self.current_word_index = 0
        self.EncourageSound_count = 0
        self.elapsed_time = QTime(0, 0)
        self.input_text_started = False
        self.practice_start_datetime = None
        self.practice_input_method = None
        self.practice_auto_submit = None
        self.correct_count = 0
        self.mistake_count = 0
        self.correct_character_count = 0
        self.input_character_count = 0
        self.timer.stop()  # 停止计时器
        self.input_edit.setEnabled(True)
        self.input_edit.clear()
        self.update_practice_display()
        self.timer_label.setText("00:00:00")

    def closeEvent(self, event):
        self.save_config()
        event.accept()

    @staticmethod
    def percentile(values, percentage):
        if not values:
            return 0.0

        ordered = sorted(values)
        position = (len(ordered) - 1) * percentage / 100
        lower_index = int(position)
        upper_index = min(lower_index + 1, len(ordered) - 1)
        fraction = position - lower_index
        return ordered[lower_index] + (
            ordered[upper_index] - ordered[lower_index]
        ) * fraction

    def calculate_session_statistics(self):
        durations = [record["duration_seconds"] for record in self.session_records]
        if not durations:
            return {
                "count": 0,
                "average": 0.0,
                "median": 0.0,
                "p90": 0.0,
                "p95": 0.0,
                "maximum": 0.0,
                "stall_threshold": 0.0,
                "stall_count": 0,
                "first_try_correct_count": 0,
                "first_try_correct_rate": 0.0,
                "slow_questions": [],
                "slow_words": [],
            }

        median = statistics.median(durations)
        stall_threshold = median * self.STALL_FACTOR
        grouped_by_word = {}
        for record in self.session_records:
            grouped_by_word.setdefault(record["text"], []).append(record)

        slow_words = []
        for text, records in grouped_by_word.items():
            word_durations = [record["duration_seconds"] for record in records]
            slow_words.append({
                "text": text,
                "count": len(records),
                "average": statistics.mean(word_durations),
                "median": statistics.median(word_durations),
                "fastest": min(word_durations),
                "slowest": max(word_durations),
                "stall_count": sum(
                    duration > stall_threshold for duration in word_durations
                ),
            })

        slow_words.sort(
            key=lambda item: (item["average"], item["slowest"]),
            reverse=True,
        )
        first_try_correct_count = sum(
            record["first_try_correct"] for record in self.session_records
        )
        return {
            "count": len(durations),
            "average": statistics.mean(durations),
            "median": median,
            "p90": self.percentile(durations, 90),
            "p95": self.percentile(durations, 95),
            "maximum": max(durations),
            "stall_threshold": stall_threshold,
            "stall_count": sum(duration > stall_threshold for duration in durations),
            "first_try_correct_count": first_try_correct_count,
            "first_try_correct_rate": (
                first_try_correct_count / len(durations) * 100
            ),
            "slow_questions": sorted(
                self.session_records,
                key=lambda record: record["duration_seconds"],
                reverse=True,
            )[:self.TOP_N],
            "slow_words": slow_words[:self.TOP_N],
        }

    @staticmethod
    def format_slow_questions(records):
        if not records:
            return "无"
        return "|".join(
            f"{record['index']}.{record['text']}:{record['duration_seconds']:.3f}s"
            for record in records
        )

    @staticmethod
    def format_slow_words(records):
        if not records:
            return "无"
        return "|".join(
            f"{record['text']}:平均={record['average']:.3f}s,"
            f"中位数={record['median']:.3f}s,"
            f"最快={record['fastest']:.3f}s,"
            f"最慢={record['slowest']:.3f}s,"
            f"卡顿={record['stall_count']}"
            for record in records
        )

    def append_detail_log(self, base_dir):
        if not self.session_records or self.detail_log_saved:
            return

        detail_path = os.path.join(base_dir, "typing_detail_log.csv")
        fieldnames = [
            "session_id",
            "index",
            "text",
            "shown_at",
            "submitted_at",
            "duration_ms",
            "error_attempts",
            "attempts",
            "first_try_correct",
        ]
        has_header = os.path.exists(detail_path) and os.path.getsize(detail_path) > 0
        with open(detail_path, "a", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            if not has_header:
                writer.writeheader()
            for record in self.session_records:
                writer.writerow({
                    "session_id": record["session_id"],
                    "index": record["index"],
                    "text": record["text"],
                    "shown_at": record["shown_at"],
                    "submitted_at": record["submitted_at"],
                    "duration_ms": f"{record['duration_ms']:.3f}",
                    "error_attempts": record["error_attempts"],
                    "attempts": record["attempts"],
                    "first_try_correct": int(record["first_try_correct"]),
                })
        self.detail_log_saved = True

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
            elapsed_milliseconds = self.elapsed_time.msecsSinceStartOfDay()
            elapsed_minutes = elapsed_milliseconds / 60000
            characters_per_minute = (
                self.input_character_count / elapsed_minutes
                if elapsed_minutes > 0
                else 0
            )
            session_stats = self.calculate_session_statistics()
            slow_questions = self.format_slow_questions(
                session_stats["slow_questions"]
            )
            slow_words = self.format_slow_words(session_stats["slow_words"])
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
                f"字数={self.target_character_count} "
                f"实际提交字数={self.input_character_count} "
                f"正确字数={self.correct_character_count} "
                f"每分钟输入字数={characters_per_minute:.1f} "
                f"提交间隔平均={session_stats['average']:.3f}s "
                f"提交间隔中位数={session_stats['median']:.3f}s "
                f"提交间隔P90={session_stats['p90']:.3f}s "
                f"提交间隔P95={session_stats['p95']:.3f}s "
                f"提交间隔最大={session_stats['maximum']:.3f}s "
                f"卡顿阈值={session_stats['stall_threshold']:.3f}s "
                f"卡顿次数={session_stats['stall_count']} "
                f"产生时间={end_short_text}\n"
            )
            log_line = (
                f"开始={start_text} 结束={end_text} 数据文件={self.current_word_file} "
                f"输入法={input_method} 自动提交={auto_submit_text} "
                f"模式={self.current_mode} "
                f"重复次数={repeat_count} 词表词数={len(self.words)} "
                f"总题数={self.total_word_count} 字数={self.target_character_count} "
                f"实际提交字数={self.input_character_count} "
                f"正确字数={self.correct_character_count} "
                f"每分钟输入字数={characters_per_minute:.1f} "
                f"正确={self.correct_count} "
                f"错误={self.mistake_count} 尝试={total_attempts} "
                f"正确率={accuracy:.1f}% 用时={elapsed} "
                f"会话ID={self.session_id} "
                f"提交间隔平均={session_stats['average']:.3f}s "
                f"提交间隔中位数={session_stats['median']:.3f}s "
                f"提交间隔P90={session_stats['p90']:.3f}s "
                f"提交间隔P95={session_stats['p95']:.3f}s "
                f"提交间隔最大={session_stats['maximum']:.3f}s "
                f"卡顿阈值={session_stats['stall_threshold']:.3f}s "
                f"卡顿次数={session_stats['stall_count']} "
                f"首次正确题数={session_stats['first_try_correct_count']} "
                f"首次正确率={session_stats['first_try_correct_rate']:.1f}% "
                f"最慢题目TOP10={slow_questions} "
                f"最慢词平均TOP10={slow_words}"
                f"\n"
            )

            with open(os.path.join(base_dir, 'achievement.txt'), 'a', encoding='utf-8') as file:
                file.write(achievement_line)
            with open(os.path.join(base_dir, 'typing_log.txt'), 'a', encoding='utf-8') as file:
                file.write(log_line)
            self.append_detail_log(base_dir)
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
