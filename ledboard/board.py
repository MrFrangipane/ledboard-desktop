from ledboard.serial_.communicator import SerialCommunicator
from ledboard.serial_.protocol import SerialProtocol


class LedBoard:
    def __init__(self):
        self.serial_communicator = SerialCommunicator(port="COM13")

    def connect(self):
        self.serial_communicator.connect()

    def disconnect(self):
        self.serial_communicator.disconnect()

    def illuminate(self, led_index, brightness):
        self.serial_communicator.send(
            SerialProtocol.MessageType.illuminate,
            SerialProtocol.IlluminatedLed(led_index=led_index, w=brightness)
        )
