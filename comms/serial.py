import struct
from serial import Serial
from collections import namedtuple
from time import monotonic_ns

Command = namedtuple("Command", ("value", "length"))
COM_IDENTIFY_SEND = Command('I', 0)
COM_IDENTIFY_RECV = Command('I', 1)


class SerialComms:
    START_BYTE = 13
    FRAME_BYTES = 3

    WAITING = 0
    COMMAND_NEXT = 1
    DATA_NEXT = 2
    CHECKSUM = 3

    DEFAULT_TIMEOUT = 1

    def __init__(self, serial_port='/dev/ttyACM0'):
        self.__serial = Serial(serial_port, timeout=1)
        self.state = self.WAITING

    def __del__(self):
        self.__serial.close()

    """
    # This is no longer needed for our use-case as Pi will always initiate the communication
    def check_receive(self):
        current_command = None
        data = []
        bytes_received = 0
        checksum_expected = 0
        while self.__serial.in_waiting > 0:
            s = self.__serial.read(1)  # Read one byte, although it comes in as a list of one byte
            print(chr(s[0]), end="")
            if not s:  # No data left, quit loop
                # TODO possible problem - timeout of 1s?
                return

            if self.state == self.WAITING:  # Finished processing last command
                if s[0] == self.START_BYTE:  # Start byte received
                    self.state = self.COMMAND_NEXT

            elif self.state == self.COMMAND_NEXT:
                current_command = None
                data = []
                bytes_received = 0
                checksum_expected = 13
                if chr(s[0]) in self.COMMANDS.keys():  # If command matters
                    current_command = chr(s[0])
                    # print(f"Command {current_command}")
                    checksum_expected = (checksum_expected + s[0]) % 256  # Calculate checksum on the go
                    if self.COMMANDS[current_command]['bytes'] > 0:  # If there's data to look at
                        self.state = self.DATA_NEXT
                    else:
                        self.state = self.CHECKSUM

            elif self.state == self.DATA_NEXT:
                data.append(s[0])  # Shove that data in a list
                bytes_received += 1
                checksum_expected = (checksum_expected + s[0]) % 256
                if bytes_received == self.COMMANDS[current_command]['bytes']:  # Finished receiving data
                    self.state = self.CHECKSUM

            elif self.state == self.CHECKSUM:
                if s[0] == checksum_expected:  # Check that checksum
                    if self.COMMANDS[current_command]['bytes'] > 0:  # If you need to do something with the data
                        self.COMMANDS[current_command]['command'](data)  # Call the referenced command
                    else:
                        self.COMMANDS[current_command]['command']()
                else:
                    print("Checksum failed!")
                self.state = self.WAITING  # Go back to looking for a command
    """
    def checksum(self, buffer):
        checksum = 0
        for i in range(len(buffer) - 1):
            checksum += buffer[i]
        return checksum % 0x100

    def send(self, command: Command, fmt="", *data):
        # Create a buffer of the correct length
        buffer = bytearray(command.length + self.FRAME_BYTES)

        # Populate the buffer with the required header values and command data
        struct.pack_into(">BB" + fmt + "B", buffer, 0,  # fmt, buffer, offset
                         self.START_BYTE,
                         ord(command.value),
                         *data,
                         0)  # where the checksum will go

        # Calculate the checksum and update the last byte of the buffer
        buffer[-1] = self.checksum(buffer)

        # Clear out the input buffer in case anything is still lingering from a previous command
        self.__serial.reset_input_buffer()

        # Write out the buffer
        self.__serial.write(buffer)

    def receive(self, command: Command, fmt="", timeout=DEFAULT_TIMEOUT):
        # Calculate how long to wait for data
        ms = int(1000.0 * timeout + 0.5)
        end_ms = (monotonic_ns() // 1000000) + ms

        # Wait for data of the expected size to be received
        receive_length = command.length + self.FRAME_BYTES
        while self.__serial.in_waiting < receive_length:
            remaining_ms = end_ms - (monotonic_ns() // 1000000)

            # Has the timeout been reached?
            if remaining_ms <= 0:
                raise TimeoutError("Serial did not reply within the expected time")

        received = self.__serial.read(receive_length)  # Read the expected number of bytes

        expected_checksum = self.checksum(received)
        received_checksum = received[-1]
        if received_checksum != expected_checksum:
            raise ValueError(f"Checksum mismatch! Expected {expected_checksum}, received {received_checksum}")

        buffer = struct.unpack(">BB" + fmt + "B", received)
        if len(fmt) > 0:
            data = buffer[2:2 + command.length]
            if len(fmt) == 1:
                data = data[0]
            return data
        else:
            return None

    def identify(self, timeout=DEFAULT_TIMEOUT):
        self.send(COM_IDENTIFY_SEND)
        return self.receive(COM_IDENTIFY_RECV, "B", timeout)
