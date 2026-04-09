from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QFileDialog, QMessageBox

from src.command.CommandScheduler import CommandScheduler
from src.command.CommandController import CommandController, CommandDictionary
from src.ui.AddCommandWindow import AddCommandWindow
from src.ui.RemoveCommandWindow import RemoveCommandWindow
from src.ui.GraphWidget import GraphWidget
from src.ui.ConsoleWidget import ConsoleWidget
from src.ui.CommandScheduleWindow import CommandScheduleWindow

HEIGHT = 600
WIDTH = 800

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.script_path = "" 

        # The targets for all the values in code
        self.target_graph_views = {
            command_str: command_value for command_str, command_value in CommandDictionary.items() if command_value[1] > 1 
        }

        self.setWindowTitle("PSU GUI")
        self.setFixedSize(WIDTH, HEIGHT)

        container = QWidget()
        self.setCentralWidget(container)

        layout = QVBoxLayout(container)

        self.graph = GraphWidget()

        self.console = ConsoleWidget()

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

        for name, command in self.target_graph_views.items():
            action = commanded_submenu.addAction("Graph commanded " + name)

            # Sometimes I really hate pythonsrc..
            action.triggered.connect(lambda *_, cmd=command: (self.graph.set_graph(cmd, "Commanded " + cmd[0])))

        # End of menu section

        layout.addWidget(self.graph)
        layout.addWidget(self.console)

        self.add_window = None
        self.remove_window = None

    def show_add_window(self):
        if self.add_window == None:
            self.add_window = AddCommandWindow(self.graph.update_plot)
        self.add_window.show()

    def show_remove_window(self):
        if self.remove_window == None:
            self.remove_window = RemoveCommandWindow(self.graph.update_plot)
        self.remove_window.show()

    def new_script(self):
        msg_box = QMessageBox.question(self, "Quit Current script", "Are you sure you want to quit your current script?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if msg_box == QMessageBox.StandardButton.No:
            return

        CommandScheduler.clear()
        self.graph.update_plot()

    def load_script(self):
        msg_box = QMessageBox.question(self, "Quit Current script", "Are you sure you want to quit your current script?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if msg_box == QMessageBox.StandardButton.No:
            return

        self.script_path = QFileDialog.getOpenFileName(self)[0]
        
        if self.script_path != "":
            CommandScheduler.load_file(self.script_path)

        self.graph.update_plot()

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
            self.command_schedule_window = CommandScheduleWindow()

        self.command_schedule_window.show()