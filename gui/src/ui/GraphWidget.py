from PySide6.QtWidgets import QWidget, QGridLayout 
import pyqtgraph as pg

from src.command.CommandScheduler import CommandScheduler

class CurrentView:
    def __init__(self, plot: pg.PlotWidget, y_label: str, realtime: bool, command_type: tuple[str, int, bool]):
        self.plot = plot
        self.y_label = y_label
        self.x_data1 = [] 
        self.y_data1 = [] 
        self.realtime = realtime
        self.command_type = command_type

        self.data_line1 = self.plot.plot(self.x_data1, self.y_data1, symbol='o', stepMode='right')

        self.plot.setLabel("left", y_label)
        self.plot.setLabel("bottom", "Time (s)")
        self.plot.setTitle(y_label + " Over Time (s)")

        if not realtime:
            self.x_data2 = []
            self.y_data2 = []

            pen = pg.mkPen(color=(255, 0, 0))
            self.data_line2 = self.plot.plot(self.x_data2, self.y_data2, pen=pen)

class GraphWidget(QWidget):
    # First index of plots is going to be the default graph
    def __init__(self, plots: list[tuple[str, int, bool]], realtime_length: int):
        super().__init__()

        self.realtime_length = realtime_length

        self.graph_layout = QGridLayout(self)

        self.target_views = {
            plot: CurrentView(pg.PlotWidget(), plot[0], False, plot) for plot in plots
        }

        self.realtime_views = {
            plot: CurrentView(pg.PlotWidget(), "Realtime " + plot[0], True, plot) for plot in plots
        }

        self.cur_view = list(self.target_views.values())[0]
        self.set_graph(list(self.target_views.values())[0].command_type, False)
        
        self.script_running: bool = False
        self.script_start: float = 0.0

    def set_graph(self, command_type: tuple[str, int, bool], realtime: bool):
        self.update_plot()
        self.graph_layout.removeWidget(self.cur_view.plot)
        self.cur_view.plot.hide()

        if realtime:
            self.cur_view = self.realtime_views[command_type]
        else:
            self.cur_view = self.target_views[command_type]

        self.graph_layout.addWidget(self.cur_view.plot, 0, 0)
        self.cur_view.plot.show()

    def update_plot(self):
        for view in self.target_views.values():
            target_xs,  target_ys = CommandScheduler.get_arg_plot(view.command_type)
            view.data_line1.setData(target_xs, target_ys)
            print("Set data called at", view.y_label)

        for views in self.realtime_views.values():
            pass
