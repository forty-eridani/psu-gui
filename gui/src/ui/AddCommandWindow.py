from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLineEdit, QHBoxLayout, QPushButton, QComboBox, QCheckBox
from PySide6.QtGui import QDoubleValidator

from src.command.CommandScheduler import CommandScheduler
from src.command.CommandController import CommandDictionary
from src.ErrorMessage import Error

HEIGHT = 225
WIDTH = 400

class AddCommandWindow(QMainWindow):
    def __init__(self, update_plot):
        super().__init__()
        self.update_plot = update_plot

        self.setWindowTitle("Add Command")
        self.setFixedSize(WIDTH, HEIGHT)

        container = QWidget()
        self.setCentralWidget(container)
        
        main_layout = QVBoxLayout(container)

        # Fields

        fields_container = QWidget(container)
        fields_layout = QVBoxLayout(fields_container)

        self.name_field = QLineEdit()
        self.name_field.setPlaceholderText("Command Name")

        self.command_field = QComboBox()
        self.command_field.addItems(CommandDictionary.keys())  
        self.command_field.setStyleSheet("combobox-popup: 0;") # A solution to entire dropdown appearing
                                                               # I found off of a 15 year old QT forum thread

        self.command_field.currentIndexChanged.connect(self.set_hidden)

        self.time_field = QLineEdit()
        self.time_field.setValidator(QDoubleValidator())
        self.time_field.setPlaceholderText("Time (s)")

        arg_container = QWidget(fields_container)
        arg_layout = QHBoxLayout(arg_container)
        
        self.arg_field = QLineEdit()
        self.arg_field.setPlaceholderText("Argument for command")
        self.arg_field.setDisabled(True)

        self.step = QCheckBox("Step")
        self.step.setToolTip("If selected, command will generate intermediate commands that step to this command.")
        self.should_step = self.step.isChecked()
        self.step.stateChanged.connect(self.set_step)

        arg_layout.addWidget(self.arg_field)
        arg_layout.addWidget(self.step)

        fields_layout.addWidget(self.name_field)
        fields_layout.addWidget(self.command_field)
        fields_layout.addWidget(self.time_field)
        fields_layout.addWidget(arg_container)

        self.set_hidden()

        # End fields

        # Bottom 'Cancel' and 'Add' buttons

        bottom_button_container = QWidget(container)
        bottom_button_layout = QHBoxLayout(bottom_button_container)

        cancel_button = QPushButton('Cancel')
        cancel_button.setStyleSheet("text-align: center")
        cancel_button.clicked.connect(lambda: (self.clear_fields(), self.close()))

        add_button = QPushButton('Add')
        add_button.setStyleSheet("text-align: center")
        add_button.clicked.connect(lambda: (self.update_plot(), self.push_command()))

        bottom_button_layout.addWidget(cancel_button)
        bottom_button_layout.addWidget(add_button)

        # End bottom buttons

        main_layout.addWidget(fields_container)
        main_layout.addWidget(bottom_button_container)

    def set_hidden(self):
        if CommandDictionary[self.command_field.currentText()][1] < 1:
            self.arg_field.setDisabled(True)
        else:
            self.arg_field.setEnabled(True)

        if CommandDictionary[self.command_field.currentText()][1] < 2:
            self.step.hide()
        else:
            self.step.show()

    def clear_fields(self):
        self.step.setEnabled(True)
        self.time_field.setText("")
        self.arg_field.setText("")
        self.name_field.setText("")

    def set_step(self):
        self.should_step = not self.should_step

    def push_command(self):
        if self.time_field.text() == "":
            Error("Command must have a time.").call()
            return

        try:
            CommandScheduler.add_command(float(self.time_field.text()), CommandDictionary[self.command_field.currentText()], self.arg_field.text(), self.step.isChecked(), self.name_field.text())
        except Error as err:
            err.call()
            return

        self.update_plot()
        self.clear_fields()
        self.close()
        print("Pushed a command", self.command_field.currentText())
