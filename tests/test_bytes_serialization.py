"""
This demonstrates usage of `ledboard.serial_.types` to construct bytes-serializable dataclasses
"""
from dataclasses import dataclass
from unittest import TestCase

from ledboard.serial_.byte_serializer import ByteSerializer
from ledboard.serial_.byte_deserializer import ByteDeserializer
from ledboard.serial_.types import *


# FIXME factorize with c header exporter tests
@dataclass
class AllTypes:
    string: StringType(10) = StringDefault(10)
    float: FloatType() = 0.0
    boolean: BooleanType() = False
    integer: IntegerType() = 0
    integers: ListType(IntegerType(), 3) = ListDefault(IntegerType(), 3)
    bytes: BytesType(5) = BytesDefault(5)


@dataclass
class Nested:
    string: StringType(5) = StringDefault(5)
    nested: AllTypes = AllTypes()
    nesteds: ListType(AllTypes, 2) = ListDefault(AllTypes, 2)


class TestSerializeToBytes(TestCase):

    def setUp(self):
        self.serializer = ByteSerializer()

        #
        # Modify each value to ensure actual data is serialized (not default values)
        self.all_types = AllTypes()
        self.all_types.string = "ABCDEFGHIJ"
        self.all_types.float = 0.5
        self.all_types.integer = 5
        self.all_types.integers = [1, 2, 3]
        self.all_types.bytes = b'\x01\x02\x03\x04\x05'

        self.nested = Nested()
        self.nested.nested = self.all_types
        self.nested.nesteds = [self.all_types, self.all_types]

        self._all_types_as_bytes = (
            b'\x41\x42\x43\x44\x45\x46\x47\x48\x49\x4a'  # string 
            b'\x00\x00\x00\x3f'  # float
            b'\x00'  # bool
            b'\x05\x00\x00\x00'  # int
            b'\x01\x00\x00\x00\x02\x00\x00\x00\x03\x00\x00\x00'  # [int, int, int]
            b'\x01\x02\x03\x04\x05'  # [byte, byte, byte, byte, byte]
        )

        self._nested_as_bytes = (
            b'\x20\x20\x20\x20\x20' +  # string
            self._all_types_as_bytes * 3
        )

    def test_serialize_all_types(self):
        output = self.serializer.to_bytes(self.all_types)

        self.assertEqual(
            output,
            self._all_types_as_bytes
        )

    def test_serialize_nested(self):
        output = self.serializer.to_bytes(self.nested)

        self.assertEqual(
            output,
            self._nested_as_bytes
        )

    def test_deserialize_all_types(self):
        deserializer = ByteDeserializer(self._all_types_as_bytes)
        output = deserializer.to_object(AllTypes)

        self.assertEqual(
            output,
            self.all_types
        )

    def test_deserialize_nested(self):
        deserializer = ByteDeserializer(self._nested_as_bytes)
        output = deserializer.to_object(Nested)

        self.assertEqual(
            output,
            self.nested
        )
