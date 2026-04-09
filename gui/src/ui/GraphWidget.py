from PySide6.QtWidgets import QWidget, QVBoxLayout
import pyqtgraph as pg

from src.command.CommandScheduler import CommandScheduler
from src.command.CommandController import CommandController, Command

class CurrentView:
    def __init__(self, command: tuple[str, int, bool], y_label: str):
        self.command = command
        self.y_label = y_label

class GraphWidget(QWidget):
    def __init__(self):
        super().__init__()

        graph_layout = QVBoxLayout(self)

        self.graph = pg.PlotWidget()

        self.set_graph(Command.PV, "Commanded " + Command.PV[0])

        graph_layout.addWidget(self.graph)

    def set_graph(self, command_type: tuple[str, int, bool], y_label: str):
        times, args = CommandScheduler.get_arg_plot(command_type)
        
        self.graph.clear()
        self.graph.setTitle(y_label + " Over Time")
        self.graph.setLabel('left', y_label)
        self.graph.setLabel('bottom', 'Time (s)')
        self.graph.plot(times, args, symbol='+', stepMode="right")

        self.set_cur_view(command_type, y_label)

    def set_cur_view(self, commmand: tuple[str, int, bool], y_label: str): 
        self.current_view = CurrentView(commmand, y_label)
        print(self.current_view)

    def update_plot(self):
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