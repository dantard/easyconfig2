from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QDoubleValidator, QValidator, QIntValidator, QFontMetrics, QFont
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, \
    QCheckBox, QComboBox, QSlider, QHBoxLayout, QLabel, QSizePolicy, QStyle, QFileDialog, QListWidget, QMessageBox, \
    QPlainTextEdit

from easyconfig2.easydialog import InputDialog
from easyconfig2.easyutils import get_validator_type, get_validator_from_type


class EasyWidget(QWidget):
    widget_value_changed = pyqtSignal(object)

    def __init__(self, value, **kwargs):
        super().__init__()
        self.h_layout = QHBoxLayout()
        self.h_layout.setContentsMargins(3, 3, 3, 3)
        self.setLayout(self.h_layout)
        self.default = value if value is not None else kwargs.get("default")
        self.enabled = kwargs.get("enabled", True)
        self.list_widget = None

    def is_ok(self):
        return True

    def get_value(self):
        pass

    def set_value(self, value):
        pass

    def value_changed(self):
        self.widget_value_changed.emit(self)

    def set_enabled(self, enabled):
        pass


class EasySubsectionWidget(EasyWidget):
    """This class is like a container for the children widgets
        in case we need to disable all of them at once"""

    def __init__(self, value, **kwargs):
        super().__init__(value, **kwargs)
        self.children = []
        # self.layout().addWidget(QPushButton("Subsection"))

    def add_child_widget(self, child):
        self.children.append(child)

    def set_enabled(self, enabled):
        for child in self.children:
            child.set_enabled(enabled)


class EasyInputBoxWidget(EasyWidget):

    def __init__(self, value, **kwargs):
        super().__init__(value, **kwargs)
        self.validated = True
        self.widget = QLineEdit()
        self.layout().addWidget(self.widget)
        self.validator = kwargs.get("validator", None)
        self.readonly = kwargs.get("readonly", False)
        self.my_font = kwargs.get("font", None)
        if self.my_font is not None:
            self.widget.setFont(self.my_font)

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
        self.widget.textChanged.connect(self.validate)

        # ####### WARNING: this signal is emitted ONLY if the text is valid ######
        self.widget.returnPressed.connect(self.value_changed)

        self.set_value(self.default)

    def validate(self):
        if self.validator is not None:
            state, _, _ = self.validator.validate(self.widget.text(), 0)
            if state == QValidator.Acceptable:
                self.widget.setStyleSheet("color: gray")
            else:
                self.widget.setStyleSheet("color: red")

    def get_value(self):
        if self.widget.text() != "":
            return self.kind(self.widget.text())
        return None

    def set_value(self, value):
        self.widget.blockSignals(True)
        self.widget.setText(str(value) if value is not None else "")
        self.widget.blockSignals(False)

    def value_changed(self):

        # if self.validator is not None and self.validator.validate(self.widget.text(), 0)[0] != QValidator.Acceptable:
        #     self.widget.setStyleSheet("color: red")
        #     self.validated = False
        # else:
        #     self.widget.setStyleSheet("color: black")
        #     self.validated = True
        self.widget.setStyleSheet("color: black")
        super().value_changed()

    def is_ok(self):
        return self.validated

    def set_enabled(self, enabled):
        self.widget.setEnabled(enabled)


class EasyLabelWidget(EasyWidget):
    def __init__(self, value, **kwargs):
        super().__init__(value, **kwargs)
        self.widget = QLabel()
        self.layout().addWidget(self.widget)
        self.max_height = kwargs.get("max_height", 100)
        self.my_font = kwargs.get("font", None)
        self.format = kwargs.get("format", "{}")
        if self.my_font is not None:
            self.widget.setFont(self.my_font)
        self.set_value(self.default)

    def get_value(self):
        if self.widget.text() != "":
            return self.widget.text()
        return None

    def set_value(self, value):
        self.widget.blockSignals(True)
        self.widget.setText(self.format.format(value) if value is not None else "")
        self.widget.blockSignals(False)

    def set_enabled(self, enabled):
        self.widget.setEnabled(enabled)


class EasyEditBoxWidget(EasyWidget):

    def __init__(self, value, **kwargs):
        super().__init__(value, **kwargs)
        self.widget = QPlainTextEdit()
        self.layout().addWidget(self.widget)
        self.readonly = kwargs.get("readonly", False)
        self.max_height = kwargs.get("max_height", 100)
        self.my_font = kwargs.get("font", None)
        self.setMaximumHeight(self.max_height)
        if self.my_font is not None:
            self.widget.setFont(self.my_font)

        self.widget.setReadOnly(self.readonly)
        self.widget.textChanged.connect(self.value_changed)

        self.set_value(self.default)

    def get_value(self):
        if self.widget.toPlainText() != "":
            return self.widget.toPlainText()
        return None

    def set_value(self, value):
        self.widget.blockSignals(True)
        self.widget.setPlainText(str(value) if value is not None else "")
        self.widget.blockSignals(False)

    def set_enabled(self, enabled):
        self.widget.setEnabled(enabled)


