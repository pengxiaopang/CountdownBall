from PyQt5.QtWidgets import QWidget, QLabel, QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from core.mode import ModeManager
from core.system.tray import TrayHandler
from core.input.mouse import MouseHandler
from core.system.autostart import AutostartManager
from core.display.color import ColorManager
from ui.menu import MenuManager
from core.display.renderer import TimerRenderer
from config.env import reset_config
from config.settings import APP_CONFIG


class CountdownBall(QWidget):
    def __init__(self):
        super().__init__()
        # 初始化几个部件
        self._setup_window() # 主窗口
        self._setup_components() # 组件功能

    def _setup_window(self):
        # 设置 无边框窗口|窗口始终保持在最顶层|工具窗口类型
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        # 透明背景
        self.setAttribute(Qt.WA_TranslucentBackground)
        # 设置主窗口size
        self.setFixedSize(APP_CONFIG.BALL_SIZE, APP_CONFIG.BALL_SIZE)

        self.time_label = QLabel("00:00", self) # 时间显示区域
        self.time_label.setAlignment(Qt.AlignCenter) # 文本居中
        self.time_label.setFont(QFont("Arial", 26, QFont.Bold)) # 颜色
        self.time_label.setGeometry(0, 0, APP_CONFIG.BALL_SIZE, APP_CONFIG.BALL_SIZE) # 位置尺寸
        self.time_label.setStyleSheet("color: rgba(255,255,255,0.95); background: transparent;")

    def _setup_components(self):
        self.mode_manager = ModeManager(self)
        self.tray_handler = TrayHandler(self)
        self.mouse_handler = MouseHandler(self)
        self.autostart_manager = AutostartManager(self)
        self.color_manager = ColorManager(self)
        self.menu_manager = MenuManager(self)
        self.timer_renderer = TimerRenderer(self)


    def center_on_screen(self):
        screen = QApplication.primaryScreen().availableGeometry()
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2
        )

    def update_display(self,remaining): # 更新计时显示

        m, s = divmod(abs(remaining), 60)
        print(m, s)
        if remaining<0:
            self.time_label.setText(f"-{m:02d}:{s:02d}")
        else:
            self.time_label.setText(f"{m:02d}:{s:02d}")
        self.update()

    def reset_timer(self):
        reset_config()
        self.update_display(0)


    def flash_alert(self): # 时间显示闪烁（结束计时）
        self.timer_renderer.start_flash_alert()


    def paintEvent(self, event): # 绘画事件
        self.timer_renderer.paint_timer(event)

    def mousePressEvent(self, event): # 鼠标点击事件
        self.mouse_handler.handle_mouse_press(event)

    def mouseMoveEvent(self, event): # 鼠标移动事件
        self.mouse_handler.handle_mouse_move(event)

    def mouseDoubleClickEvent(self, event): # 鼠标双击事件
        self.mouse_handler.handle_mouse_double_click(event)

    def closeEvent(self, event): # 关闭事件
        self.tray_handler.hide_to_tray(event)

    def is_autostart_enabled(self): # 检查开机自启状态
        return self.autostart_manager.is_autostart_enabled()

    def set_autostart(self, enabled: bool): # 设置开机自启
        self.autostart_manager.set_autostart(enabled)

    def open_color_dialog(self): # 打开颜色选择对话框
        self.color_manager.open_color_dialog()

    def hide_to_tray(self): # 隐藏到托盘
        self.tray_handler.hide_to_tray(None)

    def show_context_menu(self,pos):
        self.menu_manager.show_context_menu(pos)

    def set_ball_size(self, size: int):
        """动态调整球体大小"""
        self.setFixedSize(size, size)

        # 调整时间标签
        font_size = max(12, int(size * 0.24))  #
        self.time_label.setFont(QFont("Arial", font_size, QFont.Bold))
        self.time_label.setGeometry(0, 0, size, size)

        # 触发重绘
        self.update()