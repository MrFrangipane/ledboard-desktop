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
