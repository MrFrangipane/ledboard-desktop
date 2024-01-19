import logging

import cv2
import numpy as np
from PySide6.QtCore import Qt, QTimer

from PySide6.QtGui import QImage, QPixmap, QPainter, QPen
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QGraphicsView, QGraphicsScene

from ledboard.camera import Camera


_logger = logging.getLogger(__name__)


class BrightestPointDetector(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("LED Board")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        self.view = QGraphicsView(self)
        self.scene = QGraphicsScene(self)
        self.view.setScene(self.scene)
        self.layout.addWidget(self.view)

        self.camera = Camera()
        self.camera.open()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

        self.painter = QPainter()
        self.pen = QPen(Qt.red)
        self.drawing = False

    def update_frame(self):
        ret, frame = self.camera.read()
        if not ret:
            return

        # Convert the frame to grayscale for better detection
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(gray_frame)

        frame_with_circle = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        cv2.circle(frame_with_circle, max_loc, 10, (0, 0, 255), -1)

        self.display_frame(frame_with_circle)

    def display_frame(self, frame):
        height, width, channel = frame.shape
        bytes_per_line = 3 * width
        qt_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)
        self.scene.clear()
        self.scene.addPixmap(pixmap)
        self.view.setScene(self.scene)
        self.view.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = True
            self.last_point = event.pos()

    def mouseMoveEvent(self, event):
        if self.drawing:
            current_point = event.pos()
            self.painter.begin(self.scene)
            self.painter.setPen(self.pen)
            self.painter.drawLine(self.last_point, current_point)
            self.painter.end()
            self.last_point = current_point

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = False

    def closeEvent(self, event):
        self.camera.release()
        super().closeEvent(event)


def main():
    app = QApplication([])

    window = BrightestPointDetector()
    window.show()
    app.exec()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
