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

    if "--test-communication" in sys.argv:
        board = LedBoard()

        logging.info(f"Available ports:")
        for name in board.available_serial_port_names():
            logging.info(name)

        board.set_serial_port_name("COM15")

        #
        # CONFIGURE
        settings = BoardSettings(
            name="Demo",
            ip_address=bytes([192, 168, 1, 203]),
            # do_reboot_bootloader=True,
            do_save_and_reboot=False,
            pixel_per_universe=150
        )
        logging.info(f"Sending settings: {settings}")
        board.configure(settings)

        time.sleep(1)

        #
        # GET CONFIGURATION
        settings = board.get_configuration()
        logging.info(f"Received settings: {settings}")
        print(".".join([str(int(b)) for b in settings.ip_address]))
