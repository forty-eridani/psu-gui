from PySide6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLineEdit
from PySide6.QtGui import QDoubleValidator 

from src.ErrorMessage import Error

class RealtimeSettingsWindow(QWidget):
    def __init__(self, set_rate, set_lookback):
        super().__init__()

        self.set_rate = set_rate
        self.set_lookback = set_lookback 

        layout = QVBoxLayout(self)

        self.setWindowTitle("Adjust Real Time Parameters")

        self.poll_rate_field = QLineEdit()
        self.poll_rate_field.setPlaceholderText("Polling Rate (polls per second)")
        self.poll_rate_field.setValidator(QDoubleValidator())

        self.lookback_field = QLineEdit()
        self.lookback_field.setPlaceholderText("Lookback Time (s)")
        self.lookback_field.setValidator(QDoubleValidator())

        # Bottom 'Cancel' and 'Add' buttons

        bottom_button_container = QWidget()
        bottom_button_layout = QHBoxLayout(bottom_button_container)

        cancel_button = QPushButton('Cancel')
        cancel_button.setStyleSheet("text-align: center")
        cancel_button.clicked.connect(self.close)

        add_button = QPushButton('Set Parameters')
        add_button.setStyleSheet("text-align: center")
        add_button.clicked.connect(self.update_params)

        bottom_button_layout.addWidget(cancel_button)
        bottom_button_layout.addWidget(add_button)

        # End bottom buttons

        layout.addWidget(self.poll_rate_field)
        layout.addWidget(self.lookback_field)
        layout.addWidget(bottom_button_container)
    
    def update_params(self):
        if self.poll_rate_field.text() == "":
            Error("Poll rate field cannot be empty.").call()
            return

        if self.lookback_field.text() == "":
            Error("Lookback field cannot be empty.").call()
            return

        self.set_rate(float(self.poll_rate_field.text()))
        self.set_lookback(float(self.lookback_field.text()))

        self.close()
