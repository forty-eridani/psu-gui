from PySide6.QtWidgets import QApplication

from src.ui.MainWindow import MainWindow

app = QApplication()

window = MainWindow()
window.show()

app.exec()