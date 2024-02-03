from dataclasses import dataclass

from pythonarduinoserial.types import *


@dataclass
class BoardSettings:
    name: StringType(8) = StringDefault(8)  # includes null terminator (8 for proper alignment)
    hardware_revision: IntegerType() = 1
    firmware_revision: IntegerType() = 1
    hardware_id: BytesType(8) = BytesDefault(8)
    ip_address: BytesType(4) = BytesDefault(4)
    universe_a: IntegerType() = 0
    universe_b: IntegerType() = 1
    universe_c: IntegerType() = 2
    pixel_per_universe: IntegerType() = 150
    do_save_and_reboot: IntegerType() = 0  # 4 bytes int instead of bool to avoid manual bytes padding
    do_reboot_bootloader: IntegerType() = 0

# string(8) start    : b'01 00 00 00 | 01 00 00 00 | 00 00 00 00 00 00 00 00 | 61 62 63 64 | 02 00 00 00 | 96 00 00 00 | 00 | 20 20 20 20 20 20 20 00 | XX XX XX', len=40
# string(7) end      : b'20 20 20 20 20 20 00 XX | 01 00 00 00 | 01 00 00 00 | 00 00 00 00 00 00 00 00 | 61 62 63 64 | 02 00 00 00 | 96 00 00 00 | 00 | XX XX XX', len=40
# "manually aligned" : b'20 20 20 20 20 20 20 00 | 01 00 00 00 | 01 00 00 00 | 00 00 00 00 00 00 00 00 | 61 62 63 64 | 02 00 00 00 | 96 00 00 00 | 00 00 00 00', len=40


all_structs = [
    BoardSettings
]


if __name__ == "__main__":
    import argparse
    import logging
    import sys

    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    parser = argparse.ArgumentParser(description="RP2040 LED Board - C Header exporter")
    parser.add_argument("--export-header", "-e", required=True, help="Export C Header to given filepath")
    args = parser.parse_args()

    from pythonarduinoserial.c_header_exporter import CHeaderExporter

    c_header_exporter = CHeaderExporter(
        struct_types=all_structs,
        namespace="Frangitron",
        include_guard_name="PLATFORMIO_SERIALPROTOCOL_H"
    )
    with open(args.export_header, "w+") as c_header_file:
        c_header_file.write(c_header_exporter.export())
