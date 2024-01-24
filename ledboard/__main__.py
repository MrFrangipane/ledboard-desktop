import logging

from PySide6.QtWidgets import QApplication
from pyside6helpers import css

from main_window import MainWindow


logging.basicConfig(level=logging.INFO)

app = QApplication([])
css.load_onto(app)

window = MainWindow()
window.show()
app.exec()
