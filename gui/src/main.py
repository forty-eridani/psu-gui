from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout, QLineEdit, QGridLayout
import pyqtgraph as pg
from PySide6.QtCore import Qt

from CommandScheduler import CommandScheduler
from CommandController import Command, CommandDictionary

HEIGHT = 600
WIDTH = 800

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

register_graph_views = {
        Command.FLT_REQ[0]: Command.FLT_REQ,
        Command.FENA_REQ[0]: Command.FENA_REQ,
        Command.FEVE_REQ[0]: Command.FEVE_REQ,
        Command.STAT_REQ[0]: Command.STAT_REQ,
        Command.SENA_REQ[0]: Command.SENA_REQ,
        Command.SEVE_REQ[0]: Command.SEVE_REQ,
}

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

        line_edit = QLineEdit()
        line_edit.setPlaceholderText("Type your command here")
        line_edit.setMaximumWidth(WIDTH // 2)

        output = QLabel("Hello There")
        output.setMinimumHeight(250)
        output.setStyleSheet("background-color: black; color: white; padding: 5px; font-family: \"Terminal\";")
        output.setAlignment(Qt.AlignmentFlag.AlignTop)

        console_layout.addWidget(output)
        console_layout.addWidget(line_edit)

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

        edit_menu.addAction("Add Command")
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

    def update_graph(self, command_type: tuple[str, int], y_label: str):
        times, args = CommandScheduler.get_arg_plot(command_type)
        
        self.graph.clear()
        self.graph.setTitle(y_label + " Over Time")
        self.graph.setLabel('left', y_label)
        self.graph.setLabel('bottom', 'Time (s)')
        self.graph.plot(times, args, symbol='+', stepMode="right")

CommandScheduler.set_step_rate(3)

CommandScheduler.add_command(1.0, Command.PV, "1.0", False, "PV_1")
CommandScheduler.add_command(2.0, Command.PV, "3.0", False, "PV_1.5")
CommandScheduler.add_command(10.0, Command.PV, "10.0", True, "PV_2")

app = QApplication()
window = MainWindow()
window.show()

app.exec()
