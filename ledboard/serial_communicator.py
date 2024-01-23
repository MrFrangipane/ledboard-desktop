import struct
import time
import serial
from binascii import hexlify


class SerialProtocol:
    """
    Message topology

    ```
    |   0   |       1      | 2 | 3 | 4 | 5 |   n  | 6 + n |
    | begin | message type |   data size   | data |  end  |
    |-------|           header             | data |-------|
    ```
    """
    class MessageType:
        response_ok = 0x41      # "A"
        get_board_info = 0x42   # "B"

    flag_begin = 0x3c   # "<"
    flag_end = 0x3e     # ">""


if __name__ == '__main__':
    arduino_port = serial.Serial()
    arduino_port.baudrate = 115200
    arduino_port.dtr = True  # TODO: check if need on linux ?
    arduino_port.port = "COM13"
    arduino_port.open()

    print(arduino_port)

    i = 0
    while True:
        data = struct.pack('<iif', struct.calcsize('<if'), i, i * 0.33)
        message = bytearray([
            SerialProtocol.flag_begin,
            SerialProtocol.MessageType.get_board_info,
        ]) + data + bytearray([SerialProtocol.flag_end])

        print(f"f: {i * 0.33} i: {i}")

        arduino_port.write(message)

        time.sleep(0.1)

        response = bytearray()
        while arduino_port.in_waiting > 0:
            response += arduino_port.read(1)

        print(hexlify(response, sep=" "))

        i += 1
        time.sleep(0)
