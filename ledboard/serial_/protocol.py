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
        illuminate = 0x41               # "A"
        board_info_get = 0x42           # "B"
        board_info_get_response = 0x43  # "C"

    @dataclass
    class IlluminatedLed:
        led_index: int = 0
        r: int = 0
        g: int = 0
        b: int = 0
        w: int = 0

    message_type_to_data_type = {
        MessageType.illuminate: IlluminatedLed
    }

    header_size = 5
    flag_begin = 0x3c   # "<"
    flag_end = 0x3e     # ">"
