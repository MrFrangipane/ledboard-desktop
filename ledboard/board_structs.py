from dataclasses import dataclass

from pythonarduinoserial.types import *


@dataclass
class BoardSettings:
    name: StringType(4) = StringDefault(4)  # includes null terminator
    hardware_revision: IntegerType() = 1
    hardware_id: BytesType(8) = BytesDefault(8)
    ip_address: BytesType(4) = BytesDefault(4)


all_structs = [
    BoardSettings
]
