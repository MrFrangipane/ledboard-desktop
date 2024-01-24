from ledboard.serial_.communicator import SerialCommunicator
from ledboard.serial_.protocol import SerialProtocol


if __name__ == '__main__':
    serial_communicator = SerialCommunicator(port="COM13")
    serial_communicator.connect()

    i = 1
    for i in range(150):
        serial_communicator.send(
            SerialProtocol.MessageType.illuminate,
            SerialProtocol.IlluminatedLed(led_index=i)
        )
        print(serial_communicator.receive())

        i += 1
