from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QFileDialog, QMessageBox, QHBoxLayout, QLabel

from src.command.CommandScheduler import CommandScheduler
from src.command.CommandController import CommandController, CommandDictionary, Command
from src.ui.AddCommandWindow import AddCommandWindow
from src.ui.RemoveCommandWindow import RemoveCommandWindow
from src.ui.GraphWidget import GraphWidget
from src.ui.ConsoleWidget import ConsoleWidget
from src.ui.CommandScheduleWindow import CommandScheduleWindow
from src.ui.ConnectPromptWindow import ConnectPromptWindow

HEIGHT = 800
WIDTH = 800

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.script_path = "" 

        # The targets for all the values in code
        self.target_graph_views = {
                "Target Voltage (v)": Command.PV,
                "Target Current (a)": Command.PC,
                "Target Fold Back Delay (ns)": Command.FBD,
                "Target Overvoltage Limit (v)": Command.OVP,
                "Target Undervoltage Limit (v)": Command.UVL
        }

        self.target_real_table = {
            Command.PV: Command.MV_REQ,
            Command.PC: Command.MC_REQ,
            Command.FBD: Command.FBD_REQ,
            Command.OVP: Command.OVP_REQ,
            Command.UVL: Command.UVL_REQ
        }

        self.telemetry_views = {
            "Requested Voltage (v)": Command.PV_REQ,
            "True Voltage (v)": Command.MV_REQ,
            "Target Current (a)": Command.PC_REQ,
            "True Current (a)": Command.MC_REQ,
            "Foldback Delay (ns)": Command.FBD_REQ,
            "Overvoltage Limit (v)": Command.OVP_REQ,
            "Undervoltage Limit (v)": Command.UVL_REQ,
        }

        self.setWindowTitle("PSU GUI")
        self.setFixedSize(WIDTH, HEIGHT)

        container = QWidget()
        self.setCentralWidget(container)

        layout = QVBoxLayout(container)

        self.graph = GraphWidget(self.target_graph_views, self.telemetry_views, self.target_real_table, 32, 1000)

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
        file_menu.addAction("Connect").triggered.connect(self.show_connect_prompt)
        file_menu.addAction("Disconnect").triggered.connect(self.disconnect_from_device)

        edit_menu.addAction("Add Command").triggered.connect(self.show_add_window)
        edit_menu.addAction("Remove Command").triggered.connect(self.show_remove_window)

        commanded_submenu = view_menu.addMenu("Script Setpoints")
        realtime_submenu = view_menu.addMenu("Real Time Device Telemetry")
        command_schedule = view_menu.addAction("Script Command Schedule")
        command_schedule.triggered.connect(self.show_command_schedule)
        self.command_schedule_window = None

        for name, command in self.target_graph_views.items():
            action = commanded_submenu.addAction("Graph commanded " + name)

            # Sometimes I really hate pythonsrc..
            action.triggered.connect(lambda *_, cmd=command: (self.graph.set_graph(cmd, False)))

        for name, command in self.telemetry_views.items():
            action = realtime_submenu.addAction("Real Time " + name)

            # Sometimes I really hate pythonsrc..
            action.triggered.connect(lambda *_, cmd=command: (self.graph.set_graph(cmd, True)))

        # End of menu section

        # Top bar section

        top_bar_container = QWidget()
        top_bar = QHBoxLayout(top_bar_container)

        self.connected_label = QLabel("Disconnected •")
        self.connected_label.setStyleSheet("color: red;")

        top_bar.addWidget(self.connected_label)

        # End of top bar section

        layout.addWidget(top_bar_container)
        layout.addWidget(self.graph)
        layout.addWidget(self.console)

        self.add_window = None
        self.remove_window = None
        self.connection_prompt = None

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

    def show_connect_prompt(self):
        if self.connection_prompt == None:
            self.connection_prompt = ConnectPromptWindow(self.on_connection)
        
        self.connection_prompt.show()

    def on_connection(self):
        self.connected_label.setText("Connected •")
        self.connected_label.setStyleSheet("color: green;")

    def disconnect_from_device(self):
        CommandController.disconnect()
        self.connected_label.setText("Disconnected •")
        self.connected_label.setStyleSheet("color: red;")
