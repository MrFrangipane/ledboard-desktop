import logging
import sys

import imageio
from imageio.core.format import Format
from PySide6.QtMultimedia import QMediaDevices


_logger = logging.getLogger(__name__)


class Camera:

    def __init__(self):
        self._capture: Format.Reader = None

    def open(self, index):
        self._capture = imageio.get_reader(f'<video{index}>')

    def read(self):
        if self._capture is not None:
            return self._capture.get_next_data()

    @staticmethod
    def get_camera_names():
        return [camera.description() for camera in QMediaDevices.videoInputs()]
