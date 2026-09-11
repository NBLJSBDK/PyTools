import os
import sys

from PyQt5.QtCore import QUrl, QTimer, QTime, QDateTime, Qt
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton


class BlindTyping(QWidget):
    def __init__(self):
        super().__init__()
        self.practice_times = 7
        self.players = []  # 存储音频播放器对象的列表
        self.encourage_sounds = [os.path.join(os.path.dirname(__file__), 'misc', 'EncourageSound', f"{i}.mp3") for i in
                                 range(1, 15)]  # 修改为14
        self.punishment_sounds = [os.path.join(os.path.dirname(__file__), 'misc', 'PunishmentSound', f"{i}.mp3") for i
                                  in range(1, 4)]
        self.initUI()
        self.EncourageSound_count = 0  # 初始化奖励声音计数器
        self.PunishmentSound_count = 0  # 初始化惩罚声音计数器
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.elapsed_time = QTime(0, 0)
        self.input_text_started = False  # 标记输入框是否开始输入文字

    def initUI(self):
        self.words = self.load_words_from_file()
        self.current_word_index = 0
        self.current_word_count = 0
        self.total_word_count = len(self.words)

        self.word_label = QLabel(self.format_word_label())
        self.input_edit = QLineEdit()
        self.count_label = QLabel(f"{self.current_word_count}/{self.practice_times}")
        self.timer_label = QLabel("00:00:00")
        self.restart_button = QPushButton("重新开始")  # 添加重新开始按钮
        self.restart_button.clicked.connect(self.restart_practice)  # 点击按钮时触发重新开始方法

        self.input_edit.textChanged.connect(self.start_timer_if_needed)
        self.input_edit.returnPressed.connect(self.check_input)

        hbox = QHBoxLayout()
        hbox.addWidget(self.word_label)
        hbox.addWidget(self.count_label)

        vbox = QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addWidget(self.input_edit)
        vbox.addWidget(self.timer_label, alignment=Qt.AlignRight)  # 将计时器标签右对齐
        vbox.addWidget(self.restart_button)  # 添加重新开始按钮到布局

        self.setLayout(vbox)
        self.setWindowTitle('Blind Typing Practice')
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

    def load_words_from_file(self):
        try:
            with open('data.txt', 'r') as file:
                words = file.read().splitlines()[1:]  # Ignore the first line (comment)
            return words
        except FileNotFoundError:
            print("File 'data.txt' not found.")
            sys.exit(1)

    def format_word_label(self):
        return f"{self.current_word_index + 1}.{self.words[self.current_word_index]}"

    def check_input(self):
        if not self.input_text_started:
            return

        input_text = self.input_edit.text()
        if input_text == self.words[self.current_word_index]:
            self.current_word_count += 1
            if self.current_word_count == self.practice_times:
                self.current_word_index += 1
                self.current_word_count = 0
            if self.current_word_index == self.total_word_count:
                self.word_label.setText("Practice Finished")
                self.input_edit.setDisabled(True)
                self.count_label.setText("")
                self.timer.stop()  # 停止计时器

                # 保存最后记录的时间到achievement.txt文件中
                self.save_achievement()

            else:
                self.word_label.setText(self.format_word_label())
                self.count_label.setText(f"{self.current_word_count}/{self.practice_times}")
            # 播放奖励声音
            self.play_encourage_sound()
        else:
            # 播放惩罚声音
            self.play_punishment_sound()
            self.EncourageSound_count = 0
        self.input_edit.clear()
        self.input_edit.setFocus()

    def start_timer_if_needed(self, text):
        if not self.input_text_started and text:
            self.timer.start(10)  # 在输入第一个字符后开始计时，每10毫秒更新一次
            self.input_text_started = True

    def update_timer(self):
        self.elapsed_time = self.elapsed_time.addMSecs(10)  # 每10毫秒加10毫秒
        self.timer_label.setText(self.elapsed_time.toString("mm:ss:zzz"))  # 更新计时器标签

    def restart_practice(self):
        # 重新开始练习，重置所有参数
        self.play_sound(os.path.join(os.path.dirname(__file__), 'misc', 'ready', '卫星图.wav'))
        self.current_word_index = 0
        self.current_word_count = 0
        self.EncourageSound_count = 0
        self.elapsed_time = QTime(0, 0)
        self.input_edit.setEnabled(True)
        self.input_edit.clear()
        self.word_label.setText(self.format_word_label())
        self.count_label.setText(f"{self.current_word_count}/{self.practice_times}")
        self.timer_label.setText("00:00:00")
        self.input_text_started = False
        self.timer.stop()  # 停止计时器

    def closeEvent(self, event):
        if self.current_word_index == self.total_word_count:
            event.accept()  # 如果当前练习完成，接受关闭事件，退出程序
        else:
            self.restart_practice()
            event.ignore()

    def save_achievement(self):
        try:
            # 获取当前时间
            current_datetime = QDateTime.currentDateTime().toString("yyyy-M-d h:mm:ss")

            # 将最后记录的时间和产生的时间添加到achievement.txt文件中
            with open('achievement.txt', 'a') as file:
                file.write(f"记录{self.elapsed_time.toString('mm:ss:zzz')} 产生时间{current_datetime}\n")
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
