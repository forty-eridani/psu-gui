from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout, QLineEdit, QGridLayout, QScrollArea, QHBoxLayout, QPushButton, QComboBox, QCheckBox
from PySide6.QtGui import QDoubleValidator
import pyqtgraph as pg
from PySide6.QtCore import Qt

from CommandScheduler import CommandScheduler
from CommandController import Command, CommandController, CommandDictionary

HEIGHT = 600
WIDTH = 800

EDIT_WIDTH = 400 
EDIT_HEIGHT = 225 

# The targets for all the values in code
target_graph_views = {
    command_str: command_value for command_str, command_value in CommandDictionary.items() if command_value[1] > 1 
}

true_graph_views = {
        Command.PV_REQ[0]: Command.PV_REQ,
        Command.MV_REQ[0]: Command.MV_REQ,
        Command.PC_REQ[0]: Command.PC_REQ,
        Command.MC_REQ[0]: Command.MC_REQ,
        Command.FBD_REQ[0]: Command.FBD_REQ,
        Command.OVP_REQ[0]: Command.OVP_REQ,
        Command.UVL_REQ[0]: Command.UVL_REQ,
}

class AddCommand(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Add Command")
        self.setFixedSize(EDIT_WIDTH, EDIT_HEIGHT)

        container = QWidget()
        self.setCentralWidget(container)
        
        main_layout = QVBoxLayout(container)

        # Fields

        fields_container = QWidget(container)
        fields_layout = QVBoxLayout(fields_container)

        name_field = QLineEdit()
        name_field.setPlaceholderText("Command Name")

        self.command_field = QComboBox()
        self.command_field.addItems(CommandDictionary.keys()) 
        self.command_field.setStyleSheet("combobox-popup: 0;") # A solution to entire dropdown appearing
                                                               # I found off of a 15 year old QT forum thread

        self.command_field.currentIndexChanged.connect(self.set_hidden)

        time_field = QLineEdit()
        time_field.setValidator(QDoubleValidator())
        time_field.setPlaceholderText("Time (s)")

        arg_container = QWidget(fields_container)
        arg_layout = QHBoxLayout(arg_container)
        
        self.arg_field = QLineEdit()
        self.arg_field.setPlaceholderText("Argument for command")
        self.arg_field.setDisabled(True)

        self.step = QCheckBox("Step")

        arg_layout.addWidget(self.arg_field)
        arg_layout.addWidget(self.step)

        fields_layout.addWidget(name_field)
        fields_layout.addWidget(self.command_field)
        fields_layout.addWidget(time_field)
        fields_layout.addWidget(arg_container)

        self.set_hidden()

        # End fields

        # Bottom 'Cancel' and 'Add' buttons

        bottom_button_container = QWidget(container)
        bottom_button_layout = QHBoxLayout(bottom_button_container)

        cancel_button = QPushButton('Cancel')
        cancel_button.setStyleSheet("text-align: center")
        cancel_button.clicked.connect(self.close)

        add_button = QPushButton('Add')
        add_button.setStyleSheet("text-align: center")
        add_button.clicked.connect(self.close)

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


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PSU GUI")
        self.setFixedSize(WIDTH, HEIGHT)

        container = QWidget()
        self.setCentralWidget(container)

        layout = QGridLayout(container)

        # Beginning of graph section

        graph_container = QWidget(container)
        graph_layout = QVBoxLayout(graph_container)

        self.graph = pg.PlotWidget()

        self.update_graph(Command.PV, "Commanded " + Command.PV[0])

        graph_layout.addWidget(self.graph)

        # End of graph section

        label2 = QLabel("Test")
        label2.setMinimumWidth(WIDTH // 2)
        label2.setAlignment(Qt.AlignCenter) # type: ignore

        # Console section TODO: Once GUI complete, add date/time at top of console

        console_container = QWidget(container)
        console_layout = QVBoxLayout(console_container)

        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText("Type your command here")
        self.line_edit.setMaximumWidth(WIDTH // 2)

        self.line_edit.returnPressed.connect(self.push_cmd)

        self.output = QLabel("Hello There\n")
        self.output.setMinimumHeight(250)
        self.output.setStyleSheet("background-color: black; color: white; padding: 5px; font-family: \"Terminal\";")
        self.output.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.output.setMinimumWidth(600)

        scroll_area = QScrollArea()
        scroll_area.setWidget(self.output)

        console_layout.addWidget(scroll_area)
        console_layout.addWidget(self.line_edit)

        # End of console section

        # Menu section

        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("File")
        edit_menu = menu_bar.addMenu("Edit")
        view_menu = menu_bar.addMenu("View")

        file_menu.addAction("New Script")
        file_menu.addAction("Open Script")
        file_menu.addAction("Save Script as")
        file_menu.addAction("Save Script")

        edit_menu.addAction("Add Command").triggered.connect(self.show_add_window)
        edit_menu.addAction("Remove Command")

        view_menu.addMenu("View")
        for name, command in target_graph_views.items():
            action = view_menu.addAction("Graph commanded " + name)

            # Sometimes I really hate python...
            action.triggered.connect(lambda *_, cmd=command: self.update_graph(cmd, "Commanded " + cmd[0]))

        # End of menu section

        label3 = QLabel("Test")
        label3.setMinimumWidth(WIDTH // 2)
        label3.setAlignment(Qt.AlignCenter) # type: ignore

        layout.addWidget(graph_container, 0, 0)
        layout.addWidget(label2, 0, 1)
        layout.addWidget(console_container, 1, 0)
        layout.addWidget(label3, 1, 1)


        self.font_metrics = self.output.fontMetrics()

        self.w = None

    def show_add_window(self):
        if self.w == None:
            self.w = AddCommand()
            self.w.show()

    def update_graph(self, command_type: tuple[str, int], y_label: str):
        times, args = CommandScheduler.get_arg_plot(command_type)
        
        self.graph.clear()
        self.graph.setTitle(y_label + " Over Time")
        self.graph.setLabel('left', y_label)
        self.graph.setLabel('bottom', 'Time (s)')
        self.graph.plot(times, args, symbol='+', stepMode="right")

    def push_cmd(self) -> None:
        full_command = self.line_edit.text() + "\r"
        self.output.setText(self.output.text() + "[USER] " + full_command[:-1] + '\n')

        response = CommandController.run_raw_command(full_command)

        self.output.setText(self.output.text() + "[DEVICE] " + response)

CommandScheduler.set_step_rate(3)

CommandScheduler.add_command(1.0, Command.PV, "1.0", False, "PV_1")
CommandScheduler.add_command(2.0, Command.PV, "3.0", False, "PV_1.5")
CommandScheduler.add_command(10.0, Command.PV, "10.0", True, "PV_2")

# CommandScheduler.run_commands(0.0)

app = QApplication()

window = MainWindow()
window.show()

app.exec()
