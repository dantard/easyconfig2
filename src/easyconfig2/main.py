import sys
from PyQt5.QtCore import Qt, QPointF, QSizeF, QTimer

from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QApplication, QPushButton

from easyconfig2.easyconfig import EasyConfig2
from easyconfig2.easydependency import EasyPairDependency, EasyMandatoryDependency

app = QApplication(sys.argv)


class MainWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.v_layout = QVBoxLayout()
        self.setLayout(self.v_layout)

        self.config = EasyConfig2(name="hello", encoded=True)

        ss1 = self.config.root().addSubSection("ss1")
        ss1_str_1 = ss1.addString("ss1_string", default="100", validator=QIntValidator())
        ss2 = self.config.root().addSubSection("ss2")
        ss2.addString("ss2_string_1", default="ss2_string_1", base64=True)
        self.aa = ss2.addString("ss2_string_2", default="ss2_string_2_dflt")

        self.config.add_dependency(EasyMandatoryDependency(ss1_str_1, lambda x: x > 10))
        self.config.add_dependency(EasyPairDependency(ss1_str_1, ss2, lambda x: x > 10))

        btn = QPushButton("Save")
        btn.clicked.connect(lambda: self.config.save("config.yaml"))
        # btn.clicked.connect(lambda: self.config.get_collapsed_recursive(a))

        btn_load = QPushButton("Load")
        btn_load.clicked.connect(self.load)

        btn_edit = QPushButton("Edit")
        btn_edit.clicked.connect(lambda: self.config.edit())

        self.layout().addWidget(btn_load)
        self.layout().addWidget(btn)
        self.layout().addWidget(btn_edit)

        self.setMinimumWidth(200)

        # self.tree = EasyTree(self.config.root, self.config.dependencies)
        # self.v_layout.addWidget(self.tree)

    def load(self):
        def do():
            self.config.load("config.yaml")
        QTimer.singleShot(2000, do)



a = MainWindow()
a.show()

app.exec()
