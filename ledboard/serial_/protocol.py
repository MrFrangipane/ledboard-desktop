from dataclasses import dataclass


class SerialProtocol:
    """
    Message topology

    ```
    |   0   |    1      |     2     |   n  | 3 + n |
    | begin | direction | data type | data |  end  |
    |-------| ------ header ------- | data |-------|
    ```
    """
    class Direction:
        Send = 0
        Receive = 1

    header_size = 2
    flag_begin = 0x3c   # "<"
    flag_end = 0x3e     # ">"

    # -------------------------------------- #

    class PixelType:
        RGB = 0
        RGBW = 1

    class DataTypeCode:
        configuration = 0x41
        illumination = 0x42

    @dataclass
    class Configuration:
        pixel_type: int = 0
        pixel_count: int = 60
        board_id: bytes = bytes([0, 0, 0, 0, 0, 0, 0, 0])
        ip_address: bytes = bytes([0, 0, 0, 0])

    data_type_code_to_type = {
        DataTypeCode.configuration: Configuration
    }
