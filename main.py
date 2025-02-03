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

    def set_hidden(self, hidden):
        self.hidden = hidden


    def hide(self, value):
        if self.item is not None:
            self.item.setHidden(value)

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

    def set_tree_item(self, tree, parent):
        self.item = QTreeWidgetItem(parent)
        self.item.setText(0, self.key)
        tree.setItemWidget(self.item, 1, self.get_widget())
        return self.item

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
            if (hidden:=dictionary.get("$hidden", None)) is not None:
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
            self.value = self.widget.text()
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
                self.value = self.widget.isChecked()
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
            self.value = self.widget.currentIndex()
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
        return self.widget

    def value_changed(self):
        self.value = self.slider.value()
        self.text.setText(str(self.value*self.den))
        self.on_change.emit(self)

    def get_arguments(self):
        return super().get_arguments() + ["min", "max", "den"]

app = QApplication(sys.argv)


class EasyConfig2:

    def __init__(self):
        self.easyconfig_private = {}
        self.tree = None
        self.dependencies = {}
        self.root = Root()

    def add(self, node):
        self.root.add_child(node)
        return node

    def hang(self, node, tree, parent):
        parent = node.set_tree_item(tree, parent) if parent else tree.invisibleRootItem()

        for child in node.get_children():
            if isinstance(child, Subsection):
                #if not child.is_hidden():
                self.hang(child, tree, parent)
            else:
                #if not child.is_hidden():
                child.set_tree_item(tree, parent)


    def filter(self, node):
        for child in node.get_children():
            if isinstance(child, Subsection):
                child.hide(child.is_hidden())
                self.filter(child)
            else:
                child.hide(child.is_hidden())



    def transform_dict(self, d):
        new_dict = {}
        for key, value in d.items():
            if ":" in key:
                main_key, suffix = key.split(":", 1)
            else:
                main_key, suffix = key, None

            if isinstance(value, dict):
                new_dict[main_key] = (self.transform_dict(value), suffix)
            else:
                new_dict[main_key] = (value, suffix)

        return new_dict


    def distribute_values(self, node, values):

        for child in node.get_children():
            if isinstance(child, Subsection):
                dictionary = values.get(child.get_key())
                self.distribute_values(child, dictionary)
                child.check_extended(dictionary)
            else:
                value = values.get(child.get_key())
                if isinstance(value, (int, float, str, bool)) or value is None:
                    child.set(value)
                # Manage the extended functionality of the value
                elif isinstance(value, dict):
                    child.check_extended(value)
                else:
                    raise ValueError("Invalid value")

    def collect_values(self, node, values=None):
        # create a dictionary to store the values traversing the tree

        if values is None:
            values = {}
        # iterate over the children of the node
        for child in node.get_children():
            # if the child is a subsection, traverse it
            if isinstance(child, Subsection):
                if child.is_savable():
                    new_dict = {}
                    self.collect_values(child, new_dict)
                    if child.extended:
                        new_dict["$hidden"] = child.is_hidden()
                        new_dict["$editable"] = child.editable
                    values[child.get_key()] = new_dict
            else:
                # if the child is a TextLine, store the value in the dictionary
                if child.is_savable():
                    if child.extended:
                        values[child.get_key()] = {"$value": child.get(), "$hidden": child.is_hidden(), "$editable": child.editable}
                    else:
                        values[child.get_key()] = child.get()


    def save(self, filename):
        values = self.get_dictionary(filename)
        with open(filename, "w") as f:
            yaml.dump(values, f)

    def get_dictionary(self, filename):
        values = {}
        self.collect_values(self.root, values)
        values["easyconfig"] = self.easyconfig_private
        values["easyconfig"]["collapsed"]=  self.get_collapsed_recursive()
        return values


    def create_tree(self, node):
        self.tree = QTreeWidget()
        self.tree.setColumnCount(2)
        self.hang(node, self.tree, None)
        self.filter(node)
        self.check_all_dependencies()
        return self.tree

    def load(self, filename):
        with open(filename, "r") as f:
            values = yaml.safe_load(f)
            self.parse(values)
        self.filter(self.root)

    def parse(self, values):
        self.distribute_values(self.root, values)
        print("distribute", self.transform_dict(values))


        # manage easyconfig private values
        self.easyconfig_private = values.get("easyconfig", {})
        collapsed = self.easyconfig_private.get("collapsed", None)
        if collapsed:
            self.set_collapsed_recursive(collapsed)

        # Apply Hidden property at load time
        hidden = self.easyconfig_private.get("hidden", [])
        for node in hidden:
            self.root.get_node(node).set_hidden(True)

        # Apply Disabled property at load time
        disabled = self.easyconfig_private.get("disabled", [])
        for node in disabled:
            self.root.get_node(node).set_editable(False)




    def add_dependencies(self, dependencies):
        def connect_signal(node):
            for child in node.get_children():
                if isinstance(child, Subsection):
                    connect_signal(child)
                else:
                    child.on_change.connect(self.on_change)
        connect_signal(self.root)

        for master, slave, fun in dependencies:
            if self.dependencies.get(master, None) is None:
                self.dependencies[master] = []
            self.dependencies[master].append((slave, fun))


    def on_change(self, node):
        self.check_dependency(node)

    def check_all_dependencies(self):
        for node in self.dependencies.keys():
            self.check_dependency(node)

    def check_dependency(self, node):
        deps = self.dependencies.get(node, [])
        for slave, fun in deps:
            if isinstance(fun, (int, float, str, bool)):
                slave.set_widget_enabled(node.get()!=fun)

    def get_collapsed_recursive(self):
        info = []
        def traverse(item):
            if item.childCount() == 0:
                return

            info.append("1" if item.isExpanded() else "0")
            for i in range(item.childCount()):
                traverse(item.child(i))

        traverse(self.tree.invisibleRootItem())
        return "".join(info)

    def set_collapsed_recursive(self, info):
        info = list(info)

        def traverse(item, info2):
            if item.childCount() == 0:
                return

            item.setExpanded(info2.pop(0)=="1")
            for i in range(item.childCount()):
                traverse(item.child(i), info2)

        traverse(self.tree.invisibleRootItem(), info)



