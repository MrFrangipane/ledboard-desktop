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
    def __init__(self, struct_format_token=None, length=1):
        self._struct_format_token = struct_format_token
        self.length = length

    @property
    def struct_format(self):
        return f"<{self._struct_format_token * self.length}"


def StringType(length):
    return Annotated[str, SerializationAnnotation(struct_format_token="c", length=length)]


def IntegerType():
    return Annotated[int, SerializationAnnotation(struct_format_token="i")]


def FloatType():
    return Annotated[float, SerializationAnnotation(struct_format_token="f")]


def BooleanType():
    return Annotated[bool, SerializationAnnotation(struct_format_token="c")]


def BytesType(length):
    return Annotated[bytes, SerializationAnnotation(struct_format_token="c", length=length)]


def ListType(type_, length):
    return Annotated[list[type_], SerializationAnnotation(length=length)]


def ListDefault(type_, length):
    return field(default_factory=lambda: [type_()] * length)


def StringDefault(length):
    return " " * length


def BytesDefault(length):
    return bytes(length)
