from core.timer.cow_timer import   CowTimer
from core.timer.slide_timer import SlideTimer
from core.timer.normal_timer import NormalTimer


class ModeManager:
    def __init__(self, parent):
        self.parent = parent
        self.mode = "normal"

        # 创建不同模式的计时器实例
        self.timers = {
            "normal": NormalTimer,
            "slide": SlideTimer,
            "cow": CowTimer
        }
        self.current_timer = self.timers["normal"](self.parent)

    def set_mode(self, mode):
        if mode not in self.timers:
            raise ValueError(f"不支持的模式: {mode}")
        if mode == self.mode:
            return

        # 完全停止当前计时器
        self.current_timer.reset()

        # 切换到新计时器
        self.mode = mode
        self.current_timer = self.timers[mode](self.parent)

        # 重置显示
        self.parent.update_display(0)


    def get_current_timer(self):
        return self.current_timer

    def get_mode(self):
        return self.mode
