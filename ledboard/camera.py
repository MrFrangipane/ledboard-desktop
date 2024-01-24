import logging

import imageio
from imageio.core.format import Format

_logger = logging.getLogger(__name__)


class Camera:

    def __init__(self, index):
        self._capture: Format.Reader = imageio.get_reader(f'<video{index}>')

    def read(self):
        return self._capture.get_next_data()
