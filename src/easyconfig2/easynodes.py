import base64

from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QIntValidator, QDoubleValidator
from sympy.printing.cxx import reserved

from easyconfig2.easywidgets import EasyInputBoxWidget, EasyCheckBoxWidget, EasySliderWidget, EasyComboBoxWidget, \
    EasyFileDialogWidget, EasyListWidget, EasyFileListWidget, EasyEditBoxWidget, EasyPasswordEditWidget, \
    EasySubsectionWidget, EasyLabelWidget


class EasyNode(QObject):
    node_value_changed = pyqtSignal(object)
    value_changed = pyqtSignal(object)

    def __init__(self, key, **kwargs):
        super().__init__()
        self.extended = False
        self.kwargs = kwargs
        self.key = key
        self.widget = None
        self.item = None
        self.base64 = kwargs.get("base64", False)
        self.value = kwargs.get("default", None)
        # TODO: value can be a list :
        #  if self.base64:
        #    self.value = base64.b64encode(self.value.encode()).decode() if self.value is not None else None
        self.save = kwargs.get("save", True)
        self.hidden = kwargs.get("hidden", False)
        self.editable = kwargs.get("editable", True)
        self.pretty = kwargs.get("pretty", key)
        self.save_if_none = kwargs.get("save_if_none", True)
        self.callback = kwargs.get("callback", None)
        # self.immediate_update = kwargs.get("immediate", self.callback is not None)
        self.immediate_update = kwargs.get("immediate", False)
        self.father = None
        self.widget = None

        if not self.check_kwargs():
            raise ValueError("Invalid keyword argument")

    def get_widget(self):
        return self.widget

    def set_father(self, father):
        self.father = father

    # Push the kwargs down to the children
    # E.g. if a subsection is hidden, all children
    def update_kwargs(self, kwargs):
        self.save = kwargs.get("save", self.save)
        self.hidden = kwargs.get("hidden", self.hidden)
        self.editable = kwargs.get("editable", self.editable)
        self.immediate_update = kwargs.get("immediate", self.immediate_update)
        self.save_if_none = kwargs.get("save_if_none", self.save_if_none)

        # TODO: WARNING: ADDED 28/10/2025 may provoke some unexpected behavior
        self.kwargs.update(kwargs)

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

    def is_base64(self):
        return self.base64

    def get(self, default=None):
        return self.value if self.value is not None else default

    def is_savable_if_none(self):
        return self.save_if_none

    def set(self, value):
        self.value = value
        self.node_value_changed.emit(self)
        self.value_changed.emit(self)
        if self.callback is not None:
            self.callback(self.value)

    def set_silent(self, value):
        self.value = value
        self.node_value_changed.emit(self)

    def use_inmediate_update(self):
        return self.immediate_update

    def set_visible(self, tree, visible):
        pass

    def update_value(self, value):
        if self.value != value:
            # print("widget_changed_received: applying", value)
            self.value = value
            self.value_changed.emit(self)
            if self.callback is not None:
                self.callback(self.value)

    def get_key(self):
        return self.key

    def get_arguments(self):
        return ["pretty", "save", "hidden", "immediate", "default", "enabled", "save_if_none", "base64", "callback"]

    def check_kwargs(self):

        for key in self.kwargs.keys():
            if key not in self.get_arguments():
                return False
        return True

    def set_item_visible(self, visible):
        if self.item is not None:
            self.item.setHidden(not visible)

    def new_widget(self):
        return None

    # compatibility with the previous version
    def get_value(self):
        return self.get()

    def set_value(self, value):
        self.set(value)

    def set_callback(self, callback, run_now=False, set_immediate=True):
        self.callback = callback
        self.immediate_update = set_immediate
        if run_now and self.callback is not None:
            self.callback(self.value)


class EasyInputBox(EasyNode):

    def new_widget(self):
        self.widget = EasyInputBoxWidget(self.value, **self.kwargs)
        return self.widget

    def get_arguments(self):
        return super().get_arguments() + ["validator", "readonly", "font"]


class EasyEditBox(EasyNode):

    def new_widget(self):
        self.widget = EasyEditBoxWidget(self.value, **self.kwargs)
        return self.widget

    def get_arguments(self):
        return super().get_arguments() + ["readonly", "max_height", "font"]


class EasyLabel(EasyNode):

    def new_widget(self):
        self.widget = EasyLabelWidget(self.value, **self.kwargs)
        return self.widget

    def get_arguments(self):
        return super().get_arguments() + ["max_height", "font", "format"]


class EasyInt(EasyInputBox):

    def __init__(self, key, **kwargs):
        if "validator" in kwargs:
            raise ValueError("Cannot set validator for EasyInt")
        kwargs["validator"] = QIntValidator(kwargs.get("min", -2147483648), kwargs.get("max", 2147483647))
        super().__init__(key, **kwargs)

    def get_arguments(self):
        return super().get_arguments() + ["min", "max"]


