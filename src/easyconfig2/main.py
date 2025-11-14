import sys
from PyQt5.QtCore import Qt, QPointF, QSizeF, QTimer

from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QApplication, QPushButton

from easyconfig2.easyconfig import EasyConfig2, MultiConfig
from easyconfig2.easydependency import EasyPairDependency, EasyMandatoryDependency

app = QApplication(sys.argv)


class MainWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.v_layout = QVBoxLayout()
        self.setLayout(self.v_layout)

        self.config = EasyConfig2(filename="config.yaml")
        ss1 = self.config.root().addSubSection("ss1", immediate=True)
        ss1_str_1 = ss1.addString("ss1_string_1", default="ss1_string_1", base64=True,
                                  callback=lambda x: print("changed ss1_string_1"))
        ss1_str_2 = ss1.addString("ss1_string_2", default="ss1_string_2", base64=True)
        ss3 = ss1.addSubSection("ss3")
        ss3.addString("ss3_string_1", default="ss3_string_1", base64=True)
        ss3.addFloat("float", default="444", base64=True)
        ss3.addLabel("thislabel", pretty="jjjj", default="jjjj333")

        ss2 = self.config.root().addSubSection("ss2")
        ss2.addString("ss2_string_1", default="ss2_string_1")  # , base64=True)
        self.aa = ss2.addString("ss2_string_2", default="ss2_string_2")
        aaaa = ss2.addCheckbox("ss2_bool_1", default=True)
        aaaa = ss2.addCombobox("ss2_combo_1", items=["kakka", "pipi", "kuku"], default=1)

        self.config2 = EasyConfig2(filename="config.yaml", name="main_config2")
        ss1 = self.config2.root().addSubSection("ss1", immediate=True)
        # self.config2.save()
        # self.config.add_dependency(EasyMandatoryDependency(ss1_str_1, lambda x: x > 10))
        # self.config.add_dependency(EasyPairDependency(ss1_str_1, ss2, lambda x: x > 10))

        # self.config.load()

        self.mc = MultiConfig()
        self.mc.add("kakka", self.config)
        self.mc.add("pipi", self.config2)
        self.mc.load("kakka.yaml")

        # late_joiner_section = self.config.root().addSubSection("late_joiner")
        # late_joiner_section.addString("late_joiner_string", default="late_joiner_string")

        # self.config.populate(late_joiner_section)

        # self.config2 = EasyConfig2(filename="config.yaml", name="main_config2")
        # ss1 = self.config2.root().addSubSection("ss1")
        # ss1_str_1 = ss1.addString("ss1_string_1", default="ss1_string_1")
        # self.config2.load()
        # self.config2.save()
        # a = self.config.root().addSubSection("hola")
        # b = a.addString("hole", default="kkk")
        #
        # self.config.populate(a)
        #
        # print(b.get_value())
        #
        btn = QPushButton("Save")
        btn.clicked.connect(lambda: self.mc.save("ooo.yaml"))
        # btn.clicked.connect(lambda: self.config.get_collapsed_recursive(a))

        btn_load = QPushButton("Load")
        btn_load.clicked.connect(self.load)

        btn_edit = QPushButton("Edit")
        btn_edit.clicked.connect(lambda: self.config.edit())

        self.layout().addWidget(btn_load)
        self.layout().addWidget(btn)
        self.layout().addWidget(btn_edit)

        self.setMinimumWidth(200)

    def load(self):
        def do():
            self.config.load()

        QTimer.singleShot(2000, do)


a = MainWindow()
a.show()

app.exec()
