import logging

import cv2
import numpy
import numpy as np
from PySide6.QtCore import Qt, QTimer, QThread
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QLabel, QApplication, QMainWindow, QGridLayout, QWidget, QGraphicsView, QGraphicsScene, QPushButton, QSlider, QProgressBar

from ledboard.board import LedBoard
from ledboard.camera2 import Camera


_logger = logging.getLogger(__name__)


class BrightestPointDetector(QMainWindow):
    _blur_radius = 1
    _viewport_scale = 1
    _led_start = 1
    _led_end = 149
    _locator_radius = 1

    def __init__(self):
        super().__init__()

        self.led_board = LedBoard()

        self.setWindowTitle("LED Board")
        self.setGeometry(100, 100, 1280, 720)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.layout = QGridLayout(self.central_widget)

        self.view = QGraphicsView(self)
        self.view.scale(self._viewport_scale, self._viewport_scale)
        self.scene = QGraphicsScene(self)
        self.pixmap_item = self.scene.addPixmap(QPixmap())
        self.view.setScene(self.scene)

        self.button_scan = QPushButton("Scan...")
        self.button_scan.setFixedWidth(250)
        self.button_scan.clicked.connect(self.button_scan_clicked)

        self.slider_led_brightness = QSlider()
        self.slider_led_brightness.setMaximum(255)
        self.slider_led_brightness.setValue(20)
        self.slider_led_brightness.setOrientation(Qt.Horizontal)
        self.slider_led_brightness.valueChanged.connect(self.slider_led_brightness_changed)

        self.slider_led_index = QSlider()
        self.slider_led_index.setMaximum(150)
        self.slider_led_index.setValue(75)
        self.slider_led_index.setOrientation(Qt.Horizontal)
        self.slider_led_index.valueChanged.connect(self.slider_led_index_changed)

        self.slider_blur_radius = QSlider()
        self.slider_blur_radius.setMaximum(10)
        self.slider_blur_radius.setValue(0)
        self.slider_blur_radius.setOrientation(Qt.Horizontal)
        self.slider_blur_radius.valueChanged.connect(self.slider_blur_radius_changed)

        self.progress = QProgressBar()

        self.layout.addWidget(self.view, 0, 0, 9, 1)
        self.layout.addWidget(QLabel("Led brightness"), 0, 1)
        self.layout.addWidget(self.slider_led_brightness, 1, 1)
        self.layout.addWidget(QLabel("Led index"), 2, 1)
        self.layout.addWidget(self.slider_led_index, 3, 1)
        self.layout.addWidget(QLabel("Blur radius"), 4, 1)
        self.layout.addWidget(self.slider_blur_radius, 5, 1)
        self.layout.addWidget(self.button_scan, 6, 1)
        self.layout.addWidget(self.progress, 7, 1)
        self.layout.addWidget(QLabel(), 8, 1)
        self.layout.setRowStretch(8, 100)
        self.layout.setColumnStretch(0, 100)

        self.camera = Camera()
        self.camera.open()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_viewport)
        self.timer.start(30)

        self._is_working = False

        self._led_coords = list()

    @staticmethod
    def frame_to_pixmap(frame: cv2.Mat) -> QPixmap:
        height, width, channel = frame.shape
        bytes_per_line = 3 * width
        qt_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_BGR888)
        return QPixmap.fromImage(qt_image)

    def update_viewport(self):
        if not self._is_working:
            frame = cv2.cvtColor(self.camera.read(), cv2.COLOR_BGR2RGB)
            frame = cv2.GaussianBlur(frame, (self._blur_radius, self._blur_radius), 0)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(gray)
            cv2.circle(frame, max_loc, self._locator_radius * 2, (255, 0, 255), -1)

            for loc, color in self._led_coords:
                cv2.circle(frame, loc, self._locator_radius, color, -1)
            self.pixmap_item.setPixmap(self.frame_to_pixmap(frame))

    def slider_led_brightness_changed(self):
        self.led_board.connect()
        self.led_board.illuminate(
            led_index=self.slider_led_index.value(),
            brightness=self.slider_led_brightness.value()
        )
        self.led_board.disconnect()

    def slider_led_index_changed(self):
        self.led_board.connect()
        self.led_board.illuminate(
            led_index=self.slider_led_index.value(),
            brightness=self.slider_led_brightness.value()
        )
        self.led_board.disconnect()

    def slider_blur_radius_changed(self):
        self._blur_radius = self.slider_blur_radius.value() * 2 + 1

    def button_scan_clicked(self):
        if self._is_working:
            self.progress.setValue(0)
            self.button_scan.setText("Scan...")
            self._is_working = False

        else:
            self.button_scan.setText("Cancel scan")
            self.scanalyze()

    def scanalyze(self):
        self._is_working = True
        self.led_board.connect()
        brightness = self.slider_led_brightness.value()
        self.progress.setMaximum(self._led_end - self._led_start)
        self._led_coords = list()

        self.led_board.illuminate(-1, 0)
        QThread.currentThread().msleep(100)
        background = self.camera.read()
        background = cv2.GaussianBlur(background, (self._blur_radius, self._blur_radius), 0)

        for led in range(self._led_start, self._led_end):
            self.progress.setValue(led - self._led_start)

            difference = None
            loc = None
            capture_count = None

            for capture_count in range(10):
                self.led_board.illuminate(led, brightness)
                image_led = self.camera.read()
                image_led = cv2.GaussianBlur(image_led, (self._blur_radius, self._blur_radius), 0)
                difference = cv2.absdiff(background, image_led)
                gray = cv2.cvtColor(difference, cv2.COLOR_BGR2GRAY)
                _, max_val, _, loc = cv2.minMaxLoc(gray)
                if max_val > 128:
                    break

            if self._led_coords:
                prev = numpy.array(self._led_coords[-1][0])
                curr = numpy.array(loc)
                distance = np.linalg.norm(curr - prev)
                if distance < 5.0:
                    color = (0, 0, 255)
                else:
                    color = (0, 255, 0)
            else:
                color = 255, 255, 255
                distance = 0

            print(led, capture_count, distance)
            self._led_coords.append([loc, color])

            for loc, color in self._led_coords:
                cv2.circle(difference, loc, self._locator_radius, color, -1)
            self.pixmap_item.setPixmap(self.frame_to_pixmap(difference))

            QApplication.processEvents()

        self.led_board.illuminate(-1, 0)
        self.led_board.disconnect()
        self._is_working = False
        self.progress.setValue(0)
        self.button_scan.setText("Scan...")
        self._is_working = False

    def closeEvent(self, event):
        self._is_working = False
        self.timer.stop()
        super().closeEvent(event)

    def _wait_interval(self):
        for _ in range(int(self._interval / 10)):
            QThread.currentThread().msleep(10)
            QApplication.processEvents()


def main():
    app = QApplication([])

    window = BrightestPointDetector()
    window.show()
    app.exec()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
