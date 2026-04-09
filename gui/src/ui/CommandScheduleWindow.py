from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QScrollArea, QComboBox, QListWidget

from src.command.CommandScheduler import CommandScheduler
from src.command.CommandController import CommandDictionary

HEIGHT = 600
WIDTH = 400

class CommandScheduleWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setFixedSize(WIDTH, HEIGHT)

        container = QWidget()
        self.setCentralWidget(container)
        layout = QVBoxLayout(container)

        # Selector portion

        self.selector = QComboBox()
        self.selector.setStyleSheet("combobox-popup: 0;") 
        self.selector.activated.connect(self.set_list)
        
        for name in CommandDictionary.keys():
            self.selector.addItem(name)

        # End of selector portion

        # Start of actual list 

        scroll_area = QScrollArea()
        scroll_container = QWidget(scroll_area)
        scroll_layout = QVBoxLayout(scroll_container)

        self.scroll_list = QListWidget()
        self.scroll_list.setMinimumHeight(500)
        self.scroll_list.setMinimumWidth(WIDTH - 50)

        scroll_layout.addWidget(self.scroll_list)
        scroll_area.setWidget(scroll_container)

        # End of list

        layout.addWidget(self.selector)
        layout.addWidget(scroll_area)

    def set_list(self):
        self.scroll_list.clear()
        command = CommandDictionary[self.selector.currentText()]
        for cmd in CommandScheduler.get_command_times(command):
            self.scroll_list.addItem(cmd)