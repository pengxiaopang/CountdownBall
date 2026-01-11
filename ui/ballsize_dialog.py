# ui/size_dialog.py
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QSlider, QLabel
from PyQt5.QtCore import Qt
from dotenv import set_key
from config.env import ENV_PATH


class SizeDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("调整球体大小")
        self.setModal(True)
        self.resize(300, 100)

        layout = QVBoxLayout()

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(80, 300)
        current_size = self.parent.width()
        self.slider.setValue(current_size)
        self.slider.valueChanged.connect(self.on_size_changed)

        self.label = QLabel(f"大小: {current_size}px")
        self.label.setAlignment(Qt.AlignCenter)

        layout.addWidget(self.label)
        layout.addWidget(self.slider)
        self.setLayout(layout)

    def on_size_changed(self, value):
        self.label.setText(f"大小: {value}px")
        self.parent.set_ball_size(value)

        set_key(ENV_PATH, 'BALL_SIZE', str(value))

