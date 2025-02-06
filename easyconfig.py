import base64
import os

import yaml

from easydialog import EasyDialog
from easynodes import Root, Subsection, PrivateNode
from easytree import EasyTree


class EasyConfig2:

    def __init__(self):
        self.easyconfig_private = {}
        self.tree = None
        self.dependencies = {}
        self.root = Root()
        self.private = self.root.add_child(Subsection("easyconfig", hidden=True))
        self.collapsed = self.private.add_child(PrivateNode("collapsed", default=""))
        self.hidden = self.private.add_child(PrivateNode("hidden", default=None, save_if_none=False))
        self.disabled = self.private.add_child(PrivateNode("disabled", default=None, save_if_none=False))

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

    def distribute_values(self, node, values):

        for child in node.get_children():
            if isinstance(child, Subsection):
                dictionary = values.get(child.get_key())
                self.distribute_values(child, dictionary)
                child.check_extended(dictionary)
            else:
                value = values.get(child.get_key())
                child.set(value)

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
                    values[child.get_key()] = new_dict
            else:
                # if the child is a TextLine, store the value in the dictionary
                if child.is_savable():
                    if child.get() is not None or child.is_savable_if_none():
                        values[child.get_key()] = child.get()

    def save(self, filename, encoded=False):
        values = self.get_dictionary()
        if encoded:
            # encode in base64
            string = yaml.dump(values)
            string = base64.b64encode(string.encode()).decode()
            with open(filename, "w") as f:
                f.write(string)
        else:
            with open(filename, "w") as f:
                yaml.dump(values, f)

    def get_dictionary(self):
        values = {}
        self.create_dictionary(self.root, values)
        return values

    def load(self, filename, encoded=False):
        if os.path.exists(filename):
            with open(filename, "r") as f:
                if encoded:
                    string = f.read()
                    string = base64.b64decode(string).decode()
                    values = yaml.safe_load(string)
                else:
                    values = yaml.safe_load(f)

                self.parse(values)
                for key in self.hidden.get([]):
                    self.root.get_node(key).set_hidden(True)

    def edit(self):
        dialog = EasyDialog(EasyTree(self.root, self.dependencies))
        dialog.set_collapsed(self.collapsed.get())
        if dialog.exec():
            dialog.collect_widget_values()
            self.collapsed.set(dialog.get_collapsed())
            self.save("config.yaml")

    def parse(self, values):
        self.distribute_values(self.root, values)

    def add_dependencies(self, dependencies):
        for master, slave, fun in dependencies:
            if self.dependencies.get(master, None) is None:
                self.dependencies[master] = []
            self.dependencies[master].append((slave, fun))
