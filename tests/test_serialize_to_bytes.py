"""
This demonstrates usage of `ledboard.serial_.types` to construct bytes-serializable dataclasses
"""
from dataclasses import dataclass
from unittest import TestCase

from ledboard.serial_.byte_serializer import ByteSerializer
from ledboard.serial_.types import *


@dataclass
class DataStructA:
    string: StringType(10) = StringDefault(10)
    float: FloatType() = 0.0
    boolean: BooleanType() = False
    integer: IntegerType() = 0
    integers: ListType(IntegerType(), 3) = ListDefault(IntegerType(), 3)
    bytes_: BytesType(5) = BytesDefault(5)


@dataclass
class DataStructB:
    string: StringType(5) = StringDefault(5)
    nested: DataStructA = DataStructA()
    nesteds: ListType(DataStructA, 2) = ListDefault(DataStructA, 2)


class TestSerializeToBytes(TestCase):

    def setUp(self):
        self.serializer = ByteSerializer()
        self.input_data = DataStructB()

    def test_serialize_to_bytes(self):
        output = self.serializer.serialize(self.input_data)

        self.assertEqual(
            output,
            bytes([0x10, 0x11, 0x12, 0x13, 0x14])
        )