class MainWindow(QWidget):



    def __init__(self):
        super().__init__()
        self.v_layout = QVBoxLayout()
        self.setLayout(self.v_layout)

        self.config = EasyConfig2()
        a = QTreeWidget()
        a.setColumnCount(2)

        ss1 = Subsection("ss1")
        ss2 = Subsection("ss2")

        self.config.add(ss1)
        self.config.add(ss2)

        tl1 = ss1.add_child(EasyInputBox("Name1", validator=QDoubleValidator(0, 100, 2)))
        tl2 = ss1.add_child(EasyCheckBox("cab1", pretty = "Checkbox"))
        tl3 = ss1.add_child(EasyComboBox("cab12", pretty="Checkbox", items=["a", "b", "c"]))
        tl3 = ss1.add_child(EasySlider("cab13", pretty="Slider"))
        ss2.add_child(EasyInputBox("Name2", default="John2"))


        ss1.add_child(Subsection("ss3", hidden=True)).add_child(EasyInputBox("Name3", default="John3"))

        self.config.add_dependencies([(tl1, tl2, "John")])

        btn = QPushButton("Save")
        btn.clicked.connect(lambda: self.config.save("config.yaml"))
        #btn.clicked.connect(lambda: self.config.get_collapsed_recursive(a))

        btn_load = QPushButton("Load")
        btn_load.clicked.connect(lambda: self.config.load("config.yaml"))

        self.layout().addWidget(btn_load)
        self.layout().addWidget(btn)

        tree = self.config.create_tree(self.config.root)
        self.v_layout.addWidget(tree)

a = MainWindow()
a.show()


app.exec()
