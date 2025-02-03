from PyQt5.QtWidgets import QDialog, QVBoxLayout, QDialogButtonBox


class EasyDialog(QDialog):
    def __init__(self, widget, parent=None):
        super().__init__(parent)
        self.widget = widget
        self.v_layout = QVBoxLayout()
        self.setLayout(self.v_layout)
        self.v_layout.addWidget(widget)
        # add standard dialog buttonbox
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.v_layout.addWidget(self.buttonBox)

    def get_widget(self):
        return self.widget()