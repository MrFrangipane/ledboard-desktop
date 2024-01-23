import time

from serial_.communicator import SerialCommunicator
from serial_.protocol import SerialProtocol


if __name__ == '__main__':
    serial_communicator = SerialCommunicator(port="COM13")
    serial_communicator.begin()

    i = 1
    while True:
        struct_test = SerialProtocol.StructTest(
            some_int=i,
            some_float=i * 0.33
        )
        serial_communicator.send(SerialProtocol.MessageType.get_board_info, struct_test)
        time.sleep(0.1)  # where to put it ?

        print(serial_communicator.receive())

        # time.sleep(0.25)
        i += 1
