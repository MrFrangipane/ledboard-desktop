import logging

import cv2
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QLabel, QApplication, QMainWindow, QGridLayout, QWidget, QGraphicsView, QGraphicsScene, QPushButton, QProgressBar, QCheckBox
from pyside6helpers.slider import Slider
from pyside6helpers.spinbox import SpinBox
from pyside6helpers.group import make_group

from ledboard.analyzer import Analyzer

_logger = logging.getLogger(__name__)


# def save_settings(self, camera_index):
#     settings = QSettings("Frangitron", "LEDBoard")
#     settings.setValue("camera_index", camera_index)
#
#
# def load_settings(self):
#     settings = QSettings("Frangitron", "LEDBoard")
#     return settings.value("camera_index", None, type=int)


class MainWindow(QMainWindow):
    _viewport_scale = 0.5
    _locator_radius = 3

    def __init__(self):
        super().__init__()

        self._analyzer = Analyzer(ledboard_port="COM13", camera_index=4)

        self.setWindowTitle("LED Board")
        self.setGeometry(100, 100, 1280, 720)

        self.view = QGraphicsView(self)
        self.view.scale(self._viewport_scale, self._viewport_scale)
        self.scene = QGraphicsScene(self)
        self.pixmap_item = self.scene.addPixmap(QPixmap())
        self.view.setScene(self.scene)

        self.spin_led_start = SpinBox(
            name="First LED",
            maximum=5000,
            value=self._analyzer.led_start,
            on_value_changed=self._set_analysis_parameters
        )
        self.spin_led_end =  SpinBox(
            name="Last LED",
            maximum=5000,
            value=self._analyzer.led_end,
            on_value_changed=self._set_analysis_parameters
        )

        self.slider_led_brightness = Slider(
            maximum=255,
            value=self._analyzer.brightness,
            on_value_changed=self._set_analysis_parameters
        )
        self.slider_blur_radius = Slider(
            maximum=self._analyzer.blur_radius * 5,
            value=self._analyzer.blur_radius,
            on_value_changed=self._set_analysis_parameters
        )

        self.spin_on_threshold = SpinBox(
            name="Light on",
            minimum=0, maximum=255,
            value=self._analyzer.comparison_light_on_threshold,
            on_value_changed=self._set_analysis_parameters
        )
        self.spin_off_threshold = SpinBox(
            name="Light off",
            minimum=0, maximum=255,
            value=self._analyzer.comparison_light_off_threshold,
            on_value_changed=self._set_analysis_parameters
        )
        group_thresholds = make_group(title="Analysis threshold", widgets=[
            self.spin_on_threshold, self.spin_off_threshold
        ])

        self.check_test_led_enabled = QCheckBox("Enabled")
        self.slider_test_led_index = Slider(
            maximum=149,
            value=self._analyzer.led_start,
            on_value_changed=self._set_analysis_parameters
        )
        group_test_led = make_group(title="Live test", widgets=[
            self.check_test_led_enabled,
            self.slider_test_led_index,
        ])

        group_parameters = make_group(title="Analysis parameters", widgets=[
            self.spin_led_start,
            self.spin_led_end,
            QLabel("Brightness"), self.slider_led_brightness,
            QLabel("Blur radius"), self.slider_blur_radius,
            group_thresholds,
            group_test_led
        ])

        self.button_scan = QPushButton("Scan...")
        self.button_scan.setFixedWidth(250)
        self.button_scan.clicked.connect(self.button_scan_clicked)

        self.progress = QProgressBar()

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.layout = QGridLayout(self.central_widget)
        self.layout.addWidget(self.view, 0, 0, 4, 1)

        self.layout.addWidget(group_parameters, 0, 1)
        self.layout.addWidget(self.button_scan, 1, 1)

        self.layout.addWidget(self.progress, 2, 1)

        self.layout.addWidget(QWidget(), 3, 1)
        self.layout.setRowStretch(3, 100)
        self.layout.setColumnStretch(0, 100)

        self._viewport_timer = QTimer(self)
        self._viewport_timer.timeout.connect(self._update_viewport)
        self._viewport_timer.start(30)

        self._set_analysis_parameters()

    def scan(self):
        if not self._analyzer.is_working:
            self._analyzer.begin_analysis()

        while self._analyzer.is_working:
            QApplication.processEvents()
            current_step = self._analyzer.analyze_step()
            self.progress.setValue(current_step - self._analyzer.led_start)

        self.progress.setValue(0)
        self.button_scan.setText("Scan...")

    def button_scan_clicked(self):
        if not self._analyzer.is_working:
            self.button_scan.setText("Cancel scan")
            self.progress.setMaximum(self._analyzer.led_end - self._analyzer.led_start)
            self.scan()

        else:
            self._analyzer.end_analysis()
            self.progress.setValue(0)
            self.button_scan.setText("Scan...")

    def closeEvent(self, event):
        self._viewport_timer.stop()
        self._analyzer.end_analysis()
        super().closeEvent(event)

    def _set_analysis_parameters(self):
        self._analyzer.blur_radius = self.slider_blur_radius.value()
        self._analyzer.brightness = self.slider_led_brightness.value()

        self._analyzer.led_start = self.spin_led_start.value()
        self._analyzer.led_end = self.spin_led_end.value()

        self.slider_test_led_index.setMinimum(self.spin_led_start.value())
        self.slider_test_led_index.setMaximum(self.spin_led_end.value())

        if self.check_test_led_enabled.isChecked():
            self._analyzer.illuminate(self.slider_test_led_index.value())

    def _update_viewport(self):
        if self._analyzer.is_working:
            image = self._analyzer.viewport_image
        else:
            image = self._analyzer.capture_blurred_image()

        for loc in self._analyzer.led_coords:
            cv2.circle(image, loc, self._locator_radius, (0, 0, 255), -1)

        self.pixmap_item.setPixmap(self._frame_to_pixmap(image))

    @staticmethod
    def _frame_to_pixmap(frame: cv2.Mat) -> QPixmap:
        height, width, channel = frame.shape
        bytes_per_line = 3 * width
        qt_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
        return QPixmap.fromImage(qt_image)