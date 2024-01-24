import logging

from PySide6.QtWidgets import QApplication

from main_window import MainWindow


logging.basicConfig(level=logging.INFO)

app = QApplication([])

window = MainWindow()
window.show()
app.exec()
