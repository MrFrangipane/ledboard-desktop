from serial.tools.list_ports import comports as list_serial_ports

from ledboard.serial_.communicator import SerialCommunicator
from ledboard.serial_.protocol import SerialProtocol


class LedBoard:
    def __init__(self):
        self.serial_communicator = SerialCommunicator()

    def connect(self):
        self.serial_communicator.connect()

    def disconnect(self):
        self.serial_communicator.disconnect()

    def illuminate(self, led_index, brightness):
        self.serial_communicator.send(
            SerialProtocol.MessageType.illuminate,
            SerialProtocol.IlluminatedLed(led_index=led_index, w=brightness)
        )

    @staticmethod
    def get_serial_port_names():
        return [port.name for port in list_serial_ports()]

    def set_serial_port_name(self, name):
        self.serial_communicator.set_port_name(name)
