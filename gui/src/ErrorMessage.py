from PySide6.QtWidgets import QMessageBox

class Error(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)
        self.dialog = QMessageBox()
        self.dialog.setWindowTitle("Error!")
        self.dialog.setText(msg)

    def call(self) -> None:
        self.dialog.show()
        self.dialog.exec()

