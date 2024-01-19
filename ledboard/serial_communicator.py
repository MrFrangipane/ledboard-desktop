import struct
import time

import serial


class SerialProtocol:
    class DataType:
        INT = 0x30  # 0
        FLOAT = 0x31  # 1

    beginFlag = 0x3c  # <
    endFlag = 0x3e  # >
    temperature = 0x41  # A


def r(serialPort, fmt="<if"):
    received = serialPort.read(struct.calcsize(fmt))
    return struct.unpack(fmt, received)


if __name__ == '__main__':
    serial_port = serial.Serial()
    serial_port.baudrate = 115200
    serial_port.dtr = True  # TODO: check if need on linux ?
    serial_port.port = "COM13"
    serial_port.open()

    print(serial_port)

    i = 0
    while True:
        serial_port.write(struct.pack('<if', i, 7.75))

        if serial_port.in_waiting > 0:
            print(" >", i)
            print("someCountingStruct", r(serial_port))
            print("someReceivingStruct", r(serial_port))

            i += 1

        time.sleep(1)

    # values = bytearray([
    #     SerialProtocol.beginFlag,
    #     SerialProtocol.temperature,
    #     SerialProtocol.DataType.FLOAT
    # ])
    # values += struct.pack('if', 13, 0.5)
    # values += bytearray([
    #     SerialProtocol.endFlag
    # ])
