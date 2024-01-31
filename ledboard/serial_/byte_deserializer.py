import struct
from typing import get_type_hints, Annotated, get_origin, get_args, Any

from ledboard.serial_.types import SerializationAnnotation


class ByteDeserializer:

    def __init__(self, input_: bytes):
        self._input = input_
        self._index = 0

    def to_object(self, type_):
        output = type_()

        items = get_type_hints(output, include_extras=True).items()
        for name, type_hint in items:
            setattr(output, name, self._deserialize(type_hint))

        return output

    def _deserialize(self, type_hint) -> Any:
        if get_origin(type_hint) == Annotated:
            type_, annotation = get_args(type_hint)
            if get_origin(type_) == list:
                return self._deserialize_list(type_, annotation)
            else:
                return self._deserialize_value(type_, annotation)
        else:
            return self.to_object(type_hint)

    def _deserialize_value(self, type_, annotation) -> Any:
        assert isinstance(annotation, SerializationAnnotation)
        value = None

        if type_ == bytes:
            value = bytes(self._input[self._index:self._index + annotation.length])
            self._index += annotation.length

        elif type_ == bool:
            value = bool(self._input[self._index])
            self._index += 1

        elif type_ == str:
            value = self._input[self._index:self._index + annotation.length].decode('ascii')
            self._index += annotation.length

        elif type_ in [float, int]:
            size = struct.calcsize(annotation.struct_format)
            value = struct.unpack(annotation.struct_format, self._input[self._index:self._index + size])[0]
            self._index += size

        return value

    def _deserialize_list(self, type_, annotation) -> list[Any]:
        sub_hint = get_args(type_)[0]
        return [self._deserialize(sub_hint) for _ in range(annotation.length)]
