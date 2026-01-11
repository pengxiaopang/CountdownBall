from PyQt5.QtGui import QIntValidator, QColor
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QGridLayout, QMessageBox, QHBoxLayout, QColorDialog
)
from config.env import (
    load_config, validate_time_format, validate_int_range,
    validate_rgb_string, CountdownConfig,ENV_PATH
)


class ConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("⚙️ 配置管理")
        self.setFixedSize(520, 520)
        self.parent = parent
        self.grid = QGridLayout()
        self._setup_ui()

    def _apply_validator(self, line_edit, validator_func, error_msg):
        """通用校验绑定"""
        def check():
            text = line_edit.text().strip()
            if not text:
                line_edit.setStyleSheet("")
                line_edit.setToolTip("")
                return
            if validator_func(text):
                line_edit.setStyleSheet("")
                line_edit.setToolTip("")
            else:
                line_edit.setStyleSheet("border: 2px solid red;")
                line_edit.setToolTip(error_msg)
        line_edit.textChanged.connect(check)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        row = 0
        config = load_config()

        #  颜色配置
        color_fields = [
            ("color_normal", "正常状态颜色"),
            ("color_gradient_bottom", "渐变底部颜色"),
            ("color_warning", "警告状态颜色"),
            ("color_critical", "临界状态颜色"),
        ]
        for name, label in color_fields:
            lbl = QLabel(label)
            color_str = ",".join(map(str, config.get_color_tuple(name)))
            line_edit = QLineEdit(color_str)
            self._apply_validator(
                line_edit,
                validate_rgb_string,
                "格式: r,g,b（0~255），例如 255,100,100"
            )

            btn = QPushButton("选择颜色")
            btn.setFixedWidth(80)
            btn.clicked.connect(lambda _, le=line_edit: self._open_color_picker(le))

            hbox = QHBoxLayout()
            hbox.addWidget(line_edit)
            hbox.addWidget(btn)
            hbox.setSpacing(5)

            self.grid.addWidget(lbl, row, 0)
            self.grid.addLayout(hbox, row, 1)
            row += 1

        #  阈值配置（带联动）
        lbl_warn = QLabel("警告阈值（秒）")
        self.warn_edit = QLineEdit(str(config.color_warning_threshold))
        self.warn_edit.setValidator(QIntValidator(0, 3600))
        self._apply_validator(
            self.warn_edit,
            lambda x: validate_int_range(x, 0, 3600),
            "请输入 0~3600 之间的整数"
        )

        lbl_crit = QLabel("临界阈值（秒）")
        self.crit_edit = QLineEdit(str(config.color_critical_threshold))
        self.crit_edit.setValidator(QIntValidator(0, 3600))
        self._apply_validator(
            self.crit_edit,
            lambda x: validate_int_range(x, 0, 3600),
            "请输入 0~3600 之间的整数"
        )

        # 联动校验
        def validate_thresholds():
            try:
                w = int(self.warn_edit.text())
                c = int(self.crit_edit.text())
                if c >= w:
                    self.crit_edit.setStyleSheet("border: 2px solid red;")
                    self.crit_edit.setToolTip("临界阈值必须小于警告阈值")
                else:
                    self.crit_edit.setStyleSheet("")
                    self.crit_edit.setToolTip("")
            except ValueError:
                pass

        self.warn_edit.textChanged.connect(validate_thresholds)
        self.crit_edit.textChanged.connect(validate_thresholds)

        self.grid.addWidget(lbl_warn, row, 0)
        self.grid.addWidget(self.warn_edit, row, 1)
        row += 1
        self.grid.addWidget(lbl_crit, row, 0)
        self.grid.addWidget(self.crit_edit, row, 1)
        row += 1

        # 时长配置
        duration_fields = [
            ("slide_mode_default_duration", "幻灯片模式默认时长（分钟）", 1, 120),
            ("normal_mode_default_duration", "普通模式默认时长（分钟）", 1, 120),
        ]
        for name, label, min_v, max_v in duration_fields:
            lbl = QLabel(label)
            le = QLineEdit(str(getattr(config, name)))
            le.setValidator(QIntValidator(min_v, max_v))
            self._apply_validator(
                le,
                lambda x, mv=min_v, Mv=max_v: validate_int_range(x, mv, Mv),
                f"请输入 {min_v}~{max_v} 之间的整数"
            )
            self.grid.addWidget(lbl, row, 0)
            self.grid.addWidget(le, row, 1)
            row += 1

        # 时间配置
        time_fields = [
            ("cow_mode_odd_week_lunch_time", "单周午休时间"),
            ("cow_mode_even_week_lunch_time", "双周午休时间"),
            ("cow_mode_afternoon_off_time", "下班时间"),
            ("cow_mode_mooning_on_time", "上班时间"),
        ]
        for name, label in time_fields:
            lbl = QLabel(label)
            le = QLineEdit(getattr(config, name))
            self._apply_validator(
                le,
                validate_time_format,
                "格式: HH:MM，例如 08:30"
            )
            self.grid.addWidget(lbl, row, 0)
            self.grid.addWidget(le, row, 1)
            row += 1

        #  工资配置（无校验）
        lbl_income = QLabel("每月收入")
        self.income_edit = QLineEdit(str(config.cow_income_per_month))
        self.income_edit.setEchoMode(QLineEdit.Password)

        toggle_btn = QPushButton("👁️")
        toggle_btn.setCheckable(True)
        toggle_btn.setFixedWidth(40)
        toggle_btn.clicked.connect(self._toggle_income_visibility)

        hbox_income = QHBoxLayout()
        hbox_income.addWidget(self.income_edit)
        hbox_income.addWidget(toggle_btn)
        hbox_income.setSpacing(5)

        self.grid.addWidget(lbl_income, row, 0)
        self.grid.addLayout(hbox_income, row, 1)
        row += 1

        # 每月工作日数（保留校验）
        lbl_days = QLabel("每月工作天数")
        self.days_edit = QLineEdit(str(config.cow_working_days_per_month))
        self.days_edit.setValidator(QIntValidator(1, 31))
        self._apply_validator(
            self.days_edit,
            lambda x: validate_int_range(x, 1, 31),
            "请输入 1~31 之间的整数"
        )
        self.grid.addWidget(lbl_days, row, 0)
        self.grid.addWidget(self.days_edit, row, 1)
        row += 1

        #  按钮
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("保存")
        cancel_btn = QPushButton("取消")
        btn_layout.addStretch()
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)

        save_btn.clicked.connect(self.save_config)
        cancel_btn.clicked.connect(self.reject)

        layout.addLayout(self.grid)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def _toggle_income_visibility(self):
        """切换工资输入框的明文/密文显示"""
        btn = self.sender()
        if btn.isChecked():
            self.income_edit.setEchoMode(QLineEdit.Normal)
            btn.setText("🙈")
        else:
            self.income_edit.setEchoMode(QLineEdit.Password)
            btn.setText("👁️")

    def _open_color_picker(self, line_edit):
        current = line_edit.text().strip()
        try:
            if current and ',' in current:
                rgb = [int(x) for x in current.split(',')]
                color = QColor(*rgb) if len(rgb) == 3 else QColor(255, 255, 255)
            else:
                color = QColor(255, 255, 255)
        except Exception:
            color = QColor(255, 255, 255)
        dlg = QColorDialog.getColor(color, self, "选择颜色")
        if dlg.isValid():
            line_edit.setText(f"{dlg.red()},{dlg.green()},{dlg.blue()}")

    def _find_line_edit_in_item(self, item):
        if not item:
            return None
        widget = item.widget()
        if widget:
            if isinstance(widget, QLineEdit):
                return widget
            elif hasattr(widget, 'layout'):
                lay = widget.layout()
                if lay:
                    for i in range(lay.count()):
                        sub_w = lay.itemAt(i).widget()
                        if isinstance(sub_w, QLineEdit):
                            return sub_w
        elif item.layout():
            lay = item.layout()
            for i in range(lay.count()):
                sub_w = lay.itemAt(i).widget()
                if isinstance(sub_w, QLineEdit):
                    return sub_w
        return None

    def save_config(self):
        try:
            data = {}

            # 颜色
            color_keys = ["color_normal", "color_gradient_bottom", "color_warning", "color_critical"]
            for i, key in enumerate(color_keys):
                item = self.grid.itemAtPosition(i, 1)
                le = self._find_line_edit_in_item(item)
                data[key] = le.text().strip() if le else ""

            # 阈值
            data["color_warning_threshold"] = int(self.warn_edit.text())
            data["color_critical_threshold"] = int(self.crit_edit.text())

            # 时长
            offset = 6
            data["slide_mode_default_duration"] = int(self.grid.itemAtPosition(offset, 1).widget().text())
            data["normal_mode_default_duration"] = int(self.grid.itemAtPosition(offset + 1, 1).widget().text())

            # 时间
            time_start = offset + 2
            time_keys = [
                "cow_mode_odd_week_lunch_time",
                "cow_mode_even_week_lunch_time",
                "cow_mode_afternoon_off_time",
                "cow_mode_mooning_on_time"
            ]
            for i, key in enumerate(time_keys):
                le = self.grid.itemAtPosition(time_start + i, 1).widget()
                data[key] = le.text().strip()

            # 工资：直接保存字符串，不转 int，不校验
            data["cow_income_per_month"] = self.income_edit.text().strip()
            data["cow_working_days_per_month"] = int(self.days_edit.text())

            # 创建模型（触发 Pydantic 验证）
            config = CountdownConfig(**data)

            # 写入 .env
            with open(ENV_PATH, "w", encoding="utf-8") as f:
                for k, v in config.model_dump().items():
                    f.write(f"{k.upper()}={v}\n")

            QMessageBox.information(self, "成功", "配置已保存！重启软件生效。")
            self.accept()

        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "错误", f"保存失败:\n{str(e)}")