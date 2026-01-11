from PyQt5.QtCore import QTimer
from core.timer.timerbase import TimerBase
from config.settings import APP_CONFIG


class SlideTimer(TimerBase):
    """PPT模式计时类"""

    def __init__(self, parent):
        super().__init__(parent)
        self.slideshow_pid = None
        self.check_ppt_timer = QTimer(parent)
        self.start_countdown()
        self.check_ppt_timer.timeout.connect(self.update_countdown)

    def start_countdown(self, minutes=None):
        self.reload()
        self.is_running = True
        self.check_ppt_timer.start(1000)


    def update_countdown(self):
        from core.system.powerpoint import get_powerpoint_slide_pid
        current_pid = get_powerpoint_slide_pid()

        if current_pid and not self.slideshow_pid:
            print(f"[进入幻灯片放映] 检测到幻灯片播放 → 启动倒计时 ({APP_CONFIG.SLIDE_MODE_DEFAULT_DURATION} 分钟)")
            self.slideshow_pid = current_pid
            self.is_running = True
        elif not current_pid and self.slideshow_pid:
            print("[退出幻灯片放映] → 重置倒计时")
            self.reload()
            self.slideshow_pid = None
            self.is_running = False

        elif not current_pid and not self.slideshow_pid:
            self.reload()
            self.is_running = False

        # 只有在运行状态下才减少时间
        if self.is_running:
            if self.remaining == 0:
                self.parent.flash_alert()
            self.remaining -= 1
            self.parent.update_display(self.remaining)

    def reload(self):
        self.total_seconds = APP_CONFIG.SLIDE_MODE_DEFAULT_DURATION * 60
        self.remaining = self.total_seconds
        self.parent.update_display(self.remaining)


    def reset(self):
        self.check_ppt_timer.stop()
        self.is_running = False
        self.remaining = 0
        self.total_seconds = 0
        self.slideshow_pid = None

    def get_status_text(self):
        return "slide"