class EasyFloat(EasyInputBox):

    def __init__(self, key, **kwargs):
        if "validator" in kwargs:
            raise ValueError("Cannot set validator for EasyFloat")
        kwargs["validator"] = QDoubleValidator(kwargs.get("min", -1.7976931348623157e+308),
                                               kwargs.get("max", 1.7976931348623157e+308), 4)
        super().__init__(key, **kwargs)

    def get_arguments(self):
        return super().get_arguments() + ["min", "max"]


class EasyPasswordEdit(EasyInputBox):

    def __init__(self, key, **kwargs):
        self.base64 = True
        super().__init__(key, **kwargs)

    def new_widget(self):
        self.widget = EasyPasswordEditWidget(self.value, **self.kwargs)
        return self.widget

    def get_arguments(self):
        return super().get_arguments() + ["readonly"]


class EasyCheckBox(EasyNode):
    def new_widget(self):
        self.widget = EasyCheckBoxWidget(self.value, **self.kwargs)
        return self.widget


class EasySlider(EasyNode):

    def new_widget(self):
        self.widget = EasySliderWidget(self.value, **self.kwargs)
        return self.widget

    def get_arguments(self):
        return super().get_arguments() + ["min", "max", "den", "format", "show_value", "justify", "align"]


class EasyComboBox(EasyNode):

    def get_items(self):
        return self.kwargs.get("items", [])

    def get_item(self, index):
        items = self.kwargs.get("items", [])
        return items[index] if index < len(items) else None

    def new_widget(self):
        self.widget = EasyComboBoxWidget(self.value, **self.kwargs)
        return self.widget

    def get_arguments(self):
        return super().get_arguments() + ["items", "editable", "mode_text", "validator"]


class EasyFileDialog(EasyNode):

    def new_widget(self):
        self.widget = EasyFileDialogWidget(self.value, **self.kwargs)
        return self.widget

    def get_arguments(self):
        return super().get_arguments() + ["type", "extension"]


class EasyPrivateNode(EasyNode):

    def __init__(self, key, **kwargs):
        super().__init__(key, **kwargs)
        self.hidden = True


class EasyList(EasyNode):

    def __init__(self, key, **kwargs):
        super().__init__(key, **kwargs)

    def get_arguments(self):
        return super().get_arguments() + ["validator", "height", "editable"]

    def new_widget(self):
        self.widget = EasyListWidget(self.value, **self.kwargs)
        return self.widget


class EasyFileList(EasyNode):

    def __init__(self, key, **kwargs):
        super().__init__(key, **kwargs)

    def get_arguments(self):
        return super().get_arguments() + ["type", "height"]

    def new_widget(self):
        self.widget = EasyFileListWidget(self.value, **self.kwargs)
        return self.widget


