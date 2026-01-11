
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QColorDialog
from config.settings import APP_CONFIG
import os


class ColorManager:
    def __init__(self, parent=None):
        self.parent = parent

    def open_color_dialog(self):
        """打开颜色选择对话框"""
        current_color = QColor(*APP_CONFIG.COLOR_NORMAL)
        color = QColorDialog.getColor(current_color, self.parent, "选择主题颜色")
        if color.isValid():
            r, g, b = color.red(), color.green(), color.blue()
            # 更新全局配置
            APP_CONFIG.COLOR_NORMAL = (r, g, b)
            APP_CONFIG.COLOR_GRADIENT_BOTTOM = (max(0, r - 32), max(0, g - 32), max(0, b - 32))

            # 更新env文件
            self._update_env_file(r, g, b)

            # 触发界面更新
            if self.parent:
                self.parent.update()

    def _update_env_file(self, r, g, b):
        """更新env文件中的颜色配置"""
        from config.env import ENV_PATH
        lines = []
        updated = set()

        if os.path.exists(ENV_PATH):
            with open(ENV_PATH, "r", encoding="utf-8") as f:
                lines = f.readlines()

        for i, line in enumerate(lines):
            if line.startswith("COLOR_NORMAL="):
                lines[i] = f"COLOR_NORMAL={r},{g},{b}\n"
                updated.add("normal")
            elif line.startswith("COLOR_GRADIENT_BOTTOM="):
                lines[
                    i] = f"COLOR_GRADIENT_BOTTOM={APP_CONFIG.COLOR_GRADIENT_BOTTOM[0]},{APP_CONFIG.COLOR_GRADIENT_BOTTOM[1]},{APP_CONFIG.COLOR_GRADIENT_BOTTOM[2]}\n"
                updated.add("bottom")

        if "normal" not in updated:
            lines.append(f"COLOR_NORMAL={r},{g},{b}\n")
        if "bottom" not in updated:
            lines.append(
                f"COLOR_GRADIENT_BOTTOM={APP_CONFIG.COLOR_GRADIENT_BOTTOM[0]},{APP_CONFIG.COLOR_GRADIENT_BOTTOM[1]},{APP_CONFIG.COLOR_GRADIENT_BOTTOM[2]}\n")

        with open(ENV_PATH, "w", encoding="utf-8") as f:
            f.writelines(lines)
