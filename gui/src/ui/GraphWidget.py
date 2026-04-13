from PySide6.QtWidgets import QWidget, QGridLayout
from PySide6.QtCore import QTimer
import pyqtgraph as pg
import time
import re

from src.command.CommandScheduler import CommandScheduler
from src.command.CommandController import CommandDictionary
from src.command.DeviceStatus import StatusFrame

def extract_number(num: str) -> float:
    match = re.search(r"(-?\d+(?:\.\d+)?)", num.strip())

    if match == None:
        raise ValueError(f"Input '{num}' does not contain a number")

    return float(match[0])

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
            self.data_line2 = self.plot.plot(self.x_data2, self.y_data2, pen=pen, symbol='o', stepMode='right')

class GraphWidget(QWidget):
    # First index of plots is going to be the default graph
    def __init__(self, commanded_plots: dict[str, tuple[str, int, bool]], true_plots: dict[str, tuple[str, int, bool]], command_translation_table: dict[tuple[str, int, bool], tuple[str, int, bool]], realtime_length: int, realtime_interval: int):
        super().__init__()

        self.realtime_length = realtime_length
        self.rt_start_time = time.monotonic()
        self.timer = None

        self.graph_layout = QGridLayout(self)

        self.target_views = {
            plot[1]: CurrentView(pg.PlotWidget(), plot[0], False, plot[1]) for plot in commanded_plots.items()
        }

        self.realtime_views = {
            plot[1]: CurrentView(pg.PlotWidget(), "Realtime " + plot[0], True, plot[1]) for plot in true_plots.items()
        }

        # Translating between keys of the commanded plot to commands for retriving the information to verify whether the parameter is truly following the target
        self.command_translation_table = command_translation_table

        self.true_plots: list[tuple[str, int, bool]] = list(true_plots.values()) 
        print(self.true_plots)

        self.cur_view = list(self.target_views.values())[0]
        self.set_graph(list(self.target_views.values())[0].command_type, False)
        
        self.script_running: bool = False
        self.script_start: float = 0.0

        self.realtime_interval = realtime_interval

        self.pause_time = 0.0
        self.pause_duration = 0.0

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

    def update_rt_data(self):

        status_frame = StatusFrame(self.true_plots)

        for view in self.realtime_views.values():
            num_str = status_frame.status[view.command_type]
            
            view.y_data1.append(extract_number(num_str))
            view.x_data1.append(time.monotonic() - self.rt_start_time)

            view.data_line1.setData(view.x_data1, view.y_data1)

            if len(view.x_data1) > self.realtime_length:
                view.x_data1.pop(0)
                view.y_data1.pop(0)


        if self.script_running:
            status_frame = StatusFrame(list(self.command_translation_table.values()))
            for view in self.target_views.values():
                num = status_frame.status[self.command_translation_table[view.command_type]]
                num = extract_number(num)

                view.x_data2.append((time.monotonic() - self.script_start) - self.pause_duration)
                view.y_data2.append(num)
                view.data_line2.setData(view.x_data2, view.y_data2)

    def start_script(self, start_time: float):
        self.script_running = True
        self.script_start = time.monotonic() + start_time

    def stop_script(self):
        self.script_running = False
        self.pause_duration = 0.0
        self.script_start = 0.0

        for view in self.target_views.values():
            view.x_data2 = []
            view.y_data2 = []
            view.data_line2.setData(view.x_data2, view.y_data2)

    def pause_script(self):
        self.pause_time = time.monotonic()
        self.script_running = False

    def resume_script(self):
        self.script_running = True
        self.pause_duration += time.monotonic() - self.pause_time

    def start_rt(self):
        self.timer = QTimer()
        self.timer.setInterval(self.realtime_interval)
        self.timer.timeout.connect(self.update_rt_data)
        self.timer.start()

    def stop_rt(self):
        if self.timer != None:
            self.timer.stop()

    def set_polling_rate(self, rate: float):
        self.realtime_interval = int((1.0 / rate) * 1000)

        if self.timer != None:
            self.timer.setInterval(self.realtime_interval)

    def set_lookback_time(self, time: float):
        self.realtime_length = int(time / (self.realtime_interval / 1000.0))
