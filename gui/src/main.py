from ErrorMessage import Error
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout, QLineEdit, QGridLayout, QScrollArea, QHBoxLayout, QPushButton, QComboBox, QCheckBox, QFileDialog, QMessageBox, QListWidget
from PySide6.QtGui import QDoubleValidator
import pyqtgraph as pg
from PySide6.QtCore import Qt

from CommandScheduler import CommandScheduler
from CommandController import Command, CommandController, CommandDictionary

HEIGHT = 600
WIDTH = 800

ADD_COMMAND_WIDTH = 400 
ADD_COMMAND_HEIGHT = 225 

REMOVE_COMMAND_WIDTH = 400 
REMOVE_COMMAND_HEIGHT = 130 

COMMAND_SCHEDULE_WIDTH = 400
COMMAND_SCHEDULE_HEIGHT = 600 

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

class CurrentView:
    def __init__(self, command: tuple[str, int], y_label: str):
        self.command = command
        self.y_label = y_label

update_plot = lambda: None

class AddCommand(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Add Command")
        self.setFixedSize(ADD_COMMAND_WIDTH, ADD_COMMAND_HEIGHT)

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
        add_button.clicked.connect(lambda: (update_plot(), self.push_command()))

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

        update_plot()
        self.clear_fields()
        self.close()
        print("Pushed a command", self.command_field.currentText())

class RemoveCommand(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setFixedSize(REMOVE_COMMAND_WIDTH, REMOVE_COMMAND_HEIGHT)
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

        update_plot()
        self.clear_field()
        self.close()

class ViewCommandSchedule(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setFixedSize(COMMAND_SCHEDULE_WIDTH, COMMAND_SCHEDULE_HEIGHT)

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
        self.scroll_list.setMinimumWidth(COMMAND_SCHEDULE_WIDTH - 50)

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

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.script_path = "" 

        self.setWindowTitle("PSU GUI")
        self.setFixedSize(WIDTH, HEIGHT)

        container = QWidget()
        self.setCentralWidget(container)

        layout = QVBoxLayout(container)

        # Beginning of graph section

        graph_container = QWidget(container)
        graph_layout = QVBoxLayout(graph_container)

        self.graph = pg.PlotWidget()

        self.set_graph(Command.PV, "Commanded " + Command.PV[0])

        graph_layout.addWidget(self.graph)

        # End of graph section

        # Console section TODO: Once GUI complete, add date/time at top of console

        console_container = QWidget(container)
        console_layout = QVBoxLayout(console_container)

        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText("Type your command here")

        self.line_edit.returnPressed.connect(self.push_cmd)

        self.output = QLabel("Hello There\n")
        self.output.setMinimumHeight(250)
        self.output.setStyleSheet("background-color: black; color: white; padding: 5px; font-family: \"Terminal\"; font-weight: bold;")
        self.output.setMinimumWidth(WIDTH)
        self.output.setAlignment(Qt.AlignmentFlag.AlignTop)

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

        file_menu.addAction("New Script").triggered.connect(self.new_script)
        file_menu.addAction("Open Script").triggered.connect(self.load_script)
        file_menu.addAction("Save Script as").triggered.connect(self.save_script_as)
        file_menu.addAction("Save Script").triggered.connect(self.save_script)
        file_menu.addSeparator()
        file_menu.addAction("Run Script")

        edit_menu.addAction("Add Command").triggered.connect(self.show_add_window)
        edit_menu.addAction("Remove Command").triggered.connect(self.show_remove_window)

        commanded_submenu = view_menu.addMenu("Script Setpoints")
        command_schedule = view_menu.addAction("Script Command Schedule")
        command_schedule.triggered.connect(self.show_command_schedule)
        self.command_schedule_window = None

        for name, command in target_graph_views.items():
            action = commanded_submenu.addAction("Graph commanded " + name)

            # Sometimes I really hate python...
            action.triggered.connect(lambda *_, cmd=command: (self.set_graph(cmd, "Commanded " + cmd[0])))

        # End of menu section

        layout.addWidget(graph_container)
        layout.addWidget(console_container)

        self.add_window = None
        self.remove_window = None

    def show_add_window(self):
        if self.add_window == None:
            self.add_window = AddCommand()
        self.add_window.show()

    def show_remove_window(self):
        if self.remove_window == None:
            self.remove_window = RemoveCommand()
        self.remove_window.show()


    def set_cur_view(self, commmand: tuple[str, int], y_label: str): 
        self.current_view = CurrentView(commmand, y_label)
        print(self.current_view)

    def set_graph(self, command_type: tuple[str, int], y_label: str):
        times, args = CommandScheduler.get_arg_plot(command_type)
        
        self.graph.clear()
        self.graph.setTitle(y_label + " Over Time")
        self.graph.setLabel('left', y_label)
        self.graph.setLabel('bottom', 'Time (s)')
        self.graph.plot(times, args, symbol='+', stepMode="right")

        self.set_cur_view(command_type, y_label)

    def update_graph(self):
        if (self.current_view != None):
            times, args = CommandScheduler.get_arg_plot(self.current_view.command)
            y_label = self.current_view.y_label

            self.graph.clear()
            self.graph.setTitle(y_label + " Over Time")
            self.graph.setLabel('left', y_label)
            self.graph.setLabel('bottom', 'Time (s)')
            self.graph.plot(times, args, symbol='+', stepMode="right")

            print("Updated cur graph")
        else:
            print("No current graph", self.current_view)

    def push_cmd(self) -> None:
        full_command = self.line_edit.text() + "\r"
        self.output.setText(self.output.text() + "[USER] " + full_command[:-1] + '\n')

        response = CommandController.run_raw_command(full_command)

        self.output.setText(self.output.text() + "[DEVICE] " + response)

    def new_script(self):
        msg_box = QMessageBox.question(self, "Quit Current script", "Are you sure you want to quit your current script?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if msg_box == QMessageBox.StandardButton.No:
            return

        CommandScheduler.clear()
        self.update_graph()

    def load_script(self):
        msg_box = QMessageBox.question(self, "Quit Current script", "Are you sure you want to quit your current script?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if msg_box == QMessageBox.StandardButton.No:
            return

        self.script_path = QFileDialog.getOpenFileName(self)[0]
        
        if self.script_path != "":
            CommandScheduler.load_file(self.script_path)

        self.update_graph()

    def save_script(self):
        if self.script_path == "":
            self.script_path = QFileDialog.getSaveFileName(self)[0]

        # Means the user closed out of the file dialog
        if self.script_path != "":
            CommandScheduler.save_file(self.script_path)

    def save_script_as(self):
        self.script_path = QFileDialog.getSaveFileName(self)[0]

        if self.script_path != "":
            CommandScheduler.save_file(self.script_path)

    def show_command_schedule(self):
        if self.command_schedule_window== None:
            self.command_schedule_window = ViewCommandSchedule()

        self.command_schedule_window.show()

app = QApplication()

window = MainWindow()
update_plot = window.update_graph
window.show()

app.exec()
