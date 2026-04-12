from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit
from PySide6.QtCore import Qt

WIDTH = 400
HEIGHT = 300

class OutputWindow(QWidget):
    def __init__(self):
        super().__init__()

        console_layout = QVBoxLayout(self)

        self.output = QTextEdit("")
        self.output.setMinimumHeight(HEIGHT)
        self.output.setStyleSheet("background-color: black; color: white; padding: 5px; font-family: \"Terminal\"; font-weight: bold;")
        self.output.setMinimumWidth(WIDTH)
        self.output.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.output.setReadOnly(True)

        console_layout.addWidget(self.output)

    def add_cmd(self, req: str, res: str) -> None:
        self.output.append("[USER] " + req + "[DEVICE] " + res)
        self.output.adjustSize()