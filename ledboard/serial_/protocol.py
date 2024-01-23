from dataclasses import dataclass


class SerialProtocol:
    """
    Message topology

    ```
    |   0   |       1      | 2 | 3 | 4 | 5 |   n  | 6 + n |
    | begin | message type |   data size   | data |  end  |
    |-------|           header             | data |-------|
    ```
    """
    class MessageType:
        response_ok = 0x41          # "A"
        get_board_info = 0x42       # "B"
        responseBoardInfo = 0x43    # "C"

    @dataclass
    class StructTest:
        some_int: int = 0
        some_float: float = 0.0

    @dataclass
    class BoardInfo:
        board_version: int = 0
        id_address: str = "000.000.000.000"
        temperature: float = 0.0

    flag_begin = 0x3c   # "<"
    flag_end = 0x3e     # ">""
