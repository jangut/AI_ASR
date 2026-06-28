'''
状态栏组合。
'''


from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel


class StatusBar(QWidget):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 2, 8, 2)
        self.record_label = QLabel("⏸ 就绪")
        self.mode_label = QLabel("VAD")
        self.source_label = QLabel("麦克风")
        self.time_label = QLabel("00:00")

        layout.addWidget(self.record_label)
        layout.addWidget(QLabel("|"))
        layout.addWidget(self.mode_label)
        layout.addWidget(QLabel("|"))
        layout.addWidget(self.source_label)
        layout.addWidget(QLabel("|"))
        layout.addWidget(self.time_label)
        layout.addStretch()

    def update_field(self, key, value):
        if key == "recording":
            self.record_label.setText("🔴 录音中" if value == "true" else "⏸ 暂停")
        elif key == "mode":
            self.mode_label.setText(value)
        elif key == "time":
            self.time_label.setText(value)
        # 可按需扩展