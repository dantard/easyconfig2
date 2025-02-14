from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QAbstractItemView

from easyconfig2.easynodes import EasySubsection
from easyconfig2.tripledict import TripleDict


class EasyTree(QTreeWidget):
    config_ok = pyqtSignal(bool)

    def __init__(self, node, dependencies):
        super().__init__()
        self.setColumnCount(2)
        self.node = node
        self.dependencies = dependencies
        self.items = TripleDict()
        self.populate(node)
        self.filter(node)
        self.header().setVisible(False)
        self.setSelectionMode(QAbstractItemView.NoSelection)
        self.expanded.connect(self.tree_expanded)
        self.collapsed.connect(self.tree_expanded)
        self.expanded.connect(lambda: self.resizeColumnToContents(0))

        proxy = self.model()
        for row in range(proxy.rowCount()):
            index = proxy.index(row, 0)
            self.expand(index)
        self.resizeColumnToContents(0)

    def tree_expanded(self):
        self.node.get_node("easyconfig/collapsed").set(self.get_collapsed_items())

    def update(self):
        state = self.get_collapsed_items()
        self.clear()
        self.items.clear()
        self.populate(self.node)
        self.filter(self.node)
        self.set_collapsed_items(state)

    def collect_widget_values(self):
        for node, (widget, _) in self.items.items1():
            if widget is not None:
                node.update_value(widget.get_value())

    def filter(self, node):
        for child in node.get_children():
            if isinstance(child, EasySubsection):
                # print(child.get_pretty(), child.is_hidden())
                _, item = self.items[child]
                item.setHidden(child.is_hidden())
                self.filter(child)
            else:
                _, item = self.items[child]
                item.setHidden(child.is_hidden())

    def create_item(self, node, parent):
        item = QTreeWidgetItem(parent)
        item.setText(0, node.get_pretty())
        widget = node.get_widget()
        if widget is not None:
            widget.widget_value_changed.connect(self.widget_value_changed)
            node._node_value_changed.connect(self.node_value_changed)
            self.setItemWidget(item, 1, widget)
        self.items.add(node, widget, item)
        return item

    def widget_value_changed(self, widget):
        node, _ = self.items.get(widget)
        if node.use_inmediate_update():
            node.update_value(widget.get_value())
        self.check_dependency(node)

    def node_value_changed(self, node):
        widget, _ = self.items.get(node)
        widget.set_value(node.get())
        self.check_dependency(node)

    def populate(self, node, parent=None):

        if parent is not None:
            parent = self.create_item(node, parent)
            # node.widget_value_changed.connect(lambda x=node, y=node: self.check_dependency(y))
        else:
            parent = self.invisibleRootItem()

        for child in node.get_children():
            if isinstance(child, EasySubsection):
                # if not child.is_hidden():
                self.populate(child, parent)
            else:
                # if not child.is_hidden():
                self.create_item(child, parent)
                # child.widget_value_changed.connect(lambda x=child, y=child: self.check_dependency(y))

    def get_collapsed_items(self):
        info = []

        def traverse(item):
            if item.childCount() == 0:
                return

            info.append("1" if item.isExpanded() else "0")
            for i in range(item.childCount()):
                traverse(item.child(i))

        traverse(self.invisibleRootItem())
        return "".join(info)

    def set_collapsed_items(self, info):
        if info is None:
            return

        info = list(info)

        def traverse(item, info2):
            if item.childCount() == 0:
                return
            if len(info2) == 0:
                return

            item.setExpanded(info2.pop(0) == "1")
            for i in range(item.childCount()):
                traverse(item.child(i), info2)

        traverse(self.invisibleRootItem(), info)

    def check_all_dependencies(self):
        for node in self.dependencies.keys():
            self.check_dependency(node)

    def check_dependency(self, node):
        # print("checking deps")
        deps = self.dependencies.get(node, [])
        for dep in deps:
            widget1, _ = self.items.get(dep.master)
            for slave in dep.slave:
                widget2, _ = self.items.get(slave)
                # print("Checking", dep.master.get_pretty(), dep.slave.get_pretty())
                widget2.set_enabled(dep.kind(widget1.get_value()))  # , widget2.get_value()))

        for widget in self.items.keys2():
            if widget is not None and not widget.is_ok():
                self.config_ok.emit(False)
                return

        self.config_ok.emit(True)
