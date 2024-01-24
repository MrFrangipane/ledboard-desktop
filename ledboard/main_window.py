import logging

import cv2
from PySide6.QtCore import QTimer, QRectF, QSettings, Qt
from PySide6.QtGui import QImage, QPixmap, QBrush, QColor, QPen
from PySide6.QtWidgets import (QLabel, QApplication, QMainWindow, QGridLayout, QWidget,
                               QGraphicsScene, QPushButton, QProgressBar, QCheckBox,
                               QGraphicsRectItem, QComboBox, QRadioButton)
from pyside6helpers.slider import Slider
from pyside6helpers.spinbox import SpinBox
from pyside6helpers.group import make_group
from pyside6helpers.error_reporting import error_reported

from ledboard.analyzer import Analyzer
from ledboard.camera import Camera
from ledboard.board import LedBoard
from ledboard.graphics_view import GraphicsView

_logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    _locator_radius = 3

    def __init__(self):
        super().__init__()
        self._is_initialized = False
        #
        # FIXME create configuration classes
        self._combo_cameras = QComboBox()
        self._combo_cameras.addItems(Camera.get_camera_names())

        self._combo_serial_ports = QComboBox()
        self._combo_serial_ports.addItems(LedBoard.get_serial_port_names())

        self._combo_cameras.currentIndexChanged.connect(self._combo_cameras_changed)
        self._combo_serial_ports.currentIndexChanged.connect(self._combo_serial_port_changed)

        self._radio_pixel_type_rgb = QRadioButton("RGB")
        self._radio_pixel_type_rgb.toggled.connect(self._radio_pixel_type_rgb_toggled)
        self._radio_pixel_type_rgbw = QRadioButton("RGBW")
        group_pixel_type = make_group(title="Pixel Type", widgets=[
            self._radio_pixel_type_rgb,
            self._radio_pixel_type_rgbw
        ])

        group_devices = make_group(title="Devices", widgets=[
            self._combo_cameras,
            self._combo_serial_ports,
            group_pixel_type
        ])

        self._analyzer = Analyzer()
        self.load_settings()
        #
        # self._combo_cameras_changed(self._combo_cameras.currentIndex())
        # self._combo_serial_port_changed(self._combo_serial_ports.currentIndex())

        self.setWindowTitle("LED Board")
        self.setGeometry(100, 100, 1280, 720)

        self.scene = QGraphicsScene(self)
        self.view = GraphicsView(self)
        self.view.setScene(self.scene)

        self._item_image = self.scene.addPixmap(QPixmap())
        self._items_locators = dict()

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

        self.progress = QProgressBar()

        self.button_scan = QPushButton("Scan...")
        self.button_scan.setFixedWidth(250)
        self.button_scan.clicked.connect(self.button_scan_clicked)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.layout = QGridLayout(self.central_widget)
        self.layout.addWidget(make_group("Video", [self.view]), 0, 0, 5, 1)

        self.layout.addWidget(group_devices, 0, 1)
        self.layout.addWidget(group_parameters, 1, 1)
        self.layout.addWidget(self.progress, 2, 1)
        self.layout.addWidget(self.button_scan, 3, 1)

        self.layout.addWidget(QWidget(), 4, 1)
        self.layout.setRowStretch(4, 100)
        self.layout.setColumnStretch(0, 100)

        self._viewport_timer = QTimer(self)
        self._viewport_timer.timeout.connect(self._update_viewport)
        self._viewport_timer.start(30)

        self._set_analysis_parameters()
        self._is_initialized = True

    def scan(self):
        if not self._analyzer.is_working:
            for locator in self._items_locators.values():
                self.scene.removeItem(locator)
            self._items_locators = dict()

            self._analyzer.begin_analysis()

        while self._analyzer.is_working:
            QApplication.processEvents()
            current_led_index = self._analyzer.analyze_step()

            # TODO create a class to manage locators
            if current_led_index not in self._items_locators and current_led_index > 0:
                x = self._analyzer.locators[current_led_index][0] - self._locator_radius / 2
                y = self._analyzer.locators[current_led_index][1] - self._locator_radius / 2
                rect = QGraphicsRectItem(QRectF(x, y, self._locator_radius, self._locator_radius))
                rect.setPen(QPen(QColor.fromRgb(255, 0, 0)))
                self._items_locators[current_led_index] = rect
                self.scene.addItem(rect)

            self.progress.setValue(current_led_index - self._analyzer.led_start)

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
        self.save_settings()
        self._viewport_timer.stop()
        self._analyzer.end_analysis()
        super().closeEvent(event)

    @error_reported("Camera change")
    def _combo_cameras_changed(self, index):
        if index >= 0:
            self._analyzer.set_camera_index(index)
            self.save_settings()

    @error_reported("Serial Port change")
    def _combo_serial_port_changed(self, index):
        if index >= 0:
            self._analyzer.set_led_board_port(self._combo_serial_ports.currentText())
            self.save_settings()

    @error_reported("Pixel Type change")
    def _radio_pixel_type_rgb_toggled(self, value):
        self._analyzer.set_pixel_type(int(self._radio_pixel_type_rgbw.isChecked()))

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

        self._item_image.setPixmap(self._frame_to_pixmap(image))

    @staticmethod
    def _frame_to_pixmap(frame: cv2.Mat) -> QPixmap:
        height, width, channel = frame.shape
        bytes_per_line = 3 * width
        qt_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
        return QPixmap.fromImage(qt_image)

    def save_settings(self):
        if not self._is_initialized:
            return
        settings = QSettings("Frangitron", "LEDBoard")
        settings.setValue("camera_index", self._combo_cameras.currentIndex())
        settings.setValue("port_name", self._combo_serial_ports.currentText())
        settings.setValue("pixel_type", self._radio_pixel_type_rgbw.isChecked())

    def load_settings(self):
        settings = QSettings("Frangitron", "LEDBoard")
        self._combo_cameras.setCurrentIndex(settings.value("camera_index", None, type=int))
        self._combo_serial_ports.setCurrentIndex(self._combo_serial_ports.findText(
            settings.value("port_name", None, type=str)
        ))
        is_rgbw = settings.value("pixel_type", None, type=bool)
        self._radio_pixel_type_rgb.setChecked(not is_rgbw)
        self._radio_pixel_type_rgbw.setChecked(is_rgbw)
