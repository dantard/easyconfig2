from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QAbstractItemView

from easyconfig2.easydependency import EasyPairDependency, EasyMandatoryDependency
from easyconfig2.easynodes import EasySubsection
from easyconfig2.easywidgets import EasySubsectionWidget
from easyconfig2.tripledict import TripleDict


class EasyTree(QTreeWidget):
    config_ok = pyqtSignal(bool)

    def __init__(self, node, dependencies):
        super().__init__()
        self.node = node
        self.dependencies = dependencies
        self.items = TripleDict()
        self.header().setVisible(False)
        self.setSelectionMode(QAbstractItemView.NoSelection)
        self.expanded.connect(self.tree_expanded)
        self.collapsed.connect(self.tree_expanded)
        self.expanded.connect(lambda: self.resizeColumnToContents(0))
        self.setColumnCount(2)

        # Populate the tree
        self.populate(node)
        # Hide the hidden nodes
        self.hide_hidden(node)

        proxy = self.model()
        for row in range(proxy.rowCount()):
            index = proxy.index(row, 0)
            self.expand(index)
        self.resizeColumnToContents(0)
        self.check_all_dependencies()

    def tree_expanded(self):
        self.node.get_node("easyconfig/collapsed").set(self.get_collapsed_items())

    def update(self):
        state = self.get_collapsed_items()
        self.clear()
        self.items.clear()
        self.populate(self.node)
        self.hide_hidden(self.node)
        self.set_collapsed_items(state)

    def collect_widget_values(self):
        for node, (widget, _) in self.items.items1():
            if widget is not None:
                node.update_value(widget.get_value())

    def hide_hidden(self, node):
        for child in node.get_children():
            if isinstance(child, EasySubsection):
                # print(child.get_pretty(), child.is_hidden())
                _, item = self.items[child]
                item.setHidden(child.is_hidden())
                self.hide_hidden(child)
            else:
                _, item = self.items[child]
                item.setHidden(child.is_hidden())

    def widget_value_changed(self, widget):
        node, _ = self.items.get(widget)
        if node.use_inmediate_update():
            node.update_value(widget.get_value())
        self.check_all_dependencies()

    def node_value_changed(self, node):
        widget, _ = self.items.get(node)
        widget.set_value(node.get())
        self.check_all_dependencies()

    def _create_widget_item(self, node, parent_item: QTreeWidgetItem):
        """Create the items of the tree and insert the widgets according to those
        returned by the nodes themselves. Also, store in the EasySubsectionWidget
        the children widgets, so they can be disabled when the parent is disabled.
        NOTE: it also connects the signals of the widgets to the corresponding of
        the nodes, so a node will be updated when the widget changes and vice versa.
        This process is carried out by widget_value_changed and node_value_changed methods."""

        item = QTreeWidgetItem(parent_item)
        item.setText(0, node.get_pretty())
        widget = node.get_widget()
        if widget is not None:
            if parent_item is not None and self.itemWidget(parent_item, 1) is not None:
                # Need to add the widget to the parent widget: it has to know
                # them in case we need to disable them when a section is disabled
                parent_widget: EasySubsectionWidget = self.itemWidget(parent_item, 1)
                parent_widget.add_child_widget(widget)

            widget.widget_value_changed.connect(self.widget_value_changed)
            node.node_value_changed.connect(self.node_value_changed)
            self.setItemWidget(item, 1, widget)
        self.items.add(node, widget, item)
        return item

    def populate(self, node, parent_item=None):
        """Populate the tree with the nodes of the configuration"""

        if parent_item is not None:
            parent_item = self._create_widget_item(node, parent_item)
        else:
            parent_item = self.invisibleRootItem()

        for child_node in node.get_children():
            if isinstance(child_node, EasySubsection):
                self.populate(child_node, parent_item)
            else:
                self._create_widget_item(child_node, parent_item)

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
        is_ok = True
        for node, deps in self.dependencies.items():
            is_ok = is_ok and self.check_node_dependencies(deps)
        self.config_ok.emit(is_ok)

    def check_node_dependencies(self, deps):
        # print("checking deps")
        conf_is_ok = True
        for dep in deps:
            widget1, item1 = self.items.get(dep.master)
            if isinstance(dep, EasyPairDependency):
                ok = dep.call(widget1.get_value())
                for slave in dep.get_slave():
                    widget2, item2 = self.items.get(slave)
                    widget2.set_enabled(ok)
            elif isinstance(dep, EasyMandatoryDependency):
                if not dep.call(widget1.get_value()):
                    conf_is_ok = False
                    item1.setForeground(0, Qt.red)
                else:
                    item1.setForeground(0, Qt.black)
        return conf_is_ok
