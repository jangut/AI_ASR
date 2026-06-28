'''
滚动历史记录，只读文本编辑框。
'''


from PySide6.QtWidgets import QTextEdit
from PySide6.QtGui import QFont


class HistoryWidget(QTextEdit):
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)
        self.setPlaceholderText("笔记将显示在这里...")
        font = QFont("Segoe UI", 12)
        self.setFont(font)
        self.setStyleSheet("background-color: #fafafa; border: none;")

    def append_sentence(self, sentence):
        self.append(f"- {sentence.text}")
        # 滚动到底
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())

    def clear(self):
        self.clear()