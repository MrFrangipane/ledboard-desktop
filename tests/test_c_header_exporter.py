"""
This demonstrates usage of `ledboard.serial_.types` to export C header files
"""
from dataclasses import dataclass
from unittest import TestCase

from ledboard.serial_.c_header_exporter import CHeaderExporter
from ledboard.serial_.types import *


# FIXME factorize with serializer tests
@dataclass
class AllTypes:
    field_string: StringType(10) = StringDefault(10)
    field_float: FloatType() = 0.0
    field_boolean: BooleanType() = False
    field_integer: IntegerType() = 0
    field_integers: ListType(IntegerType(), 3) = ListDefault(IntegerType(), 3)
    field_bytes: BytesType(5) = BytesDefault(5)


@dataclass
class Nested:
    string: StringType(5) = StringDefault(5)
    nested: AllTypes = AllTypes()
    nesteds: ListType(AllTypes, 2) = ListDefault(AllTypes, 2)


class TestCHeaderExporter(TestCase):

    def setUp(self):
        self.exporter = CHeaderExporter()

        #
        # Modify each value to ensure default values are used anyways
        self.all_types = AllTypes()
        self.all_types.field_string = "ABCDEFGHIJ"
        self.all_types.field_float = 0.5
        self.all_types.field_boolean = True
        self.all_types.field_integer = 5
        self.all_types.field_integers = [1, 2, 3]
        self.all_types.field_bytes = b'\x01\x02\x03\x04\x05'

        self.nested = Nested()
        self.nested.nested = self.all_types
        self.nested.nesteds = [self.all_types, self.all_types]

        self._all_types_as_c_header = """
struct AllTypes {
    char fieldString[10] = "          ";
    float fieldFloat = 0.0;
    bool fieldBoolean = false;
    int fieldInteger = 0;
    int fieldIntegers[3] = {0, 0, 0};
    byte fieldBytes[5] = {0x00, 0x00, 0x00, 0x00, 0x00};
};
""".strip()

    def test_export_all_types(self):
        output = self.exporter.export(self.all_types)

        self.assertEqual(
            self._all_types_as_c_header,
            output
        )