class EasyPasswordEditWidget(EasyInputBoxWidget):
    def __init__(self, value, **kwargs):
        super().__init__(value, **kwargs)
        self.widget.setEchoMode(QLineEdit.Password)


class EasyCheckBoxWidget(EasyWidget):

    def __init__(self, value, **kwargs):
        super().__init__(value, **kwargs)
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
    class MySlider(QSlider):
        def wheelEvent(self, e):
            e.ignore()

    class ClickableText(QLabel):
        clicked = pyqtSignal()

        def mouseDoubleClickEvent(self, a0):
            super().mouseDoubleClickEvent(a0)
            self.clicked.emit()

    def __init__(self, value, **kwargs):
        super().__init__(value, **kwargs)
        self.slider = self.MySlider()
        self.text = self.ClickableText()
        self.text.clicked.connect(self.set_manual_value)
        if kwargs.get("align", Qt.AlignLeft) == Qt.AlignRight:
            self.layout().addWidget(self.slider)
            self.layout().addWidget(self.text)
        else:
            self.layout().addWidget(self.text)
            self.layout().addWidget(self.slider)

        self.slider.setOrientation(1)
        self.slider.setEnabled(self.enabled)
        self.slider.setMinimum(kwargs.get("min", 0))
        self.slider.setMaximum(kwargs.get("max", 100))
        self.jusify = kwargs.get("justify", "right")

        self.format = kwargs.get("format", "{:.3f}")
        self.den = kwargs.get("den", 1)
        self.show_value = kwargs.get("show_value", False)

        self.slider.setValue(int(self.default if self.default is not None else 0))
        self.slider.valueChanged.connect(self.value_changed)
        self.text.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.update_width()
        self.text.setVisible(self.show_value)
        self.set_value(self.default)

    def update_width(self):
        max_value_formatted = self.format.format(self.slider.maximum() / self.den)
        min_value_formatted = self.format.format(self.slider.minimum() / self.den)
        text_length = max(QFontMetrics(self.text.font()).boundingRect(max_value_formatted).width(),
                          QFontMetrics(self.text.font()).boundingRect(min_value_formatted).width())
        self.text.sizePolicy().setHorizontalPolicy(QSizePolicy.Minimum)
        self.text.setMinimumWidth(int(text_length))
        self.text.setMaximumWidth(int(text_length))

    def set_manual_value(self):
        dialog = InputDialog(str(self.get_value()), validator=QDoubleValidator())
        if dialog.exec_():
            try:
                val = float(dialog.input.text())
                self.set_value(val)
                self.value_changed()
                self.update_text()
            except:
                pass

    def get_value(self):
        return self.slider.value() / self.den

    def set_value(self, value):
        self.slider.blockSignals(True)
        self.slider.setValue(int(self.den * (value if value is not None else 0)))
        self.slider.blockSignals(False)
        self.update_text()

    def value_changed(self):
        super().value_changed()
        self.update_text()

    def update_text(self):
        self.text.setText(self.format.format(self.slider.value() / self.den))
        # self.text.setText(format(self.slider.value() / self.den, self.format) + self.suffix)

    def set_enabled(self, enabled):
        self.slider.setEnabled(enabled)

    def update(self, **kwargs):
        self.slider.setMinimum(kwargs.get("min", self.slider.minimum()))
        self.slider.setMaximum(kwargs.get("max", self.slider.maximum()))
        self.format = kwargs.get("format", self.format)
        self.den = kwargs.get("den", self.den)
        self.update_width()


class EasyComboBoxWidget(EasyWidget):
    class MyComboBox(QComboBox):
        def wheelEvent(self, e):
            e.ignore()

    def __init__(self, value, **kwargs):
        super().__init__(value, **kwargs)
        self.widget = self.MyComboBox()
        self.widget.addItems(kwargs.get("items", []))
        self.widget.setEnabled(self.enabled)
        self.widget.setEditable(kwargs.get("editable", False))
        self.mode_text = kwargs.get("mode_text", False)
        self.widget.setCurrentIndex(self.default if self.default is not None else 0)
        self.widget.currentIndexChanged.connect(self.value_changed)
        self.layout().addWidget(self.widget)
        self.validator = kwargs.get("validator", None)
        if self.widget.isEditable():
            if self.validator is not None:
                self.widget.lineEdit().setValidator(self.validator)
                self.widget.lineEdit().textChanged.connect(self.validate)
            self.widget.lineEdit().returnPressed.connect(self.value_changed)

    def validate(self):
        state, _, _ = self.validator.validate(self.widget.lineEdit().text(), 0)
        if state == QValidator.Acceptable:
            self.widget.setStyleSheet("color: gray")
        else:
            self.widget.setStyleSheet("color: red")

    def get_value(self):
        if self.mode_text:
            return self.widget.currentText()
        else:
            return self.widget.currentIndex()

    def set_value(self, value):
        self.widget.blockSignals(True)
        if self.mode_text:
            self.widget.setCurrentText(str(value) if value is not None else "")
        else:
            self.widget.setCurrentIndex(value if value is not None else 0)
        self.widget.blockSignals(False)
        self.widget.setStyleSheet("color: black")

    def set_enabled(self, enabled):
        self.widget.setEnabled(enabled)

    def value_changed(self):
        super().value_changed()
        self.widget.setStyleSheet("color: black")


