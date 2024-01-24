import dataclasses
import serial
import struct

from .protocol import SerialProtocol


class SerialCommunicator:
    def __init__(self, port):
        self.serial_port = serial.Serial()
        self.serial_port.baudrate = 115200
        self.serial_port.dtr = True  # TODO: check if needed on linux ?
        self.serial_port.port = port
        self._is_open = False

    def connect(self):
        if not self._is_open:
            self.serial_port.open()
            self._is_open = True

    def disconnect(self):
        if self._is_open:
            self.serial_port.close()
            self._is_open = False

    def send(self, message_type, message_data):
        if not self._is_open:
            return

        packed = self._pack(message_data)
        message = bytearray([SerialProtocol.flag_begin, message_type])
        message += packed
        message += bytearray([SerialProtocol.flag_end])
        self.serial_port.write(message)

    def receive(self):
        if not self._is_open:
            return

        response = bytearray()
        while self.serial_port.in_waiting > 0:
            response += self.serial_port.read()

        if len(response) == 0:
            return

        dataclass = SerialProtocol.message_type_to_data_type[response[1]]
        packing_format = self._make_packing_format(dataclass)
        data = struct.unpack("<" + packing_format, response[SerialProtocol.header_size + 1:-1])

        result = dataclass()
        index = 0
        for field in dataclasses.fields(dataclass):
            if field.type == int:
                setattr(result, field.name, data[index])
                index += 1
            elif field.type == float:
                setattr(result, field.name, data[index])
                index += 1
            elif field.type == str:
                value = "".join([b.decode() for b in data[index: index + len(field.default)]])
                setattr(result, field.name, value)
                index = index + len(field.default) + 1

        return result

    def _pack(self, data):
        format_ = self._make_packing_format(data)
        values = vars(data).values()
        return struct.pack("<i" + format_, struct.calcsize(format_), *values)

    @staticmethod
    def _make_packing_format(dataclass) -> str:
        format_ = ""
        for field in dataclasses.fields(dataclass):
            if field.type == int:
                format_ += "i"
            elif field.type == float:
                format_ += "f"
            elif field.type == str:
                format_ += "c" * (len(field.default) + 1)  # +1 for terminator
        return format_