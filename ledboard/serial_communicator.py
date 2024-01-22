import struct
import time
import serial


class SerialProtocol:
    """
    Typical message

    - 0   begin (1 byte)
    - 1   command (1 byte)
    - 2   data type (1 byte)
    - 3   data length (4 bytes)
    - 7   data (n bytes)
    - n+7 end (1 byte)
    """
    class DataType:
        StructTest = 0x30  # "0""

    flag_begin_command = 0x3c  # "<"
    flag_begin_data = 0x7c  # "|"
    flag_end = 0x3e  # ">""

    response_ok = 0x21  # "!"

    command_A = 0x41  # "A"
    command_B = 0x42  # "B"
    command_C = 0x43  # "C"
    command_D = 0x44  # "D"
    command_E = 0x45  # "E"
    command_F = 0x46  # "F"
    command_G = 0x47  # "G"
    command_H = 0x48  # "H"


def r(serial_port, fmt="<if"):
    received = serial_port.read(struct.calcsize(fmt))
    return struct.unpack(fmt, received)


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
        message = (bytearray([
            SerialProtocol.flag_begin_command,
            SerialProtocol.command_A,
            SerialProtocol.DataType.StructTest
        ]))
        message += data
        message += bytearray([SerialProtocol.flag_end])

        arduino_port.write(message)

        response = arduino_port.read(1)[0]
        if response == SerialProtocol.response_ok:
            print(f"OK f: {i * 0.33} i: {i}")

        i += 1
        time.sleep(1)
