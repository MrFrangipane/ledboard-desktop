from serial.tools.list_ports import comports as list_serial_ports
from pythonarduinoserial.communicator import SerialCommunicator

from ledboard.board_structs import BoardSettings, all_structs


class LedBoard:
    def __init__(self):
        self.serial_communicator = SerialCommunicator(structs=all_structs)

    @staticmethod
    def available_serial_port_names():
        return [port.name for port in list_serial_ports()]

    def set_serial_port_name(self, name):
        self.serial_communicator.set_port_name(name)

    def configure(self, settings: BoardSettings):
        self.serial_communicator.send(settings)

    def get_configuration(self) -> BoardSettings:
        return self.serial_communicator.receive(BoardSettings)


if __name__ == "__main__":
    import logging
    import sys
    import time

    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    if "--export-header" in sys.argv:
        header_filepath = "E:/PROJECTS_2024/rp2040-led-board/firmware/platformio/include/SerialProtocol.h"
        from pythonarduinoserial.c_header_exporter import CHeaderExporter

        c_header_exporter = CHeaderExporter(
            struct_types=all_structs,
            namespace="Frangitron",
            include_guard_name="PLATFORMIO_SERIALPROTOCOL_H"
        )
        with open(header_filepath, "w+") as c_header_file:
            c_header_file.write(c_header_exporter.export())

    if "--test-communication" in sys.argv:
        board = LedBoard()

        logging.info(f"Available ports:")
        for name in board.available_serial_port_names():
            logging.info(name)

        board.set_serial_port_name("COM15")

        settings = BoardSettings(
            name="Demo",
            ip_address=bytes([192, 168, 20, 201])
        )
        logging.info(f"Sending settings: {settings}")
        board.configure(settings)
        time.sleep(1)

        settings = board.get_configuration()
        logging.info(f"Received settings: {settings}")
