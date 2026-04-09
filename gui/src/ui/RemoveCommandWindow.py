from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLineEdit, QHBoxLayout, QPushButton

from src.command.DeviceStatus import DeviceStatus
from src.command.CommandScheduler import CommandScheduler
from src.command.CommandController import Command, CommandController, CommandDictionary
from src.ErrorMessage import Error

HEIGHT = 130
WIDTH = 400

class RemoveCommandWindow(QMainWindow):
    def __init__(self, update_plot):
        super().__init__()
        self.update_plot = update_plot

        self.setFixedSize(WIDTH, HEIGHT)
        self.setWindowTitle("Remove Command")

        container = QWidget()
        layout = QVBoxLayout(container)

        self.setCentralWidget(container)

        # Bottom 'Cancel' and 'Add' buttons

        bottom_button_container = QWidget(container)
        bottom_button_layout = QHBoxLayout(bottom_button_container)

        cancel_button = QPushButton('Cancel')
        cancel_button.setStyleSheet("text-align: center")
        cancel_button.clicked.connect(lambda: (self.clear_field(), self.close()))

        remove_button = QPushButton('Remove')
        remove_button.setStyleSheet("text-align: center")
        remove_button.clicked.connect(self.remove_command)

        bottom_button_layout.addWidget(cancel_button)
        bottom_button_layout.addWidget(remove_button)

        # End bottom buttons

        # Remove field

        self.remove_field = QLineEdit() 
        self.remove_field.setPlaceholderText("Enter command name to be removed.")

        # End of remove field

        layout.addWidget(self.remove_field)
        layout.addWidget(bottom_button_container)

    def clear_field(self) -> None:
        self.remove_field.setText("")

    def remove_command(self):
        command_name = self.remove_field.text()

        try:
            CommandScheduler.remove_command(command_name)
        except Error as err:
            err.call()
            return

        self.update_plot()
        self.clear_field()
        self.close()