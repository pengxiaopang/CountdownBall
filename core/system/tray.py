from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QStyle
from PyQt5.QtGui import QIcon
import os


class TrayHandler:
    def __init__(self, parent):
        self.parent = parent
        self.is_in_tray = False
        self._setup_tray()

    def _setup_tray(self):
        self.tray_icon = QSystemTrayIcon(self.parent)

        # 尝试加载本地图标
        logo_path = "data/logo.ico"
        if os.path.exists(logo_path):
            self.tray_icon.setIcon(QIcon(logo_path))
        else:
            icon = self.parent.style().standardIcon(QStyle.SP_MessageBoxInformation)
            self.tray_icon.setIcon(QIcon(icon.pixmap(64, 64)))
        self.tray_icon.setToolTip("倒计时悬浮球\n双击恢复窗口")

        tray_menu = QMenu()
        self.restore_action = tray_menu.addAction("显示窗口")
        self.restore_action.triggered.connect(self.show_from_tray)
        tray_menu.addSeparator()
        exit_action = tray_menu.addAction("退出")
        exit_action.triggered.connect(self.parent.close)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.on_tray_activated)
        self.tray_icon.show()

    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_from_tray()

    def show_from_tray(self):
        self.parent.showNormal()
        self.parent.activateWindow()
        self.parent.raise_()
        self.is_in_tray = False

    def hide_to_tray(self, event=None):
        """隐藏到托盘"""
        if event:
            event.ignore()
        self.parent.hide()
        self.is_in_tray = True



