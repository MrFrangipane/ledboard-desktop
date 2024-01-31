import struct
from typing import get_type_hints, Annotated, get_origin, get_args

from ledboard.serial_.types import SerializationAnnotation


class CHeaderExporter:

    def __init__(self):
        self._output = ""

    def export(self, object_) -> str:
        # items = get_type_hints(object_, include_extras=True).items()
        # for name, type_hint in items:
        #     self._serialize(getattr(object_, name), type_hint)

        return self._output
    #
    # def _serialize(self, value, type_hint):
    #     if get_origin(type_hint) == Annotated:
    #         type_, annotation = get_args(type_hint)
    #         if get_origin(type_) == list:
    #             self._serialize_list(value, type_)
    #         else:
    #             self._serialize_value(value, type_, annotation)
    #     else:
    #         self.to_bytes(value)
    #
    # def _serialize_value(self, value, type_, annotation):
    #     assert isinstance(value, type_)
    #     assert isinstance(annotation, SerializationAnnotation)
    #
    #     if type_ == bytes:
    #         self._output += value
    #
    #     elif type_ == bool:
    #         self._output += bytes([value])
    #
    #     elif type_ == str:
    #         if len(value) < annotation.length:
    #             self._output += bytes(value + " " * (annotation.length - len(value)), "ascii")
    #         else:
    #             self._output += bytes(value[:annotation.length], "ascii")
    #
    #     elif type_ in [float, int]:
    #         self._output += struct.pack(annotation.struct_format, value)
    #
    # def _serialize_list(self, value, type_):
    #     sub_hint = get_args(type_)[0]
    #     for item in value:
    #         self._serialize(item, sub_hint)
