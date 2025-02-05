from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QIntValidator

from easywidgets import EasyInputBoxWidget, EasyCheckBoxWidget, EasySliderWidget, EasyComboBoxWidget, EasyFileDialogWidget


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

        def get_child(self, key, default=None):
            if key is None and default is not None:
                key = default.get_key()

            for child in self.node_children:
                if child.get_key() == key:
                    return child
            if default is not None:
                return self.add_child(default)

            return None


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

class EasyFileDialog(EasyNode):

    def get_widget(self):
        return EasyFileDialogWidget(**self.kwargs)

    def get_arguments(self):
        return super().get_arguments() + ["type"]