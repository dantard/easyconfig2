from PyQt5.QtWidgets import QDialog, QVBoxLayout, QDialogButtonBox, QLineEdit, QLabel

from easyconfig2.easyutils import get_validator_type


class EasyDialog(QDialog):
    def __init__(self, tree, parent=None):
        super().__init__(parent)
        self.tree = tree
        self.tree.config_ok.connect(self.config_ok)
        self.v_layout = QVBoxLayout()
        self.setLayout(self.v_layout)
        self.v_layout.addWidget(tree)

        # add standard dialog buttonbox
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.v_layout.addWidget(self.buttonBox)

        self.tree.check_all_dependencies()

    def config_ok(self, state):
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(state)

    def get_collapsed(self):
        return self.tree.get_collapsed_items()

    def set_collapsed(self, state):
        self.tree.set_collapsed_items(state)

    def get_widget(self):
        return self.tree()

    def collect_widget_values(self):
        self.tree.collect_widget_values()


class InputDialog(QDialog):
    # dialog with a QLineEdit and standard buttons
    def __init__(self, current, validator=None, parent=None):
        super().__init__(parent)
        self.v_layout = QVBoxLayout()
        self.setLayout(self.v_layout)
        self.input = QLineEdit(current)
        self.input.textChanged.connect(self.validate)
        self.type = get_validator_type(validator)
        self.input.setValidator(validator)
        self.v_layout.addWidget(QLabel("Enter a value:"))
        self.v_layout.addWidget(self.input)
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.v_layout.addWidget(self.buttonBox)

    def validate(self):
        if self.input.hasAcceptableInput():
            self.input.setStyleSheet("color: black")
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
        else:
            self.input.setStyleSheet("color: red")
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)

    def get_value(self):
        return self.type(self.input.text())
