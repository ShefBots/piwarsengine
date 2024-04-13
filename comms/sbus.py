import struct
from serial import Serial
from time import monotonic_ns


class SBusReceiver():
    BAUD_RATE = 115200
    FRAME_START = 0x20
    FRAME_LENGTH = 32
    MAX_CHANNELS = 14
    DEFAULT_COMMS_TIMEOUT = 1.0

    def __init__(self, serial_port, num_channels, no_comms_timeout=DEFAULT_COMMS_TIMEOUT):
        self.__serial = Serial(serial_port, self.BAUD_RATE, timeout=1)
        self.__no_comms_timeout_ms = int(no_comms_timeout * 1000)
        self.__last_received_ms = 0
        self.__timeout_reached = True       # Set as true initially so the timeout callback does not get called immediately

        self.__receiving = False
        self.__rx_buffer = bytearray(self.FRAME_LENGTH)
        self.__rx_index = 0

        if num_channels < 1 or num_channels > self.MAX_CHANNELS:
            raise ValueError(f"num_channels out of range. Expected 1 to {self.MAX_CHANNELS}")

        self.__num_channels = num_channels
        self.__channel_format = "<" + "H" * self.__num_channels
        self.__channel_decoders = [None] * self.__num_channels
        self.__channel_data = [0] * self.__num_channels

        # Clear the receive buffer
        while self.__serial.in_waiting > 0:
            self.__serial.read()

    def is_connected(self):
        return not self.__timeout_reached

    def num_channels(self):
        return self.__num_channels

    def read_channel(self, channel):
        if channel < 0 or channel >= self.__num_channels:
            raise ValueError(f"channel out of range. Expected 0 to {self.__num_channels - 1}")

        data = self.__channel_data[channel]
        if self.__channel_decoders[channel] is not None:
            data = self.__channel_decoders[channel](data)

        return data

    def assign_channel_decoder(self, channel, decoder_func):
        if channel < 0 or channel >= self.__num_channels:
            raise ValueError(f"channel out of range. Expected 0 to {self.__num_channels - 1}")

        self.__channel_decoders[channel] = decoder_func

    def check_receive(self, debug=False):
        newly_received = False

        while self.__serial.in_waiting > 0:
            rx_byte = self.__serial.read(1)[0]

            # If we're not receiving, check if the byte signifies the start of the frame, and switch to receiving
            if not self.__receiving and rx_byte == self.FRAME_START:
                self.__receiving = True
                self.__rx_index = 0

            if self.__receiving:
                self.__rx_buffer[self.__rx_index] = rx_byte
                self.__rx_index += 1

                # Have enough bytes been received?
                if self.__rx_index >= self.FRAME_LENGTH:
                    if debug:
                        print(self.__rx_buffer)

                    # Extract the checksum value sent with the data
                    received_checksum = (self.__rx_buffer[self.FRAME_LENGTH - 1] << 8) | self.__rx_buffer[self.FRAME_LENGTH - 2]

                    # Calculate a checksum value from the received data
                    checksum = 0xffff
                    for i in range(self.FRAME_LENGTH - 2):
                        checksum -= self.__rx_buffer[i]

                    if checksum == received_checksum:
                        if debug:
                            if self.__timeout_reached:
                                print("Comms established!")

                            print("Checksum OK!", end=" ")

                        self.__channel_data = struct.unpack_from(self.__channel_format, self.__rx_buffer, 2)
                        newly_received = True
                    else:
                        if debug:
                            print("Checksum Error")

                    self.__last_received_ms = monotonic_ns() // 1000000
                    self.__timeout_reached = False

                    self.__receiving = False

        current_millis = monotonic_ns() // 1000000
        if ((current_millis - self.__last_received_ms) > self.__no_comms_timeout_ms) and not self.__timeout_reached:
            if debug:
                print("Comms lost!")

            self.__timeout_reached = True

        return newly_received


def analog_decoder(value):
    return (value - 1500) / 500


def analog_biased_decoder(value):
    return (value - 1000) / 1000


def binary_decoder(value):
    return 1 if value > 1500 else 0


def trinary_decoder(value):
    return 1 if value > 1750 else -1 if value < 1250 else 0


if __name__ == "__main__":
    serial_port = "/dev/serial0"  # Replace with the actual serial port
    baud_rate = 115200

    uart = Serial(serial_port, baud_rate)

    controller = SBusReceiver(serial_port, 8, 0.1)
    controller.assign_channel_decoder(0, analog_decoder)  # 1: Right Left/Right
    controller.assign_channel_decoder(1, analog_decoder)  # 2: Right Up/Down
    controller.assign_channel_decoder(2, analog_decoder)  # 3: Left Up/Down
    controller.assign_channel_decoder(3, analog_decoder)  # 4: Left Left/Right
    controller.assign_channel_decoder(4, binary_decoder)  # 5: SwA
    controller.assign_channel_decoder(5, analog_biased_decoder)  #: 6 VrA
    controller.assign_channel_decoder(6, analog_biased_decoder)  #: 7 VrB
    controller.assign_channel_decoder(7, binary_decoder)  #: 8 SwD

    print("Establishing Connection")

    while not controller.is_connected():
        controller.check_receive()

    print("Connection Established")

    while controller.is_connected():
        if controller.check_receive():
            for i in range(controller.num_channels()):
                print("Ch", i + 1, "=", controller.read_channel(i), end=", ")
            print()

    print("Connection Lost")
