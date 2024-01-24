import cv2
from PySide6.QtCore import QThread
from PySide6.QtWidgets import QApplication

from ledboard.camera import Camera
from ledboard.board import LedBoard


class Analyzer:

    def __init__(self, ledboard_port, camera_index):
        self.blur_radius = 12
        self.brightness = 15
        self.comparison_light_on_threshold = 100
        self.comparison_light_off_threshold = 50
        self.is_working = False
        self.led_start = 1
        self.led_end = 100
        self.viewport_image = None

        self._camera = Camera(camera_index)
        self._led_board = LedBoard(ledboard_port)

        self._background_image = None
        self._current_led_index = -1

        self.led_coords = list()

        self.HAHA = 0

    def capture_blurred_image(self):
        image = self._camera.read()
        blur = self.blur_radius * 2 + 1, self.blur_radius * 2 + 1
        if self.blur_radius > 0:
            image = cv2.GaussianBlur(image, blur, 0)
        return image

    def analyze_step(self) -> int:
        if not self.is_working:
            return -1

        self._wait_for_light_off()

        maximum_value, maximum_location = self._wait_for_light_on()
        self.led_coords.append(maximum_location)
        self._current_led_index += 1

        if self._current_led_index > self.led_end:
            self.end_analysis()
            return -1

        return self._current_led_index

    def illuminate(self, led_index: int) -> None:
        self._led_board.connect()
        self._led_board.illuminate(led_index, self.brightness)
        self._led_board.disconnect()

    def _wait_for_light_on(self) -> [int, int]:
        self._led_board.illuminate(self._current_led_index, self.brightness)

        image = self.capture_blurred_image()
        maximum_value, maximum_location = self._compare_with_background(image)
        print(f"wait for light on {maximum_value}")
        while maximum_value < self.comparison_light_on_threshold and self.is_working:
            image = self.capture_blurred_image()
            maximum_value, maximum_location = self._compare_with_background(image)
            print(f"wait for light on {maximum_value}")
            QApplication.processEvents()

        return maximum_value, maximum_location

    def _wait_for_light_off(self) -> None:
        self._led_board.illuminate(-1, 0)

        image = self.capture_blurred_image()
        maximum_value, maximum_location = self._compare_with_background(image)
        print(f"wait for light off {maximum_value}")
        while maximum_value > self.comparison_light_off_threshold and self.is_working:
            image = self.capture_blurred_image()
            maximum_value, maximum_location = self._compare_with_background(image)
            print(f"wait for light off {maximum_value}")
            QApplication.processEvents()

    def _compare_with_background(self, image) -> [int, tuple[int, int]]:
        difference = cv2.absdiff(self._background_image, image)
        self.viewport_image = difference
        gray = cv2.cvtColor(difference, cv2.COLOR_BGR2GRAY)
        _, maximum_value, _, maximum_location = cv2.minMaxLoc(gray)
        return maximum_value, maximum_location

    def begin_analysis(self):
        self.is_working = True
        self._current_led_index = self.led_start
        self.led_coords = list()

        self._led_board.connect()
        self._led_board.illuminate(-1, 0)

        QThread.currentThread().msleep(100)

        self._background_image = self.capture_blurred_image()

    def end_analysis(self):
        self.is_working = False
        self._current_led_index = -1

        self._led_board.disconnect()
