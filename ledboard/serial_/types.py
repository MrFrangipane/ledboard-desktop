from dataclasses import field
from typing import Annotated


class _SerializationAnnotation:
    def __init__(self, struct_format=None, length=1):
        self.struct_format = struct_format
        self.length = length


def StringType(length):
    return Annotated[str, _SerializationAnnotation(struct_format="c", length=length)]


def IntegerType():
    return Annotated[int, _SerializationAnnotation(struct_format="i")]


def FloatType():
    return Annotated[float, _SerializationAnnotation(struct_format="f")]


def BooleanType():
    return Annotated[bool, _SerializationAnnotation(struct_format="c")]


def BytesType(length):
    return Annotated[bytes, _SerializationAnnotation(struct_format="c", length=length)]


def ListType(type_, length):
    return Annotated[list[type_], _SerializationAnnotation(length=length)]


def ListDefault(type_, length):
    return field(default_factory=lambda: [type_()] * length)


def StringDefault(length):
    return " " * length


def BytesDefault(length):
    return bytes(length)
