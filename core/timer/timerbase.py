from abc import ABC, abstractmethod


class TimerBase(ABC):
    """计时器基类，定义统一接口"""

    def __init__(self, parent):
        self.parent = parent
        self.total_seconds = 0
        self.remaining = 0
        self.is_running = False

    @abstractmethod
    def start_countdown(self, minutes=None):
        """开始倒计时"""
        pass

    @abstractmethod
    def update_countdown(self):
        """更新倒计时"""
        pass

    @abstractmethod
    def reset(self):
        """重置计时器"""
        pass

    @abstractmethod
    def get_status_text(self):
        """获取状态文本"""
        pass

    def get_formatted_time(self):
        """获取格式化时间显示"""
        if self.remaining <= 0:
            return "00:00"
        minutes, seconds = divmod(self.remaining, 60)
        return f"{minutes:02d}:{seconds:02d}"
