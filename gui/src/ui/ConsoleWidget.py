from PySide6.QtWidgets import QLabel, QWidget, QVBoxLayout, QLineEdit, QScrollArea
from PySide6.QtCore import Qt

from src.command.CommandController import CommandController
from src.ErrorMessage import Error

WIDTH = 750
HEIGHT = 250

class ConsoleWidget(QWidget):
    def __init__(self):
        super().__init__()
        console_layout = QVBoxLayout(self)

        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText("Type your command here")

        self.line_edit.returnPressed.connect(self.push_cmd)

        self.output = QLabel("Hello There\n")
        self.output.setMinimumHeight(HEIGHT)
        self.output.setStyleSheet("background-color: black; color: white; padding: 5px; font-family: \"Terminal\"; font-weight: bold;")
        self.output.setMinimumWidth(WIDTH)
        self.output.setAlignment(Qt.AlignmentFlag.AlignTop)

        scroll_area = QScrollArea()
        scroll_area.setWidget(self.output)

        console_layout.addWidget(scroll_area)
        console_layout.addWidget(self.line_edit)

    def push_cmd(self) -> None:
        full_command = self.line_edit.text() + "\r"
        self.output.setText(self.output.text() + "[USER] " + full_command[:-1] + '\n')

        try:
            response = CommandController.run_raw_command(full_command)
            self.output.setText(self.output.text() + "[DEVICE] " + response)
        except Error as err:
            err.call()

        self.clear_field()

    def clear_field(self) -> None:
        self.line_edit.setText("")
