import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from ui.main_window import CountdownBall
from utils.logger import logger




def main():
    # 高DPI支持
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    # 平台检查
    if sys.platform != "win32":
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.critical(None, "错误", "本程序仅支持 Windows 系统（因依赖 PowerPoint 检测和注册表）")
        sys.exit(1)

    # 创建主窗口
    ball = CountdownBall()
    ball.center_on_screen()
    ball.show()

    logger.info("倒计时悬浮球已启动")

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
