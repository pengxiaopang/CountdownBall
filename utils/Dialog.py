import sys
from PyQt5.QtWidgets import QDialog
import traceback
import datetime
import win32api
import logging

# 初始化日志配置
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=f"log_{datetime.datetime.now().strftime('%Y-%m-%d')}.log",
    filemode='a'
)


def handle_uncaught_exception(exc_type, exc_value, exc_traceback):
    logging.error("全局未捕获异常", exc_info=(exc_type, exc_value, exc_traceback))
    print(f"发生未捕获异常: \n类型 - {exc_type.__name__},\n 详细信息 - {exc_value}, \n跟踪信息如下:")
    formatted_traceback = ''.join(traceback.format_tb(exc_traceback))
    print(formatted_traceback)
    win32api.MessageBox(0, '程序遇到问题，请查看日志或联系技术支持。', '错误', 0)


sys.excepthook = handle_uncaught_exception


class LoadingDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.resize(250, 5)
        self.setWindowTitle("程序正在初始化. . . . . .")


class Logger:
    def __init__(self):
        self.current_date = self.get_current_date()
        self.log()
        sys.excepthook = self.handle_uncaught_exception

    @staticmethod
    def log():
        # 配置日志模块
        logging.basicConfig(
            level=logging.DEBUG,  # 设置日志级别为DEBUG，低于这个级别的日志不会被记录,debug, info, warning, error, critical
            format='%(asctime)s - %(levelname)s - %(message)s',  # 日志格式
            filename=f"log_{Logger.get_current_date()}.log",  # 日志文件名，如果省略，则默认输出到控制台
            filemode='a'  # 'w'表示每次运行都重写日志文件，'a'表示追加
        )

    @staticmethod
    def get_current_date():
        return datetime.datetime.now().strftime('%Y-%m-%d')

    @staticmethod
    def handle_uncaught_exception(exc_type, exc_value, exc_traceback):
        # 记录到日志
        logging.error("全局未捕获异常", exc_info=(exc_type, exc_value, exc_traceback))
        # 同时打印到终端
        print(f"发生未捕获异常: \n类型 - {exc_type.__name__},\n 详细信息 - {exc_value}, \n跟踪信息如下:")
        formatted_traceback = ''.join(traceback.format_tb(exc_traceback))
        print(formatted_traceback)
        # 使用win32api显示消息框
        win32api.MessageBox(0, '程序遇到问题，请查看日志或联系技术支持。', '错误', 0)
