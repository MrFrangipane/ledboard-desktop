import logging
import dataclasses
import serial
import struct

from .protocol import SerialProtocol

_logger = logging.getLogger(__name__)


class SerialCommunicator:
    def __init__(self):
        self._serial_port: serial.Serial = None
        self._is_open = False
        self._name = None

    def set_port_name(self, name):
        self.disconnect()
        self._name = name
        self.connect()
        self.disconnect()

    def connect(self):
        if self._name is None:
            return False

        if not self._is_open:
            self._serial_port = serial.Serial()
            self._serial_port.baudrate = 115200
            self._serial_port.dtr = True
            self._serial_port.port = self._name
            self._serial_port.open()
            self._is_open = True

        return True

    def disconnect(self):
        if self._is_open:
            self._serial_port.close()
            self._is_open = False

    def send(self, message_type, message_data):
        if not self._is_open:
            _logger.info(f"Attempting to send while port not open, {message_type}")
            return

        packed = self._pack(message_data)
        message = bytearray([SerialProtocol.flag_begin, message_type])
        message += packed
        message += bytearray([SerialProtocol.flag_end])
        self._serial_port.write(message)

    def receive(self):
        if not self._is_open:
            return

        response = bytearray()
        while self._serial_port.in_waiting > 0:
            response += self._serial_port.read()

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
