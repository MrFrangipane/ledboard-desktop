__all__ = [
    "BooleanType",
    "BytesDefault",
    "BytesType",
    "FloatType",
    "IntegerType",
    "ListDefault",
    "ListType",
    "SerializationAnnotation",
    "StringDefault",
    "StringType"
]
from dataclasses import field
from typing import Annotated


class SerializationAnnotation:
    def __init__(self, c_name=None, struct_format_token=None, length=1):
        self._struct_format_token = struct_format_token
        self.length = length
        self.c_name = c_name

    @property
    def struct_format(self):
        return f"<{self._struct_format_token * self.length}"


def StringType(length):
    return Annotated[str, SerializationAnnotation(c_name="char", struct_format_token="c", length=length)]


def IntegerType():
    return Annotated[int, SerializationAnnotation(c_name="int", struct_format_token="i")]


def FloatType():
    return Annotated[float, SerializationAnnotation(c_name="float", struct_format_token="f")]


def BooleanType():
    return Annotated[bool, SerializationAnnotation(c_name="bool", struct_format_token="c")]


def BytesType(length):
    return Annotated[bytes, SerializationAnnotation(c_name="byte", struct_format_token="c", length=length)]


def ListType(type_, length):
    return Annotated[list[type_], SerializationAnnotation(length=length)]


def ListDefault(type_, length):
    return field(default_factory=lambda: [type_()] * length)


def StringDefault(length):
    return " " * length


def BytesDefault(length):
    return bytes(length)
