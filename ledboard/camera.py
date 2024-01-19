import logging

import cv2
from PySide6.QtCore import QSettings


_logger = logging.getLogger(__name__)


class Camera:

    def __init__(self):
        self._index: int = None
        self._capture: cv2.VideoCapture = None

    def open(self):
        self.load_settings()

        if self._index is None:
            self.detect()
            return

        if not self.check_capture():
            self.detect()

    def check_capture(self):
        capture = cv2.VideoCapture(self._index)

        if capture.isOpened():
            _logger.info(f"Checking camera {self._index}")

            ret, frame = capture.read()
            if ret:
                _logger.info("Frame captured successfully")
                self._capture = capture
                return True

            else:
                _logger.warning("Failed to capture a frame. Closing the camera")
                capture.release()

        return False

    def detect(self):
        for camera_index in range(0, 10):
            self._index = camera_index
            if self.check_capture():
                self.save_settings()
                return

        raise IOError('No camera detected')

    def save_settings(self):
        settings = QSettings("Frangitron", "LEDBoard")
        settings.setValue("camera_index", self._index)

    def load_settings(self):
        settings = QSettings("Frangitron", "LEDBoard")
        self._index = settings.value("camera_index", None, type=int)

    def read(self):
        return self._capture.read()

    def release(self):
        return self._capture.release()
