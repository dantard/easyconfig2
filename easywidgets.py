import sys
from wsgiref.validate import validator

import yaml
from PyQt5.QtCore import QObject, pyqtSignal, Qt
from PyQt5.QtGui import QDoubleValidator, QValidator, QIntValidator, QFontMetrics
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QApplication, QTreeWidget, QTreeWidgetItem, QPushButton, \
    QCheckBox, QComboBox, QSlider, QHBoxLayout, QLabel, QSizePolicy, QStyle, QFileDialog


class EasyWidget(QWidget):
    widget_value_changed = pyqtSignal(object)

    def __init__(self, **kwargs):
        super().__init__()
        self.h_layout = QHBoxLayout()
        self.h_layout.setContentsMargins(3,3,3,3)
        self.setLayout(self.h_layout)
        self.default = kwargs.get("default", None)
        self.enabled = kwargs.get("enabled", True)

    def get_value(self):
        pass

    def set_value(self, value):
        pass

    def value_changed(self):
        self.widget_value_changed.emit(self)

    def set_enabled(self, enabled):
        pass

class EasyInputBoxWidget(EasyWidget):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.widget = QLineEdit()
        self.layout().addWidget(self.widget)
        self.validator = kwargs.get("validator", None)
        self.readonly = kwargs.get("readonly", False)

        if isinstance(self.validator, int):
            self.validator = QIntValidator()
            self.kind = int
        elif isinstance(self.validator, float):
            self.validator = QDoubleValidator()
            self.kind = float
        elif isinstance(self.validator, QIntValidator):
            self.kind = int
        elif isinstance(self.validator, QDoubleValidator):
            self.kind = float
        else:
            self.kind = str
        self.widget.setValidator(self.validator)
        self.widget.setReadOnly(self.readonly)
        self.widget.setEnabled(self.enabled)
        self.widget.textChanged.connect(self.value_changed)

        self.set_value(self.default)

    def get_value(self):
        if self.widget.text() != "":
            return self.kind(self.widget.text())
        return None

    def set_value(self, value):
        self.widget.blockSignals(True)
        self.widget.setText(str(value) if value is not None else "")
        self.widget.blockSignals(False)

    def value_changed(self):
        super().value_changed()
        if self.validator is not None and self.validator.validate(self.widget.text(), 0)[0] != QValidator.Acceptable:
            self.widget.setStyleSheet("color: red")
            return
        self.widget.setStyleSheet("color: black")

    def set_enabled(self, enabled):
        self.widget.setEnabled(enabled)

class EasyCheckBoxWidget(EasyWidget):

        def __init__(self,  **kwargs):
            super().__init__(**kwargs)
            self.widget = QCheckBox()
            self.widget.setEnabled(self.enabled)
            self.widget.setChecked(self.default if self.default is not None else False)
            self.widget.stateChanged.connect(self.value_changed)
            self.layout().addWidget(self.widget)

        def get_value(self):
            return self.widget.isChecked()

        def set_value(self, value):
            self.widget.blockSignals(True)
            self.widget.setChecked(value if value is not None else False)
            self.widget.blockSignals(False)

class EasySliderWidget(EasyWidget):

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.slider = QSlider()
            self.text = QLabel()
            if kwargs.get("align", Qt.AlignLeft) == Qt.AlignRight:
                self.layout().addWidget(self.slider)
                self.layout().addWidget(self.text)
            else:
                self.layout().addWidget(self.text)
                self.layout().addWidget(self.slider)

            self.slider.setOrientation(1)
            self.slider.setEnabled(self.enabled)
            self.slider.setMinimum(kwargs.get("min", -1000))
            self.slider.setMaximum(kwargs.get("max", 100))

            self.format = kwargs.get("format", ".0f")
            self.suffix = kwargs.get("suffix", "")
            self.den = kwargs.get("den", 1)
            self.show_value = kwargs.get("show_value", False)

            self.slider.setValue(self.default if self.default is not None else 0)
            self.slider.valueChanged.connect(self.value_changed)
            self.text.setText(str(self.slider.value()*self.den))
            self.text.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            text = str(self.slider.maximum()/self.den)
            max_value_formatted = format(float(text), self.format) + self.suffix

            text = str(self.slider.minimum() / self.den)
            min_value_formatted =  format(float(text), self.format) + self.suffix

            text_length = max(QFontMetrics(self.text.font()).boundingRect(max_value_formatted).width(),
                                QFontMetrics(self.text.font()).boundingRect(min_value_formatted).width())
            self.text.sizePolicy().setHorizontalPolicy(QSizePolicy.Minimum)
            self.text.setMinimumWidth(text_length)
            self.text.setMaximumWidth(text_length)
            self.text.setVisible(self.show_value)
            self.set_value(self.default)

        def get_value(self):
            return self.slider.value()

        def set_value(self, value):
            self.slider.blockSignals(True)
            self.slider.setValue(value if value is not None else 0)
            self.slider.blockSignals(False)
            self.text.setText(str(self.slider.value()*self.den))

        def value_changed(self):
            super().value_changed()
            self.text.setText(format(self.slider.value()/self.den, self.format) + self.suffix)

        def set_enabled(self, enabled):
            self.slider.setEnabled(enabled)

class EasyComboBoxWidget(EasyWidget):

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.widget = QComboBox()
            self.widget.addItems(kwargs.get("items", []))
            self.widget.setEnabled(self.enabled)
            self.widget.setCurrentIndex(self.default if self.default is not None else 0)
            self.widget.currentIndexChanged.connect(self.value_changed)
            self.layout().addWidget(self.widget)

        def get_value(self):
            return self.widget.currentIndex()

        def set_value(self, value):
            self.widget.blockSignals(True)
            self.widget.setCurrentIndex(value if value is not None else 0)
            self.widget.blockSignals(False)

        def set_enabled(self, enabled):
            self.widget.setEnabled(enabled)



class EasyFileDialogWidget(EasyWidget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = kwargs.get("type", "open")
        if self.type not in ["file", "dir"]:
            raise ValueError("Invalid type")
        self.widget = QLineEdit()
        self.btn = QPushButton()
        self.btn.setIcon(self.style().standardIcon(QStyle.SP_DialogOpenButton))
        self.btn_discard = QPushButton()
        self.btn_discard.setMaximumWidth(25)
        self.btn_discard.setIcon(self.style().standardIcon(QStyle.SP_DialogCancelButton))
        self.btn_discard.clicked.connect(self.discard)
        self.btn.setMaximumWidth(30)
        self.btn.clicked.connect(self.open_file)
        self.layout().addWidget(self.widget)
        self.layout().addWidget(self.btn)
        self.layout().addWidget(self.btn_discard)
        self.widget.setReadOnly(True)

    def open_file(self):
        if self.type == "file":
            file, ok = QFileDialog.getOpenFileName(self, "Open File", self.default)
        elif self.type == "dir":
            file = QFileDialog.getExistingDirectory(self, "Select Directory", self.default)
            ok = True
        else:
            ok, file = False, None

        if ok and file:
            self.widget.setText(file)
            self.widget_value_changed.emit(self)

    def discard(self):
        self.widget.setText("")
        self.widget_value_changed.emit(self)