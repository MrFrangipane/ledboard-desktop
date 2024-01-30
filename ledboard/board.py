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

    def configure(self, pixel_type: int, pixel_count: int, id_: str = "12345678"):
        self.serial_communicator.send(
            SerialProtocol.Direction.Send,
            SerialProtocol.DataTypeCode.configuration,
            SerialProtocol.Configuration(
                pixel_type=pixel_type,
                pixel_count=pixel_count,
                board_id=id_.encode('ascii')
            )
        )

    def get_configuration(self) -> SerialProtocol.Configuration:
        self.serial_communicator.send(
            SerialProtocol.Direction.Receive,
            SerialProtocol.DataTypeCode.configuration
        )
        return self.serial_communicator.receive()

    @staticmethod
    def get_serial_port_names():
        return [port.name for port in list_serial_ports()]

    def set_serial_port_name(self, name):
        self.serial_communicator.set_port_name(name)


if __name__ == "__main__":
    import time
    import logging
    import serial
    logging.basicConfig(level=logging.INFO)

    board = LedBoard()

    logging.info("== Ports ==")
    ports = board.get_serial_port_names()
    logging.info(f"{ports}, using {ports[-1]}")
    board.set_serial_port_name(ports[-1])

    board.connect()
    while True:
        try:
            time.sleep(1)
            logging.info("-- Get configuration --")
            logging.info(board.get_configuration())
            time.sleep(1)
            logging.info("-- Set configuration --")
            logging.info(board.configure(0, 20))
        except KeyboardInterrupt:
            break
        except serial.serialutil.SerialException:
            continue
    board.disconnect()
