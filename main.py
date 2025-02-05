import sys
from wsgiref.validate import validator

import yaml
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QDoubleValidator, QValidator, QIntValidator, QFontMetrics
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QApplication, QTreeWidget, QTreeWidgetItem, QPushButton, \
    QCheckBox, QComboBox, QSlider, QHBoxLayout, QLabel, QSizePolicy

from easyconfig import EasyConfig2
from easynodes import EasyFileDialog, PrivateNode, EasyList, EasyFileList
from easytree import EasyTree
from easynodes import (Subsection, EasyInputBox, EasyInt, EasyCheckBox, EasySlider, EasyComboBox, EasyFileDialogWidget)
#, EasyCheckBox, EasyComboBox, EasySlider)

app = QApplication(sys.argv)


class MainWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.v_layout = QVBoxLayout()
        self.setLayout(self.v_layout)

        self.config = EasyConfig2()

        ss1 = self.config.add(Subsection("ss1", immediate=True, save_if_none=False))
        ss2 = self.config.add(Subsection("ss2"))
        ss1.add_child(EasyList("Name1333", default=[1, 2, 3], validator=QIntValidator(0, 100), height=100))
        ss1.add_child(EasyFileList("Name13332", default=[1, 2, 3],  height=100))

        self.tl1 = ss1.add_child(EasyInputBox("Name1", validator=QDoubleValidator(0, 100, 2)))
        tl2 = ss1.add_child(EasyInputBox("Name2", validator=QDoubleValidator(0, 100, 2)))
        tl3 = ss1.add_child(EasyCheckBox("cab1", pretty = "Checkbox"))
        tl4 = ss1.add_child(EasyComboBox("cab12", pretty="Checkbox", items=["a", "b", "c"]))
        tl5 = ss1.add_child(EasySlider("cab13", pretty="Slider", default=-200, show_value=True))
        print("tl5 is ", tl5)
        tl6 = ss1.get_child("cab13", EasyInputBox("csab13", default=16))
        print("tl6 is ", tl6)

        ss1.add_child(EasyInputBox("Name2", default=17))
        ss1.add_child(EasyInt("Name3", default=18))
        ss1.add_child(EasyCheckBox("Name4", default=True))
        ss1.add_child(EasyFileDialog("Name5", type="dir"))
        ss1.add_child(PrivateNode("Name6", default={"a":[1,2,3]}))

        ss1.add_child(Subsection("ss3")).add_child(EasyInputBox("Name3", default="John3"))

        self.config.add_dependencies([(self.tl1, tl2, 12)])
        self.config.load("config.yaml")

        print("AAAAAAAAAAAAAA", tl5.get())

        btn = QPushButton("Save")
        btn.clicked.connect(lambda: self.config.save("config.yaml"))
        #btn.clicked.connect(lambda: self.config.get_collapsed_recursive(a))

        btn_load = QPushButton("Load")
        btn_load.clicked.connect(self.load)

        btn_edit = QPushButton("Edit")
        btn_edit.clicked.connect(lambda: self.config.edit())

        self.layout().addWidget(btn_load)
        self.layout().addWidget(btn)
        self.layout().addWidget(btn_edit)

        #self.tree = EasyTree(self.config.root, self.config.dependencies)
        #self.v_layout.addWidget(self.tree)

    def load(self):
        pass


a = MainWindow()
a.show()


app.exec()
