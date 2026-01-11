from PyQt5.QtWidgets import (
    QDialog, QLabel, QSlider, QPushButton, QVBoxLayout, QHBoxLayout,
    QGroupBox, QSpinBox, QCheckBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from dotenv import set_key

from config.settings import APP_CONFIG


class CountdownDialog(QDialog):
    def __init__(self, parent=None, mode="normal"):
        super().__init__(parent)
        self.mode = mode.lower()
        self.setWindowTitle("⏱️ 设置倒计时")
        self.setFixedSize(400, 340)
        self.setModal(True)
        self.setWindowFlags(Qt.Dialog | Qt.WindowStaysOnTopHint)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(18)
        layout.setContentsMargins(25, 25, 25, 25)

        # 标题与复选框区域
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)  # 不加额外边距
        title_layout.setSpacing(10)

        # 图标+文字标题
        title_label = QLabel("⏱️ 设置倒计时")
        title_label.setAlignment(Qt.AlignLeft)
        title_label.setFont(QFont("Microsoft YaHei", 16, QFont.Bold))
        title_label.setStyleSheet("color: #333;")

        # 复选框
        self.note_checkbox = QCheckBox("弹窗提醒")
        self.note_checkbox.setChecked(False)
        self.note_checkbox.setFont(QFont("Microsoft YaHei", 9))
        self.note_checkbox.setStyleSheet("""
            QCheckBox {
                color: #d32f2f;
                font-family: "Microsoft YaHei";
                font-size: 10px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
            }
        """)

        # 添加到布局
        title_layout.addWidget(title_label)
        title_layout.addStretch()  # 居中对齐
        title_layout.addWidget(self.note_checkbox)

        # 添加到主布局
        layout.addLayout(title_layout)

        # 总时长输入
        time_layout = QHBoxLayout()
        time_label = QLabel("倒计时时长")
        time_label.setFont(QFont("Microsoft YaHei", 12))
        self.spin_duration = QSpinBox()
        self.spin_duration.setRange(1, 120)


        if self.mode == "slide":
            default_min = APP_CONFIG.SLIDE_MODE_DEFAULT_DURATION
        else:
            default_min = APP_CONFIG.NORMAL_MODE_DEFAULT_DURATION

        self.spin_duration.setValue(default_min)
        self.spin_duration.setFixedSize(80, 32)
        self.spin_duration.setFont(QFont("Microsoft YaHei", 12))
        self.spin_duration.setAlignment(Qt.AlignCenter)
        unit_label = QLabel("分钟")
        unit_label.setFont(QFont("Microsoft YaHei", 12))

        time_layout.addWidget(time_label)
        time_layout.addStretch()
        time_layout.addWidget(self.spin_duration)
        time_layout.addWidget(unit_label)
        layout.addLayout(time_layout)

        #  主时间轴滑块
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(1)
        self.slider.setMaximum(120)
        self.slider.setValue(default_min)
        self.slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 8px;
                background: #e0e0e0;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                width: 16px;
                height: 16px;
                margin: -4px 0;
                border: 2px solid #007BFF;
                border-radius: 8px;
                background: white;
            }
            QSlider::handle:horizontal:hover {
                border-color: #0056b3;
            }
        """)
        layout.addWidget(self.slider)

        # 阈值设置
        threshold_group = QGroupBox("颜色变化阈值")
        threshold_group.setFont(QFont("Microsoft YaHei", 10))
        threshold_layout = QVBoxLayout()

        # 获取主倒计时时长（分钟）
        if self.mode == "slide":
            default_min = APP_CONFIG.SLIDE_MODE_DEFAULT_DURATION
        else:
            default_min = APP_CONFIG.NORMAL_MODE_DEFAULT_DURATION

        total_sec = default_min * 60

        # 从配置读取阈值（秒）
        warn_sec_config = APP_CONFIG.WARNING_THRESHOLD
        crit_sec_config = APP_CONFIG.CRITICAL_THRESHOLD

        # 安全计算百分比（避免除零、越界）
        def sec_to_percent(sec, total):
            if total <= 0:
                return 50
            pct = round(sec / total * 100)
            return max(0, min(100, pct))

        warn_percent = sec_to_percent(warn_sec_config, total_sec)
        crit_percent = sec_to_percent(crit_sec_config, total_sec)

        # 确保临界 ≤ 警告（UI 逻辑）
        if crit_percent > warn_percent:
            crit_percent = warn_percent

        #  警告阈值
        warn_layout = QHBoxLayout()
        warn_label = QLabel("警告阈值")
        warn_label.setFont(QFont("Microsoft YaHei", 10))
        self.warn_slider = QSlider(Qt.Horizontal)
        self.warn_slider.setRange(0, 100)
        self.warn_slider.setValue(warn_percent)  #  使用计算出的百分比
        self.warn_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 4px;
                background: transparent;
            }
            QSlider::handle:horizontal {
                width: 10px;
                height: 10px;
                margin: -5px 0;
                border: 2px solid #ff9800;
                border-radius: 5px;
                background: #ff9800;
            }
        """)
        self.warn_display = QLabel(f"{warn_sec_config} 秒")
        self.warn_display.setStyleSheet("color: #ff9800; font-weight: bold;")
        warn_layout.addWidget(warn_label)
        warn_layout.addWidget(self.warn_slider)
        warn_layout.addWidget(self.warn_display)
        threshold_layout.addLayout(warn_layout)

        # 临界阈值
        crit_layout = QHBoxLayout()
        crit_label = QLabel("临界阈值")
        crit_label.setFont(QFont("Microsoft YaHei", 10))
        self.crit_slider = QSlider(Qt.Horizontal)
        self.crit_slider.setRange(0, 100)
        self.crit_slider.setValue(crit_percent)
        self.crit_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 4px;
                background: transparent;
            }
            QSlider::handle:horizontal {
                width: 10px;
                height: 10px;
                margin: -5px 0;
                border: 2px solid #f44336;
                border-radius: 5px;
                background: #f44336;
            }
        """)
        self.crit_display = QLabel(f"{crit_sec_config} 秒")
        self.crit_display.setStyleSheet("color: #f44336; font-weight: bold;")
        crit_layout.addWidget(crit_label)
        crit_layout.addWidget(self.crit_slider)
        crit_layout.addWidget(self.crit_display)
        threshold_layout.addLayout(crit_layout)

        threshold_group.setLayout(threshold_layout)
        layout.addWidget(threshold_group)


        # 按钮
        btn_layout = QHBoxLayout()
        start_btn = QPushButton("开始倒计时")
        start_btn.setFixedSize(120, 40)
        start_btn.clicked.connect(self.accept)
        start_btn.setStyleSheet("""
            QPushButton {
                background-color: #007BFF;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                font-family: "Microsoft YaHei";
            }
            QPushButton:hover { background-color: #0056b3; }
        """)

        cancel_btn = QPushButton("取消")
        cancel_btn.setFixedSize(100, 40)
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                font-family: "Microsoft YaHei";
            }
            QPushButton:hover { background-color: #545b62; }
        """)

        btn_layout.addStretch()
        btn_layout.addWidget(start_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        #  全局样式
        self.setStyleSheet("""
            QDialog {
                background-color: white;
                border-radius: 12px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            }
            QLabel {
                color: #333;
                font-family: "Microsoft YaHei";
            }
            QSpinBox {
                border: 1px solid #ccc;
                border-radius: 6px;
                padding: 6px;
                font-size: 14px;
            }
            QGroupBox {
                border: 1px solid #ddd;
                border-radius: 8px;
                margin-top: 10px;
                padding: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
                color: #555;
            }
        """)

        #  信号连接
        self.spin_duration.valueChanged.connect(self.slider.setValue)
        self.slider.valueChanged.connect(self.spin_duration.setValue)
        self.warn_slider.valueChanged.connect(self._update_warn_display)
        self.crit_slider.valueChanged.connect(self._update_crit_display)
        self.warn_slider.valueChanged.connect(self._enforce_order)
        self.crit_slider.valueChanged.connect(self._enforce_order)

        # 初始化显示
        self._update_warn_display()
        self._update_crit_display()

    def _enforce_order(self):
        """确保临界阈值不超过警告阈值"""
        warn_val = self.warn_slider.value()
        crit_val = self.crit_slider.value()
        if crit_val > warn_val:
            self.crit_slider.setValue(warn_val)

    def _update_warn_display(self):
        total_sec = self.get_minutes() * 60
        sec = int(total_sec * self.warn_slider.value() / 100.0)
        minutes = sec // 60
        remaining_sec = sec % 60
        self.warn_display.setText(f"{minutes}分{remaining_sec}秒")

    def _update_crit_display(self):
        total_sec = self.get_minutes() * 60
        sec = int(total_sec * self.crit_slider.value() / 100.0)
        minutes = sec // 60
        remaining_sec = sec % 60
        self.crit_display.setText(f"{minutes}分{remaining_sec}秒")

    def get_minutes(self):
        return self.spin_duration.value()

    def get_warning_threshold(self):
        total_sec = self.get_minutes() * 60
        return int(total_sec * (self.warn_slider.value() / 100.0))

    def get_critical_threshold(self):
        total_sec = self.get_minutes() * 60
        return int(total_sec * (self.crit_slider.value() / 100.0))

    def update_config(self):
        """
        更新 AppConfig 单例，立即生效,更新配置文件中的默认时长
        """
        from config.env import ENV_PATH

        minutes = self.get_minutes()
        warn_sec = self.get_warning_threshold()
        crit_sec = self.get_critical_threshold()

        if self.mode == "slide":
            APP_CONFIG.SLIDE_MODE_DEFAULT_DURATION = minutes
        else:
            APP_CONFIG.NORMAL_MODE_DEFAULT_DURATION = minutes

        APP_CONFIG.WARNING_THRESHOLD = warn_sec
        APP_CONFIG.CRITICAL_THRESHOLD = crit_sec

        try:
            if self.mode == "slide":
                set_key(ENV_PATH, 'SLIDE_MODE_DEFAULT_DURATION', str(minutes))
            else:
                set_key(ENV_PATH, 'NORMAL_MODE_DEFAULT_DURATION', str(minutes))

            set_key(ENV_PATH, 'COLOR_WARNING_THRESHOLD', str(warn_sec))
            set_key(ENV_PATH, 'COLOR_CRITICAL_THRESHOLD', str(crit_sec))

        except Exception as e:

            print(f" 保存配置到 .env 失败: {e}")

    def get_note_enabled(self):
        """返回是否启用了提醒"""
        return self.note_checkbox.isChecked()
