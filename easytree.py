from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem

from easywidgets import Subsection


class EasyTree(QTreeWidget):

    def __init__(self, node):
        super().__init__()
        self.setColumnCount(2)
        self.node = node
        self.items = {}
        self.populate(node)
        self.filter(node)

    def update(self):
        state = self.get_collapsed_items()
        self.clear()
        self.items.clear()
        self.populate(self.node)
        self.filter(self.node)
        self.set_collapsed_items(state)

    def filter(self, node):
        for child in node.get_children():
            if isinstance(child, Subsection):
                print(child.get_pretty(), child.is_hidden())
                self.items[child].setHidden(child.is_hidden())
                self.filter(child)
            else:
                self.items[child].setHidden(child.is_hidden())


    def create_item(self, node, parent):
        item = QTreeWidgetItem(parent)
        item.setText(0, node.get_pretty())
        self.setItemWidget(item, 1, node.get_widget())
        self.items[node] = item
        return item


    def populate(self, node, parent=None):
        parent = self.create_item(node, parent) if parent else self.invisibleRootItem()

        for child in node.get_children():
            if isinstance(child, Subsection):
                #if not child.is_hidden():
                self.populate(child, parent)
            else:
                #if not child.is_hidden():
                self.create_item(child, parent)

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
        info = list(info)

        def traverse(item, info2):
            if item.childCount() == 0:
                return

            item.setExpanded(info2.pop(0)=="1")
            for i in range(item.childCount()):
                traverse(item.child(i), info2)

        traverse(self.invisibleRootItem(), info)