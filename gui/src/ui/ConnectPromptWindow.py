from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QMainWindow, QPushButton, QLineEdit

from src.command.CommandController import CommandController
from src.ErrorMessage import Error

WIDTH = 385
HEIGHT = 120

class ConnectPromptWindow(QMainWindow):
    def __init__(self, on_connection):
        super().__init__()

        self.on_connection = on_connection

        self.setFixedSize(WIDTH, HEIGHT)
        self.setWindowTitle("Connect to Device")

        container = QWidget()
        layout = QVBoxLayout(container)

        self.setCentralWidget(container)

        # Bottom 'Cancel' and 'Add' buttons

        bottom_button_container = QWidget(container)
        bottom_button_layout = QHBoxLayout(bottom_button_container)

        cancel_button = QPushButton('Cancel')
        cancel_button.setStyleSheet("text-align: center")
        cancel_button.clicked.connect(lambda: (self.clear_field(), self.close()))

        remove_button = QPushButton('Connect')
        remove_button.setStyleSheet("text-align: center")
        remove_button.clicked.connect(self.connect_to_device)

        bottom_button_layout.addWidget(cancel_button)
        bottom_button_layout.addWidget(remove_button)

        # End bottom buttons

        # Remove field

        self.address_field = QLineEdit() 
        self.address_field.setPlaceholderText("Enter the address of the device (i.e. socket://192.168.0.15)")

        self.port_field = QLineEdit() 
        self.port_field.setPlaceholderText("Enter the port of the device")

        # End of remove field

        layout.addWidget(self.address_field)
        layout.addWidget(self.port_field)
        layout.addWidget(bottom_button_container)

    def clear_field(self) -> None:
        self.address_field.setText("")
        self.port_field.setText("")

    def connect_to_device(self):
        try:
            CommandController.connect(self.address_field.text(), self.port_field.text())
            self.clear_field()
            self.close()
            self.on_connection()
        except Error as err:
            err.call()
