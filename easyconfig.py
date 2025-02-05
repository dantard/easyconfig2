import sys
from wsgiref.validate import validator

import yaml
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QDoubleValidator, QValidator, QIntValidator, QFontMetrics
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QApplication, QTreeWidget, QTreeWidgetItem, QPushButton, \
    QCheckBox, QComboBox, QSlider, QHBoxLayout, QLabel, QSizePolicy, QDialog, QDialogButtonBox

from easydialog import EasyDialog
from easynodes import Root, Subsection
from easytree import EasyTree


class EasyConfig2:

    def __init__(self):
        self.easyconfig_private = {}
        self.tree = None
        self.dependencies = {}
        self.root = Root()

    def add(self, node):
        self.root.add_child(node)
        return node

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

    def collect_widget_values(self, node):
        for child in node.get_children():
            if isinstance(child, Subsection):
                self.collect_widget_values(child)
            else:
                child.update_value(child.get_widget_value())


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

    def create_dictionary(self, node, values=None):
        # create a dictionary to store the values traversing the tree

        if values is None:
            values = {}
        # iterate over the children of the node
        for child in node.get_children():
            # if the child is a subsection, traverse it
            if isinstance(child, Subsection):
                if child.is_savable():
                    new_dict = {}
                    self.create_dictionary(child, new_dict)
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
        values = self.get_dictionary()
        with open(filename, "w") as f:
            yaml.dump(values, f)

    def get_dictionary(self):
        values = {}
        self.create_dictionary(self.root, values)
        return values

    def load(self, filename):
        with open(filename, "r") as f:
            values = yaml.safe_load(f)
            self.parse(values)




    def edit(self):
        dialog = EasyDialog(EasyTree(self.root))
        if dialog.exec_():
            self.collect_widget_values(self.root)
            self.save("config.yaml")


    def parse(self, values):
        self.distribute_values(self.root, values)
        print("distribute", self.transform_dict(values))
        # manage easyconfig private values
        # self.easyconfig_private = values.get("easyconfig", {})
        # collapsed = self.easyconfig_private.get("collapsed", None)
        # if collapsed:
        #     self.set_collapsed_recursive(collapsed)
        #
        # # Apply Hidden property at load time
        # hidden = self.easyconfig_private.get("hidden", [])
        # for node in hidden:
        #     self.root.get_node(node).set_hidden(True)
        #
        # # Apply Disabled property at load time
        # disabled = self.easyconfig_private.get("disabled", [])
        # for node in disabled:
        #     self.root.get_node(node).set_editable(False)

    def add_dependencies(self, dependencies):
        for master, slave, fun in dependencies:
            if self.dependencies.get(master, None) is None:
                self.dependencies[master] = []
            self.dependencies[master].append((slave, fun))



