
import os
import sys
import winreg


class AutostartManager:
    def __init__(self, parent=None):
        self.parent = parent

    def is_autostart_enabled(self):
        """检查开机自启是否启用"""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_READ
            )
            value, _ = winreg.QueryValueEx(key, "CountdownBall")
            winreg.CloseKey(key)
            return os.path.abspath(sys.argv[0]) in value
        except FileNotFoundError:
            return False
        except Exception:
            return False

    def set_autostart(self, enabled: bool):
        """设置开机自启"""
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_WRITE
        )
        if enabled:
            exe_path = os.path.abspath(sys.argv[0])
            if exe_path.endswith(".py"):
                python_exe = sys.executable
                winreg.SetValueEx(
                    key, "CountdownBall", 0, winreg.REG_SZ,
                    f'"{python_exe}" "{exe_path}"'
                )
            else:
                winreg.SetValueEx(
                    key, "CountdownBall", 0, winreg.REG_SZ,
                    f'"{exe_path}"'
                )
        else:
            try:
                winreg.DeleteValue(key, "CountdownBall")
            except FileNotFoundError:
                pass
        winreg.CloseKey(key)
