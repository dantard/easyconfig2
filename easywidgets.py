import sys
from wsgiref.validate import validator

import yaml
from PyQt5.QtCore import QObject, pyqtSignal, Qt
from PyQt5.QtGui import QDoubleValidator, QValidator, QIntValidator, QFontMetrics
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QApplication, QTreeWidget, QTreeWidgetItem, QPushButton, \
    QCheckBox, QComboBox, QSlider, QHBoxLayout, QLabel, QSizePolicy

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

class EasyNode(QObject):

    _node_value_changed = pyqtSignal(object)
    value_changed = pyqtSignal(object)

    def __init__(self, key, **kwargs):
        super().__init__()
        self.extended = False
        self.kwargs = kwargs
        self.key = key
        self.widget = None
        self.item = None
        self.value = kwargs.get("default", None)
        self.save = kwargs.get("save", True)
        self.hidden = kwargs.get("hidden", False)
        self.editable = kwargs.get("editable", True)
        self.pretty = kwargs.get("pretty", key)
        self.immediate_update = kwargs.get("immediate", False)

        if not self.check_kwargs():
            raise ValueError("Invalid keyword argument")

    # Push the kwargs down to the children
    # E.g. if a subsection is hidden, all children
    def update_kwargs(self, kwargs):
        self.save = kwargs.get("save", self.save)
        self.hidden = kwargs.get("hidden", self.hidden)
        self.editable = kwargs.get("editable", self.editable)
        self.immediate_update = kwargs.get("immediate", self.immediate_update)

    def get_pretty(self):
        return self.pretty

    def set_hidden(self, hidden):
        self.hidden = hidden

    def set_editable(self, enabled):
        self.editable = enabled


    def is_hidden(self):
        return self.hidden

    def is_savable(self):
        return self.save

    def get(self):
        return self.value

    def set(self, value):
        self.value = value
        self._node_value_changed.emit(self)
        self.value_changed.emit(self)

    def update_value(self, value):
        print("widget_changed_received", value)
        if self.immediate_update:
            print("widget_changed_received: applying", value)
            self.value = value
            self.value_changed.emit(self)

    def get_key(self):
        return self.key

    def get_arguments(self):
        return ["pretty", "save", "hidden", "immediate", "default", "enabled"]

    def check_kwargs(self):

        for key in self.kwargs.keys():
            if key not in self.get_arguments():
                return False
        return True

    def set_item_visible(self, visible):
        if self.item is not None:
            self.item.setHidden(not visible)

    def check_extended(self, dictionary):
        if (hidden := dictionary.get("$hidden", None)) is not None:
            self.set_hidden(hidden)
            self.extended = True

        if (editable := dictionary.get("$editable", None)) is not None:
            self.set_editable(editable)
            self.extended = True

        if (value := dictionary.get("$value", None)) is not None:
            self.set(value)
            self.extended = True
    def get_widget(self):
        return None


class Subsection(EasyNode):

        def __init__(self, key, **kwargs):
            super().__init__(key, **kwargs)
            self.node_children = []

        def add_child(self, child):
            child.update_kwargs(self.kwargs)
            self.node_children.append(child)
            return child

        def get_arguments(self):
            return ["pretty", "save", "hidden", "editable", "immediate"]

        def get_children(self):
            return self.node_children

        def get_node(self, path):
            path = path.strip("/").split("/")
            print("path", path)

            def get_node_recursive(node, path2):
                for child in node.node_children:
                    if len(path2) == 1 and child.get_key() == path2[0]:
                        return child
                    if isinstance(child, Subsection):
                        if child.get_key() == path2[0]:
                            return get_node_recursive(child, path2[1:])
                return None

            return get_node_recursive(self, path)

        def check_extended(self, dictionary):
            print("check extended", dictionary)
            if (hidden:=dictionary.get("$hidden", None)) is not None:
                print("hidden", "***")
                self.set_hidden(hidden)
                self.extended = True

            if (editable:=dictionary.get("$editable", None)) is not None:
                self.set_editable(editable)
                self.extended = True



class Root(Subsection):

    def __init__(self):
        super().__init__("root")

class EasyInputBox(EasyNode):

    def get_widget(self):
        return EasyInputBoxWidget(**self.kwargs)

    def get_arguments(self):
             return super().get_arguments() + ["validator", "readonly"]

class EasyInt(EasyInputBox):

    def __init__(self, key, **kwargs):
        if "validator" in kwargs:
            raise ValueError("Cannot set validator for EasyInt")
        kwargs["validator"] = QIntValidator(kwargs.get("min", -2147483648), kwargs.get("max", 2147483647))
        super().__init__(key, **kwargs)

    def get_arguments(self):
        return super().get_arguments() + ["min", "max"]

class EasyCheckBox(EasyNode):
    def get_widget(self):
        return EasyCheckBoxWidget(**self.kwargs)

class EasySlider(EasyNode):

    def get_widget(self):
        return EasySliderWidget(**self.kwargs)

    def get_arguments(self):
        return super().get_arguments() + ["min", "max", "den", "format", "show_value", "suffix", "align"]

class EasyComboBox(EasyNode):

    def get_items(self):
        return self.kwargs.get("items", [])

    def get_item(self, index):
        items = self.kwargs.get("items", [])
        return items[index] if index < len(items) else None

    def get_widget(self):
        return EasyComboBoxWidget(**self.kwargs)

    def get_arguments(self):
        return super().get_arguments() + ["items"]

#class Easy