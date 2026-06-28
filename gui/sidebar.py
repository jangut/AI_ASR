'''
左侧导航按钮。
'''


from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PySide6.QtCore import Signal


class Sidebar(QWidget):
    settings_requested = Signal()
    help_requested = Signal()

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 8, 4, 8)

        btn_output = QPushButton("📝 输出")
        btn_settings = QPushButton("⚙️ 设置")
        btn_help = QPushButton("❓ 帮助")

        for btn in (btn_output, btn_settings, btn_help):
            btn.setCheckable(True)
            btn.setMinimumHeight(40)
            layout.addWidget(btn)

        btn_output.setChecked(True)

        btn_settings.clicked.connect(self.settings_requested)
        btn_help.clicked.connect(self.help_requested)

        layout.addStretch()