import sys
import psutil

if sys.platform == "win32":
    import ctypes
    from ctypes import wintypes

    user32 = ctypes.windll.user32
    EnumWindows = user32.EnumWindows
    GetWindowTextW = user32.GetWindowTextW
    GetWindowTextLengthW = user32.GetWindowTextLengthW
    GetWindowThreadProcessId = user32.GetWindowThreadProcessId
    IsWindowVisible = user32.IsWindowVisible
    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)


def get_powerpoint_slide_pid():
    if sys.platform != "win32":
        return None
    slide_pids = set()

    def enum_window_callback(hwnd, _):
        if not IsWindowVisible(hwnd):
            return True
        length = GetWindowTextLengthW(hwnd)
        if length == 0:
            return True
        buffer = ctypes.create_unicode_buffer(length + 1)
        GetWindowTextW(hwnd, buffer, length + 1)
        title = buffer.value
        if "幻灯片放映" in title or "Slide Show" in title or "放映" in title:
            pid = wintypes.DWORD()
            GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            try:
                proc = psutil.Process(pid.value)
                if proc.name().lower() == "powerpnt.exe":
                    slide_pids.add(pid.value)
            except (psutil.NoSuchProcess, psutil.AccessDenied, OSError):
                pass
        return True

    try:
        EnumWindows(WNDENUMPROC(enum_window_callback), 0)
    except Exception as e:
        print(f"[DEBUG] 枚举窗口失败: {e}")
        return None
    return next(iter(slide_pids)) if slide_pids else None