class EasySubsection(EasyNode):

    def __init__(self, key, **kwargs):
        super().__init__(key, **kwargs)
        self.node_children = []
        self.easyconfig = None

    def set_easyconfig(self, easyconfig):
        self.easyconfig = easyconfig

    def set_nested_attr(self, obj, attrs, value):

        class Dummy:
            pass

        for attr in attrs[:-1]:
            if not hasattr(obj, attr):
                setattr(obj, attr, Dummy())
            obj = getattr(obj, attr)
        setattr(obj, attrs[-1], value)

    def add_child(self, child):

        child.update_kwargs(self.kwargs)
        child.set_father(self)
        if isinstance(child, EasySubsection):
            child.set_easyconfig(self.easyconfig)
        else:

            # Create fields to be accessed like self.config.ss1.ss1_string_1
            fields = [child.get_key()]
            p = child.father
            while p is not None:
                fields.append(p.get_key())
                p = p.father
            fields.reverse()

            self.set_nested_attr(self.easyconfig, fields[1:], child)

            # field_key = ""
            # for f in fields:
            #     if not hasattr(self.easyconfig, f):
            #         setattr(self.easyconfig, f, None)
            #
            # for i, f in enumerate(fields[1:]):
            #     field_key += ("_" if i != 0 else "") + f
            # setattr(self.easyconfig, field_key, child)
            # print(field_key, "set to", child)

            # if hasattr(self.easyconfig, child.get_key()):
            #     print("WARNING: clash for key", child.get_key(), ":", getattr(self.easyconfig, child.get_key()),
            #           "owns it")
            # else:
            #     setattr(self.easyconfig, child.get_key(), child)

        self.node_children.append(child)
        return child

    def get_child(self, key, node=None):
        if key is None and node is not None:
            key = node.get_key()

        for child in self.node_children:
            if child.get_key() == key:
                return child
        if node is not None:
            return self.add_child(node)

        return None

    def new_widget(self):
        self.widget = EasySubsectionWidget(None, **self.kwargs)
        return self.widget

    def get_arguments(self):
        return ["pretty", "save", "hidden", "editable", "immediate", "save_if_none"]

    def get_children(self):
        return self.node_children

    def get_node(self, path):
        path = path.strip("/").split("/")

        # print("path", path)

        def get_node_recursive(node, path2):
            for child in node.node_children:
                if len(path2) == 1 and child.get_key() == path2[0]:
                    return child
                if isinstance(child, EasySubsection):
                    if child.get_key() == path2[0]:
                        return get_node_recursive(child, path2[1:])
            return None

        return get_node_recursive(self, path)

    # Utility function to add a subsection
    def addCombobox(self, key, **kwargs):
        node = EasyComboBox(key, **kwargs)
        self.add_child(node)
        return node

    #
    def addHidden(self, key, **kwargs):
        node = EasySubsection(key, **kwargs, hidden=True)
        self.add_child(node)
        return node

    #
    def addList(self, key, **kwargs):
        if self.hidden:
            node = EasyPrivateNode(key, **kwargs)
        else:
            node = EasyList(key, **kwargs)
        self.add_child(node)
        return node

    #
    def addCheckbox(self, key, **kwargs):
        node = EasyCheckBox(key, **kwargs)
        self.add_child(node)
        return node

    #
    def addFolderChoice(self, key, **kwargs):
        node = EasyFileDialog(key, **kwargs, type="dir")
        self.add_child(node)
        return node

    def addSubSection(self, key, **kwargs):
        node = EasySubsection(key, **kwargs)
        self.add_child(node)
        return node

    def addString(self, key, **kwargs):
        node = EasyInputBox(key, **kwargs)
        self.add_child(node)
        return node

    def addPassword(self, key, **kwargs):
        node = EasyPasswordEdit(key, **kwargs)
        self.add_child(node)
        return node

    def addSlider(self, key, **kwargs):
        node = EasySlider(key, **kwargs)
        self.add_child(node)
        return node

    def addEditBox(self, key, **kwargs):
        node = EasyEditBox(key, **kwargs)
        self.add_child(node)
        return node

    def addInt(self, key, **kwargs):
        node = EasyInt(key, **kwargs)
        self.add_child(node)
        return node

    def addFloat(self, key, **kwargs):
        node = EasyFloat(key, **kwargs)
        self.add_child(node)
        return node

    def addLabel(self, key, **kwargs):
        node = EasyLabel(key, **kwargs)
        self.add_child(node)
        return node

    def addFileList(self, key, **kwargs):
        node = EasyFileList(key, **kwargs)
        self.add_child(node)
        return node

    def addPrivate(self, key, **kwargs):
        node = EasyPrivateNode(key, **kwargs)
        self.add_child(node)
        return node

    def addFileChoice(self, key, **kwargs):
        node = EasyFileDialog(key, **kwargs, type="file")
        self.add_child(node)
        return node

    def getString(self, key, **kwargs):
        return self.get_child(key, EasyInputBox(key, **kwargs))

    def getSlider(self, key, **kwargs):
        return self.get_child(key, EasySlider(key, **kwargs))

    def getEditBox(self, key, **kwargs):
        return self.get_child(key, EasyEditBox(key, **kwargs))

    def getInt(self, key, **kwargs):
        return self.get_child(key, EasyInt(key, **kwargs))

    def getLabel(self, key, **kwargs):
        return self.get_child(key, EasyLabel(key, **kwargs))

    def getFloat(self, key, **kwargs):
        return self.get_child(key, EasyFloat(key, **kwargs))

    def getCheckBox(self, key, **kwargs):
        return self.get_child(key, EasyCheckBox(key, **kwargs))

    def getComboBox(self, key, **kwargs):
        return self.get_child(key, EasyComboBox(key, **kwargs))

    def getPassword(self, key, **kwargs):
        return self.get_child(key, EasyPasswordEdit(key, **kwargs))

    def getFolderChoice(self, key, **kwargs):
        return self.get_child(key, EasyFileDialog(key, **kwargs, type="dir"))

    def getFileChoice(self, key, **kwargs):
        return self.get_child(key, EasyFileDialog(key, **kwargs, type="file"))

    def getList(self, key, **kwargs):
        return self.get_child(key, EasyList(key, **kwargs))

    def getFileList(self, key, **kwargs):
        return self.get_child(key, EasyFileList(key, **kwargs))

    def getPrivate(self, key, **kwargs):
        return self.get_child(key, EasyPrivateNode(key, **kwargs))

    def getSubSection(self, key, **kwargs):
        return self.get_child(key, EasySubsection(key, **kwargs))


class Root(EasySubsection):
    def __init__(self, easyconfig, **kwargs):
        super().__init__("root", **kwargs)
        self.easyconfig = easyconfig