class EasyFileDialogWidget(EasyWidget):
    def __init__(self, value, **kwargs):
        super().__init__(value, **kwargs)
        self.type = kwargs.get("type", "file")
        if self.type not in ["file", "dir"]:
            raise ValueError("Invalid type")
        self.extension = kwargs.get("extension", "")
        self.widget = QLineEdit()
        self.widget.setText(self.default)
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
            file, ok = QFileDialog.getOpenFileName(self, "Open File", self.default, self.extension)
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

    def get_value(self):
        return self.widget.text()

    def set_value(self, value):
        self.widget.setText(value)


class EasyBasicListWidget(EasyWidget):
    def __init__(self, value, **kwargs):
        super().__init__(value, **kwargs)
        # get parameters
        self.widget_height = kwargs.get("height", 50)
        self.editable = kwargs.get("editable", True)
        self.type = str

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.widget = QWidget()
        self.widget.setLayout(layout)
        self.widget.setContentsMargins(0, 0, 0, 0)

        button_add = QPushButton("+")
        button_del = QPushButton("−")
        button_edit = QPushButton("✎")
        button_add.clicked.connect(self.add_item)
        button_edit.clicked.connect(self.edit_item)
        button_del.clicked.connect(self.del_item)

        for button in [button_add, button_del, button_edit]:
            button.setFixedSize(25, 25)
            button.setStyleSheet("font-size: 14px")

        h_layout = QHBoxLayout()
        h_layout.addWidget(button_add)
        h_layout.addWidget(button_edit)
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        h_layout.addWidget(spacer)
        h_layout.addWidget(button_del)
        h_layout.setAlignment(Qt.AlignLeft)

        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        if self.editable:
            layout.addLayout(h_layout)

        if self.default is not None:
            self.list_widget.addItems([str(i) for i in self.default])
        self.list_widget.setFont(QFont("Courier New", 10))
        self.list_widget.setMaximumHeight(self.widget_height)

        self.layout().addWidget(self.widget)

    def ask_value(self):  # retry submit
        current = self.list_widget.currentItem().text() if self.list_widget.currentItem() is not None else ""
        dialog = InputDialog(current)
        if dialog.exec_():
            return dialog.input.text()
        return None

    def add_item(self):
        value = self.ask_value()
        if value is not None:
            self.list_widget.addItem(str(value))
            self.widget_value_changed.emit(self)

    def del_item(self):
        reply = QMessageBox.question(None, "Confirm", "Are you sure?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.No:
            return
        if self.list_widget.currentItem():
            self.list_widget.takeItem(self.list_widget.currentRow())
            self.widget_value_changed.emit(self)

    def edit_item(self):
        if self.list_widget.currentItem():
            value = self.ask_value()
            if value:
                self.list_widget.currentItem().setText(value)
                self.widget_value_changed.emit(self)

    def get_value(self):
        return [self.type(self.list_widget.item(i).text()) for i in range(self.list_widget.count())]

    def set_value(self, value):
        self.list_widget.clear()
        if value is not None:
            self.list_widget.addItems(value)


class EasyListWidget(EasyBasicListWidget):
    def __init__(self, value, **kwargs):
        super().__init__(value, **kwargs)
        # Establish validator
        self.validator = kwargs.get("validator", None)
        if self.validator is not None:
            self.type = get_validator_type(self.validator)
        else:
            if self.default is None:
                types = set()
            else:
                types = set([type(e) for e in self.default])

            if len(types) == 0:
                pass
            elif len(types) == 1:
                self.type = types.pop()
                self.validator = get_validator_from_type(self.type)
            else:
                raise ValueError("Mixed types in default list")

    def ask_value(self):  # retry submit
        current = self.list_widget.currentItem().text() if self.list_widget.currentItem() is not None else ""
        dialog = InputDialog(current, self.validator)
        if dialog.exec_():
            return dialog.input.text()
        return None


class EasyFileListWidget(EasyBasicListWidget):
    def __init__(self, value, **kwargs):
        super().__init__(value, **kwargs)
        self.kind = kwargs.get("type", "file")
        if self.kind not in ["file", "dir"]:
            raise ValueError("Invalid type")

    def ask_value(self):
        current = self.list_widget.currentItem().text() if self.list_widget.currentItem() is not None else ""
        if self.kind == "file":
            file, ok = QFileDialog.getOpenFileName(self, "Open File", current)
        elif self.kind == "dir":
            file = QFileDialog.getExistingDirectory(self, "Select Directory", current)
            ok = True
        else:
            ok, file = False, None

        if ok and file:
            return file
        return None
