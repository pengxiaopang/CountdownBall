from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor
from config.settings import APP_CONFIG
from ui.settings_dialog import CountdownDialog


class MouseHandler:
    def __init__(self, parent):
        self.parent = parent
        self.drag_pos = None  # 存储鼠标拖拽的相对位置偏移
        self.indicator_rect = None  # 指示器区域矩形


    def handle_mouse_press(self, event):
        current_timer = self.parent.mode_manager.get_current_timer()
        if event.button() == Qt.RightButton:
            self.parent.show_context_menu(QCursor.pos())
        elif event.button() == Qt.LeftButton:
            # 从 TimerManager 获取指示器区域
            timer_indicator = getattr(self.parent.timer_renderer, 'indicator_rect', None)
            if (timer_indicator is not None and
                    timer_indicator.contains(event.pos())):
                self._toggle_pause()
                return
            # 记录当前鼠标位置
            self.drag_pos = event.globalPos() - self.parent.frameGeometry().topLeft()

    def handle_mouse_move(self, event):
        if event.buttons() & Qt.LeftButton and self.drag_pos is not None:
            self.parent.move(event.globalPos() - self.drag_pos)

    def handle_mouse_double_click(self, event):
        current_timer = self.parent.mode_manager.get_current_timer()
        if event.button() == Qt.LeftButton :
            if current_timer.get_status_text() in ["normal", 'slide']:
                dialog = CountdownDialog(self.parent, current_timer.get_status_text())
                if dialog.exec_() == dialog.Accepted:
                    note_enabled = dialog.get_note_enabled()
                    print(note_enabled)
                    if hasattr(current_timer, "note"):
                        current_timer.note = note_enabled
                    current_timer.start_countdown(dialog.get_minutes())
                    current_timer.total_seconds=dialog.get_minutes()*60
                    # 更新配置，单例模式全部组件共享一个配置实例
                    dialog.update_config()
                    setattr(APP_CONFIG, f"{current_timer.get_status_text().upper()}_MODE_DEFAULT_DURATION", dialog.get_minutes())
                    # 手动触发重绘，确保渲染器感知变化
                    self.parent.update()

            else:
                self.shift_cow_time_or_income()


            # 手动触发重绘，确保渲染器感知变化
            self.parent.update()



    def _toggle_pause(self):
        """切换暂停/继续"""
        current_timer = self.parent.mode_manager.get_current_timer()
        # 只有普通模式才允许暂停/继续
        if current_timer.total_seconds <= 0 or current_timer.get_status_text() != "normal":
            return
        current_timer.is_running = not current_timer.is_running
        if current_timer.is_running:
            current_timer.timer.start(1000)
        else:
            current_timer.timer.stop()
        self.parent.update()

    def shift_cow_time_or_income(self):
        current_timer = self.parent.mode_manager.get_current_timer()
        # 只有牛马模式才切换
        if current_timer.get_status_text() != "cow":
            return
        current_timer.time_or_income = not current_timer.time_or_income

        if  current_timer.time_or_income:
            current_timer.cow_timer.timeout.connect(current_timer.update_countdown)
        else:
            current_timer.cow_timer.timeout.connect(current_timer.update_income_display)
