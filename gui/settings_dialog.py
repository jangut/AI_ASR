'''
从 Config dataclass 自动生成表单。
'''

from dataclasses import fields
from PySide6.QtWidgets import (
    QDialog, QFormLayout, QCheckBox, QSpinBox, QDoubleSpinBox,
    QComboBox, QLineEdit, QDialogButtonBox
)


class SettingsDialog(QDialog):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置")
        self.config = config
        self.widgets = {}
        form = QFormLayout(self)

        for f in fields(config):
            if f.name.startswith("_") or f.name in ("app_name", "version"):
                continue
            value = getattr(config, f.name)
            w = self._create_widget(f.type, f.name, value)
            self.widgets[f.name] = w
            form.addRow(f.name, w)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

    def _create_widget(self, ftype, name, value):
        if ftype == bool:
            w = QCheckBox()
            w.setChecked(value)
        elif ftype == int:
            w = QSpinBox()
            w.setRange(0, 999999)
            w.setValue(value)
        elif ftype == float:
            w = QDoubleSpinBox()
            w.setDecimals(4)
            w.setSingleStep(0.001)
            w.setValue(value)
        elif name == "mode":
            w = QComboBox()
            w.addItems(["vad", "window"])
            w.setCurrentText(value)
        else:
            w = QLineEdit(str(value))
        return w

    def get_config_dict(self):
        d = {}
        for name, w in self.widgets.items():
            if isinstance(w, QCheckBox):
                d[name] = w.isChecked()
            elif isinstance(w, QSpinBox):
                d[name] = w.value()
            elif isinstance(w, QDoubleSpinBox):
                d[name] = w.value()
            elif isinstance(w, QComboBox):
                d[name] = w.currentText()
            else:
                d[name] = w.text()
        return d