import win32api
from PyQt5.QtCore import QTimer

from core.timer.timerbase import TimerBase
from config.settings import APP_CONFIG

class NormalTimer(TimerBase):
    """常规倒计时类"""

    def __init__(self, parent):
        super().__init__(parent)
        self.timer = QTimer(parent)
        self.timer.timeout.connect(self.update_countdown)
        self.note= False

    def start_countdown(self, minutes=None):
        self.total_seconds = minutes * 60
        self.remaining = self.total_seconds
        self.is_running = True
        self.parent.update_display(self.remaining)
        self.timer.start(1000)

    def update_countdown(self):
        if self.remaining <= 0:
            self.timer.stop()
            self.is_running = False
            self.remaining = 0
            self.parent.update_display(self.remaining)
            self.parent.flash_alert()
        else:
            self.remaining -= 1
            self.parent.update_display(self.remaining)
            print( self.remaining)
            print(APP_CONFIG.WARNING_THRESHOLD)
            if self.note and self.remaining ==  APP_CONFIG.WARNING_THRESHOLD:
                minutes = self.remaining // 60
                remaining_sec = self.remaining % 60
                win32api.MessageBox(0, f'剩余时间： {minutes}分{remaining_sec}秒', '提醒', 0)

    def reset(self):
        print(self.timer)
        self.timer.stop()
        self.is_running = False
        self.remaining = 0
        self.total_seconds = 0

    def get_status_text(self):
        return "normal"
