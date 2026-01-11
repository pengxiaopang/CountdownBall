import win32api
from PyQt5.QtCore import QTimer
from core.timer.timerbase import TimerBase
from config.settings import APP_CONFIG
import datetime
from datetime import datetime


class CowTimer(TimerBase):
    """牛马模式计时类"""

    def __init__(self, parent):
        super().__init__(parent)
        self.cow_timer = QTimer(parent)
        self.lunch_time = None
        self.off_time = None
        self.income_per_second = 0

        self.get_cow_income()
        self.start_countdown()
        # 控制两种子模式切换
        self.time_or_income= True
        if self.time_or_income:
            self.cow_timer.timeout.connect(self.update_countdown)
        else:
            self.cow_timer.timeout.connect(self.update_income_display)

    def start_countdown(self, minutes=None):
        now = datetime.now()
        week_number = now.isocalendar()[1]
        self.lunch_time = APP_CONFIG.COW_MODE_ODD_WEEK_LUNCH_TIME if week_number % 2 == 1 else APP_CONFIG.COW_MODE_EVEN_WEEK_LUNCH_TIME
        self.off_time = APP_CONFIG.COW_MODE_AFTERNOON_OFF_TIME

        self.is_running = True
        self.update_countdown()
        self.cow_timer.start(1000)

    def update_countdown(self):
        remaining, tip_type = self.get_cow_countdown()
        self.total_seconds = remaining
        self.remaining = remaining
        self.is_running = True
        if remaining == 0:
            self.parent.time_label.setText("00:00")
            win32api.MessageBox(0, tip_type, '我爱工作！', 0x00040000)
        elif remaining > 0:
            m, s = divmod(remaining, 60)
            self.parent.time_label.setText(f"{m:02d}:{s:02d}")
        else:
            self.parent.time_label.setText("下班")

        self.parent.update()

    def get_cow_countdown(self):
        now = datetime.now()
        current_time = now.time()
        if current_time < self.lunch_time:
            target_dt = datetime.combine(now.date(), self.lunch_time)
            delta = target_dt - now
            return max(0, int(delta.total_seconds())), "干饭第一！"
        elif current_time < self.off_time:
            target_dt = datetime.combine(now.date(), self.off_time)
            delta = target_dt - now
            return max(0, int(delta.total_seconds())), "再加会吧，公司招你亏麻了！"
        else:
            return -1, "已下班"

    def reset(self):
        print(self.cow_timer)
        self.cow_timer.stop()
        self.is_running = False
        self.remaining = 0
        self.total_seconds = 0

    def get_status_text(self):
        return "cow"

    def get_cow_income(self):

        # 将 time 转换为 datetime，用于计算时间差
        now_date = datetime.now().date()
        start_dt = datetime.combine(now_date,APP_CONFIG.COW_MODE_MOONING_ON_TIME)
        end_dt = datetime.combine(now_date, APP_CONFIG.COW_MODE_AFTERNOON_OFF_TIME)

        # 计算每日工作时长（秒）
        work_duration = end_dt - start_dt
        work_seconds_per_day = int(work_duration.total_seconds())
        # 计算每秒收入
        secondly_income = APP_CONFIG.INCOME_PER_MONTH / (
                APP_CONFIG.WORKING_DAYS_PER_MONTH * work_seconds_per_day
        )
        self.income_per_second = secondly_income

    # 将数字转换为下标形式
    @staticmethod
    def to_subscript(num):
        subscript_map = {
            '0': '₀', '1': '₁', '2': '₂', '3': '₃', '4': '₄',
            '5': '₅', '6': '₆', '7': '₇', '8': '₈', '9': '₉'
        }
        return ''.join(subscript_map.get(d, d) for d in num)

    def update_income_display(self):
        """每秒更新实时收入显示"""
        now = datetime.now()
        work_start_time = datetime.combine(now.date(), APP_CONFIG.COW_MODE_MOONING_ON_TIME)
        work_end_time = datetime.combine(now.date(), APP_CONFIG.COW_MODE_AFTERNOON_OFF_TIME)

        today_work_seconds = 0
        if  work_start_time<= now <= work_end_time:
            elapsed = now - work_start_time
            today_work_seconds = int(elapsed.total_seconds())
        else:
            today_work_seconds = int((work_end_time - work_start_time).total_seconds())

        current_income = f'{today_work_seconds * self.income_per_second:.2f}'

        yuan_part=str(current_income).split(".")[0]
        fen_part=str(current_income).split(".")[1]
        current_income_value=f'{yuan_part}.{self.to_subscript(fen_part)}'

        self.parent.time_label.setText(f"{current_income_value}")

