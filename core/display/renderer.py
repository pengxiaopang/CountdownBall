import math
from PyQt5.QtCore import QTimer, Qt, QRect
from PyQt5.QtGui import QPainter, QRadialGradient, QPen, QColor

from config.settings import APP_CONFIG


class TimerRenderer:
    def __init__(self, parent):
        self.parent = parent
        self.pulse_animation = 0  # 用于控制脉冲动画效果的数值变量
        self.indicator_rect = None  # 右上角状态显示器区域

        # 脉冲定时器
        self.pulse_timer = QTimer(parent)
        self.pulse_timer.timeout.connect(self.update_pulse)
        self.pulse_timer.start(50)

    def update_pulse(self):
        """
        定期更新脉冲动画的相位值
        触发父窗口重绘以显示动画效果
        """
        self.pulse_animation = (self.pulse_animation + 0.1) % (2 * 3.14159)
        self.parent.update()

    def start_flash_alert(self):  # 闪烁提醒
        def _flash(step=0):
            if step < 6:
                color = "red" if step % 2 == 0 else "white"
                self.parent.time_label.setStyleSheet(f"color: {color}; font-weight: bold;")
                QTimer.singleShot(300, lambda: _flash(step + 1))
            else:
                self.parent.time_label.setStyleSheet("color: white; font-weight: normal;")

        _flash()

    def paint_timer(self, event):
        current_timer=self.parent.mode_manager.get_current_timer()
        painter = QPainter(self.parent)
        painter.setRenderHint(painter.Antialiasing)
        center = self.parent.rect().center()
        gradient = QRadialGradient(center, 60)

        # 动态适配窗口大小
        rect = self.parent.rect()
        size = min(rect.width(), rect.height()) - 10  # 留20像素边距
        x = (rect.width() - size) // 2
        y = (rect.height() - size) // 2


        # 根据剩余时间设置颜色
        if current_timer.remaining == 0:
            gradient.setColorAt(0, QColor(*APP_CONFIG.COLOR_NORMAL))
            gradient.setColorAt(1, QColor(*APP_CONFIG.COLOR_GRADIENT_BOTTOM))
        elif current_timer.remaining <0 or current_timer.remaining <= APP_CONFIG.CRITICAL_THRESHOLD:
            r, g, b = APP_CONFIG.COLOR_CRITICAL
            gradient.setColorAt(0, QColor(r, g, b))
            gradient.setColorAt(1, QColor(max(0, r - 50), max(0, g - 50), max(0, b - 50)))
        elif current_timer.remaining <= APP_CONFIG.WARNING_THRESHOLD:
            r, g, b = APP_CONFIG.COLOR_WARNING
            gradient.setColorAt(0, QColor(r, g, b))
            gradient.setColorAt(1, QColor(max(0, r - 50), max(0, g - 50), max(0, b - 50)))
        else:
            gradient.setColorAt(0, QColor(*APP_CONFIG.COLOR_NORMAL))
            gradient.setColorAt(1, QColor(*APP_CONFIG.COLOR_GRADIENT_BOTTOM))


        painter.setBrush(gradient)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(self.parent.rect())


        # 脉冲动画 - 金黄色 + 自适应窗口大小
        if hasattr(current_timer, "time_or_income") and not current_timer.time_or_income:
            pulse_value = abs(math.sin(self.pulse_animation)) * 0.5 + 0.5
            pulse_color = QColor(255, 200, 0, int(180 * pulse_value))
            painter.setBrush(Qt.NoBrush)
            painter.setPen(QPen(pulse_color, 5))
            painter.drawEllipse(x, y, size, size)

        else:
            if current_timer.total_seconds > 0:
                if current_timer.is_running:
                    pulse_value = abs(math.sin(self.pulse_animation)) * 0.5 + 0.5
                    pulse_color = QColor(0, 255, 0, int(100 * pulse_value))
                    painter.setBrush(Qt.NoBrush)
                    painter.setPen(QPen(pulse_color, 4))
                    painter.drawEllipse(x, y, size, size)
                elif current_timer.remaining <= 0:  # 时间耗尽状态（红色）
                    pulse_value = abs(math.sin(self.pulse_animation)) * 0.5 + 0.5
                    pulse_color = QColor(255, 0, 0, int(100 * pulse_value))
                    painter.setBrush(Qt.NoBrush)
                    painter.setPen(QPen(pulse_color, 4))
                    painter.drawEllipse(x, y, size, size)
                else:  # 暂停状态（黄色）
                    pulse_value = abs(math.sin(self.pulse_animation)) * 0.5 + 0.5
                    pulse_color = QColor(255, 200, 0, int(150 * pulse_value))
                    painter.setBrush(Qt.NoBrush)
                    painter.setPen(QPen(pulse_color, 6))
                    painter.drawEllipse(x, y, size, size)

        # 获取当前窗口尺寸
        rect = self.parent.rect()
        size = min(rect.width(), rect.height())

        #  进度弧线
        if current_timer.total_seconds > 0 and current_timer.remaining > 0:
            progress = 1.0 - (current_timer.remaining / current_timer.total_seconds)
            angle = int(progress * 360 * 16)
            arc_margin = 10
            arc_width = rect.width() - 2 * arc_margin
            arc_height = rect.height() - 2 * arc_margin
            painter.setBrush(Qt.NoBrush)
            painter.setPen(QPen(QColor(255, 255, 255, 100), 5))
            painter.drawArc(arc_margin, arc_margin, arc_width, arc_height, 90 * 16, -angle)

        #状态指示器
        if current_timer.total_seconds > 0 and current_timer.get_status_text() == "normal":
            indicator_size = max(8, int(size * 0.08))
            indicator_margin = max(5, int(size * 0.03))
            x = rect.width() - indicator_margin - indicator_size
            y = indicator_margin
            self.indicator_rect = QRect(x, y, indicator_size, indicator_size)

            if current_timer.is_running:
                painter.setBrush(QColor(0, 255, 0, 200))
                painter.setPen(QPen(QColor(255, 255, 255, 150), 1))
                painter.drawEllipse(x, y, indicator_size, indicator_size)
            else:
                painter.setBrush(Qt.NoBrush)
                bar_w = max(2, int(indicator_size * 0.2))
                bar_h = indicator_size
                gap = max(1, int(indicator_size * 0.1))
                painter.setPen(QPen(QColor(255, 200, 0, 200), 2))
                painter.drawRect(x, y, bar_w, bar_h)
                painter.drawRect(x + bar_w + gap, y, bar_w, bar_h)
        else:
            self.indicator_rect = None





