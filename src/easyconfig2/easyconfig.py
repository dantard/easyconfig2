import base64
import os
import textwrap

import yaml

from easyconfig2.easydialog import EasyDialog
from easyconfig2.easynodes import Root, EasySubsection, EasyPrivateNode
from easyconfig2.easytree import EasyTree


class EasyConfig2:

    def __init__(self, **kwargs):
        self.easyconfig_private = {}
        self.tree = None
        self.dependencies = {}
        self.root_node = Root(**kwargs)
        self.private = self.root_node.add_child(EasySubsection("easyconfig", hidden=True))
        self.collapsed = self.private.add_child(EasyPrivateNode("collapsed", default=""))
        self.hidden = self.private.add_child(EasyPrivateNode("hidden", default=None, save_if_none=False))
        self.disabled = self.private.add_child(EasyPrivateNode("disabled", default=None, save_if_none=False))

    def root(self):
        return self.root_node

    def add(self, node):
        self.root_node.add_child(node)
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

    def create_dictionary(self, node, values=None):
        # create a dictionary to store the values traversing the tree

        if values is None:
            values = {}
        # iterate over the children of the node
        for child in node.get_children():
            # if the child is a subsection, traverse it
            if isinstance(child, EasySubsection):
                if child.is_savable():
                    new_dict = {}
                    self.create_dictionary(child, new_dict)
                    values[child.get_key()] = new_dict
            else:
                # if the child is a TextLine, store the value in the dictionary
                if child.is_savable():
                    if child.get() is not None or child.is_savable_if_none():
                        if child.is_base64() and child.get() is not None:
                            # Encode in base64 if required
                            # NOTE: we use yaml to dump the value to ensure that
                            # the value is stored according to the type it has and
                            # to take into account that might be a list or a dict
                            encoded = base64.b64encode(yaml.dump(child.get()).encode()).decode()
                            encoded = " ".join(textwrap.wrap(encoded, 80))
                            values[child.get_key()] = encoded
                        else:
                            values[child.get_key()] = child.get()

    def save(self, filename, encoded=False):
        print("saving")
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
        self.create_dictionary(self.root_node, values)
        return values

    def load(self, filename, emit=False, encoded=False):
        if os.path.exists(filename):
            with open(filename, "r") as f:
                if encoded:
                    string = f.read()
                    string = base64.b64decode(string).decode()
                    values = yaml.safe_load(string)
                else:
                    values = yaml.safe_load(f)

                self.parse(values, emit)
                # print("Loaded values", filename, values)
                for key in self.hidden.get([]):
                    self.root_node.get_node(key).set_hidden(True)

    def edit(self, min_width=None, min_height=None):
        dialog = EasyDialog(EasyTree(self.root_node, self.dependencies))
        if min_width is not None:
            dialog.setMinimumWidth(min_width)
        if min_height is not None:
            dialog.setMinimumHeight(min_height)

        dialog.set_collapsed(self.collapsed.get())
        if dialog.exec():
            dialog.collect_widget_values()
            self.collapsed.set(dialog.get_collapsed())
            return True
        return False

    def parse(self, dictionary, emit=False):

        def parse_recursive(node, values):
            for child in node.get_children():
                if isinstance(child, EasySubsection):
                    inner_dict = values.get(child.get_key(), {})
                    parse_recursive(child, inner_dict)
                else:
                    value = values.get(child.get_key())
                    # Decode base64 if needed
                    if child.is_base64() and value is not None:
                        value = value.replace(" ", "")
                        value = yaml.safe_load(base64.b64decode(value))

                    # TODO: Decision made here
                    if not emit:
                        child.value = value
                    else:
                        child.set(value)

        parse_recursive(self.root_node, dictionary)

    def add_dependencies(self, dependencies):
        for dep in dependencies:
            self.add_dependency(dep)

    def add_dependency(self, dep):
        if self.dependencies.get(dep.master, None) is None:
            self.dependencies[dep.master] = []
        self.dependencies[dep.master].append(dep)
