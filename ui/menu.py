from PyQt5.QtWidgets import QMenu, QApplication, QMessageBox
from ui.config_dialog import ConfigDialog
from ui.shortcut_dialog import ShortcutDialog
from ui.ballsize_dialog import SizeDialog

class MenuManager:
    def __init__(self, parent):
        self.parent = parent

    def show_context_menu(self, pos):  # 显示右键菜单
        menu = QMenu()

        mode_menu = menu.addMenu("模式")
        for name, label in [("normal", "普通模式"), ("slide", "幻灯片模式"), ("cow", "牛马模式")]:
            action = mode_menu.addAction(label)
            action.setCheckable(True)
            action.setChecked(self.parent.mode_manager.mode == name)
            action.triggered.connect(lambda _, m=name: self.parent.mode_manager.set_mode(m))

        #  快捷入口子菜单
        shortcut_menu = menu.addMenu("快捷入口")
        shortcut_dialog = ShortcutDialog(self.parent)

        add_action = shortcut_menu.addAction("添加快捷入口...")
        add_action.triggered.connect(shortcut_dialog.add_shortcut)

        manage_action = shortcut_menu.addAction("管理快捷入口...")
        manage_action.triggered.connect(shortcut_dialog.manage_shortcuts)

        shortcut_menu.addSeparator()

        from collections import defaultdict
        from functools import partial

        # 加载并分组显示
        shortcuts = shortcut_dialog.load_shortcuts()
        if shortcuts:
            grouped = defaultdict(list)
            for path, category, alias in shortcuts:
                grouped[category].append((path, alias))

            for category in sorted(grouped.keys()):
                cat_menu = shortcut_menu.addMenu(category)
                for path, alias in grouped[category]:
                    action = cat_menu.addAction(alias)
                    #  使用 partial 避免闭包问题
                    action.triggered.connect(partial(shortcut_dialog.open_shortcut, path))
        else:
            empty = shortcut_menu.addAction("（暂无快捷入口）")
            empty.setEnabled(False)


        settings_menu = menu.addMenu("设置")

        color_action = settings_menu.addAction("主题颜色")
        color_action.triggered.connect(self.parent.open_color_dialog)


        size_action = settings_menu.addAction("球体大小")
        size_action.triggered.connect(self.open_size_dialog)

        config_action = settings_menu.addAction("配置管理")
        config_action.triggered.connect(lambda: ConfigDialog(self.parent).exec_())


        autostart_action = settings_menu.addAction("开机自启")
        autostart_action.setCheckable(True)
        autostart_action.setChecked(self.parent.is_autostart_enabled())
        autostart_action.triggered.connect(lambda checked: self.parent.set_autostart(checked))

        reset_action = menu.addAction("重置")
        reset_action.triggered.connect(self.parent.reset_timer)

        about_action = menu.addAction("关于")
        about_action.triggered.connect(self.show_about_info)

        tray_action = menu.addAction("最小化")
        tray_action.triggered.connect(self.parent.hide_to_tray)

        exit_action = menu.addAction("退出")
        exit_action.triggered.connect(QApplication.quit)

        menu.exec_(pos)

    def show_about_info(self):
        """显示开发者信息"""

        info = """
        <div style="font-family: Arial; font-size: 14px; line-height: 1.6;">
            <b>开发者：</b>pengxiaopang<br>
            <b>邮箱：</b><a href="247304386@qq.com">247304386@qq.com</a><br>
            <b>版本：</b>2.0.0<br>
            <b>GitHub：</b><a href="https://github.com/pengxiaopang/Countdown">https://github.com/pengxiaopang/Countdown</a><br>
            <b>功能：</b>倒计时悬浮球，支持多种模式切换和个性化配置<br>
        </div>
        """

        QMessageBox.about(self.parent, "我爱公司", info.strip())

    def open_size_dialog(self):

        dialog = SizeDialog(self.parent)
        dialog.exec_()