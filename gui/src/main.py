from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout, QLineEdit, QGridLayout
from PySide6.QtCharts import QChart, QChartView, QLineSeries
from PySide6.QtCore import Qt

from CommandScheduler import CommandScheduler
from CommandController import Command

HEIGHT = 600
WIDTH = 800

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PSU GUI")
        self.setFixedSize(WIDTH, HEIGHT)

        container = QWidget()
        self.setCentralWidget(container)

        layout = QGridLayout(container)

        label1 = QLabel("Test")
        label1.setMinimumWidth(WIDTH // 2)
        label1.setAlignment(Qt.AlignCenter) # type: ignore

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

        label3 = QLabel("Test")
        label3.setMinimumWidth(WIDTH // 2)
        label3.setAlignment(Qt.AlignCenter) # type: ignore

        layout.addWidget(label1, 0, 0)
        layout.addWidget(label2, 0, 1)
        layout.addWidget(console_container, 1, 0)
        layout.addWidget(label3, 1, 1)

app = QApplication()
window = MainWindow()
window.show()

# CommandScheduler.add_command(5.0, Command.PV, "10.0", False, "PV_1")
# CommandScheduler.add_command(10.0, Command.PV, "5.0", True, "PV_2")
# CommandScheduler.add_command(7.0, Command.PV, "3.0", True, "PV_1.5")

# CommandScheduler.save_file("psu_save.csv")

CommandScheduler.load_file("psu_save.csv")
CommandScheduler.save_file("psu_save2.csv")


app.exec()