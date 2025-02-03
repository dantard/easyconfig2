import sys
from wsgiref.validate import validator

import yaml
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QDoubleValidator, QValidator, QIntValidator, QFontMetrics
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QApplication, QTreeWidget, QTreeWidgetItem, QPushButton, \
    QCheckBox, QComboBox, QSlider, QHBoxLayout, QLabel, QSizePolicy



class WidgetNode(QObject):

    on_change = pyqtSignal(object)

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

        if not self.check_kwargs():
            raise ValueError("Invalid keyword argument")

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
        self.set_widget_value(value)

    def update_value(self, value):
        self.value = value

    def get_key(self):
        return self.key

    def get_arguments(self):
        return ["pretty", "default", "editable", "save", "hidden"]

    def check_kwargs(self):

        for key in self.kwargs.keys():
            if key not in self.get_arguments():
                return False
        return True

    def set_item_visible(self, visible):
        if self.item is not None:
            self.item.setHidden(not visible)


    def get_widget_value(self):
        pass

    def set_widget_value(self, value):
        pass

    def set_widget_enabled(self, enabled):
        if self.widget is not None:
            self.widget.setEnabled(enabled)

    def get_widget(self):
        return None

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


class Subsection(WidgetNode):

        def __init__(self, key, **kwargs):
            super().__init__(key, **kwargs)
            self.node_children = []

        def add_child(self, child):
            self.node_children.append(child)
            return child

        def get_arguments(self):
            return ["pretty", "save", "hidden"]

        def get_children(self):
            return self.node_children

        def add_checkbox(self, key, **kwargs):
            return self.add_child(EasyCheckBox(key, **kwargs))

        def add_inputbox(self, key, **kwargs):
            return self.add_child(EasyInputBox(key, **kwargs))

        def add_combobox(self, key, **kwargs):
            return self.add_child(EasyComboBox(key, **kwargs))

        def add_slider(self, key, **kwargs):
            return self.add_child(EasySlider(key, **kwargs))

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

class EasyInputBox(WidgetNode):

        def __init__(self, name, **kwargs):
            super().__init__(name, **kwargs)
            self.validator = kwargs.get("validator", None)
            if kwargs.get("accept", None) is not None:
                if kwargs["accept"] == "float":
                    self.validator = QDoubleValidator()
                elif kwargs["accept"] == "int":
                    self.validator = QIntValidator()

        def get_widget_value(self):
            if self.widget is not None:
                return self.widget.text()

        def set_widget_value(self, value):
            if self.widget is not None:
                self.widget.blockSignals(True)
                self.widget.setText(str(value))
                self.widget.blockSignals(False)

        def get_arguments(self):
            return super().get_arguments() + ["validator", "accept"]

        def get_widget(self):
            self.widget: QLineEdit =  QLineEdit()
            self.widget.setValidator(self.validator)
            self.widget.setText(self.value)
            self.widget.setReadOnly(not self.editable)
            self.widget.textChanged.connect(self.value_changed)
            return self.widget

        def value_changed(self):
            if self.validator is not None and self.validator.validate(self.widget.text(), 0)[0] != QValidator.Acceptable:
                self.widget.setStyleSheet("color: red")
                return
            self.widget.setStyleSheet("color: black")
            self.on_change.emit(self)

        def set_editable(self, enabled):
            super().set_editable(enabled)
            if self.widget is not None:
                self.widget.setReadOnly(not enabled)

class EasyCheckBox(WidgetNode):

            def __init__(self, name, **kwargs):
                super().__init__(name, **kwargs)

            def get_widget_value(self):
                if self.widget is not None:
                    return self.widget.isChecked()

            def set_widget_value(self, value):
                if self.widget is not None:
                    self.widget.blockSignals(True)
                    self.widget.setChecked(value if value is not None else False)
                    self.widget.blockSignals(False)

            def get_widget(self):
                self.widget = QCheckBox()
                self.widget.setChecked(self.value if self.value is not None else False)
                self.widget.stateChanged.connect(self.value_changed)
                return self.widget

            def value_changed(self):
                self.on_change.emit(self)



class EasyComboBox(WidgetNode):

        def __init__(self, name, **kwargs):
            super().__init__(name, **kwargs)
            self.items = kwargs.get("items", [])

        def get_widget_value(self):
            if self.widget is not None:
                return self.widget.currentIndex()

        def set_widget_value(self, value):
            if self.widget is not None:
                self.widget.blockSignals(True)
                self.widget.setCurrentIndex(value if value is not None else 0)
                self.widget.blockSignals(False)

        def get_widget(self):
            self.widget = QComboBox()
            self.widget.addItems(self.items)
            self.widget.setCurrentIndex(self.value if self.value is not None else 0)
            self.widget.currentIndexChanged.connect(self.value_changed)
            return self.widget

        def value_changed(self):
            self.on_change.emit(self)

        def get_arguments(self):
            return super().get_arguments() + ["items"]

        def get_items(self):
            return self.items

class EasySlider(WidgetNode):

    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
        self.slider = None
        self.text = None
        self.min = kwargs.get("min", 0)
        self.max = kwargs.get("max", 100)
        self.den = kwargs.get("den", 1)


    def get_widget_value(self):
        if self.widget is not None:
            return self.slider.value()
        return None

    def set_widget_value(self, value):
        if self.widget is not None:
            self.slider.blockSignals(True)
            self.slider.setValue(value if value is not None else 0)
            self.slider.blockSignals(False)

    def get_widget(self):
        self.widget = QWidget()
        QWidget.setLayout( self.widget, QHBoxLayout())
        self.text = QLabel()
        self.slider = QSlider()
        self.slider.setOrientation(1)
        self.widget.layout().addWidget(self.text)
        self.widget.layout().addWidget(self.slider)
        # text length in points
        text_length = QFontMetrics(self.text.font()).boundingRect(str(self.max)).width()
        self.text.sizePolicy().setHorizontalPolicy(QSizePolicy.Minimum)
        self.text.setMinimumWidth(text_length)
        self.text.setMaximumWidth(text_length)
        self.slider.setValue(self.value if self.value is not None else 0)
        self.slider.valueChanged.connect(self.value_changed)
        self.text.setText(str(self.slider.value()*self.den))
        return self.widget

    def value_changed(self):
        self.text.setText(str(self.slider.value()*self.den))
        self.on_change.emit(self)

    def get_arguments(self):
        return super().get_arguments() + ["min", "max", "den"]