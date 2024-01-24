from serial.tools.list_ports import comports as list_serial_ports

from ledboard.serial_.communicator import SerialCommunicator
from ledboard.serial_.protocol import SerialProtocol


class LedBoard:
    def __init__(self):
        self.serial_communicator = SerialCommunicator()

    def connect(self) -> bool:
        return self.serial_communicator.connect()

    def disconnect(self):
        self.serial_communicator.disconnect()

    def illuminate(self, led_index, brightness):
        self.serial_communicator.send(
            SerialProtocol.MessageType.illuminate,
            SerialProtocol.IlluminatedLed(
                led_index=led_index,
                r=brightness,
                g=brightness,
                b=brightness,
                w=brightness
            )
        )

    def configure(self, pixel_type: int):
        self.serial_communicator.send(
            SerialProtocol.MessageType.configure,
            SerialProtocol.Configuration(pixel_type=pixel_type)
        )

    @staticmethod
    def get_serial_port_names():
        return [port.name for port in list_serial_ports()]

    def set_serial_port_name(self, name):
        self.serial_communicator.set_port_name(name)
