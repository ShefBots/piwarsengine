import struct
from serial import Serial
from collections import namedtuple
from time import monotonic_ns

UBYTE = "B"
SBYTE = "b"
USHORT = "H"
SSHORT = "h"
FLOAT = "f"

def format_length(fmt):
    length = 0
    for char in fmt:
        if char in 'cbB?':
            length += 1  # char, signed/unsigned char, bool
        elif char in 'hH':
            length += 2  # short, unsigned short
        elif char in 'iI':
            length += 4  # int, unsigned int
        elif char in 'lL':
            length += 4 if struct.calcsize('l') == 4 else 8  # long, unsigned long
        elif char == 'f':
            length += 4  # float
        elif char == 'd':
            length += 8  # double
        else:
            raise ValueError(f"Unsupported format character: {char}")
    return length

Command = namedtuple("Command", ("value", "length", "format"))

def make_command(value, fmt=""):
    return Command(value, format_length(fmt), fmt)

COM_POKE_SEND = make_command('P')
COM_IDENTIFY_SEND = make_command('I')
COM_IDENTIFY_RECV = make_command('I', UBYTE)


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

    def send(self, command: Command, *data):
        # Create a buffer of the correct length
        buffer = bytearray(command.length + self.FRAME_BYTES)

        # Populate the buffer with the required header values and command data
        struct.pack_into(">BB" + command.format + "B", buffer, 0,  # fmt, buffer, offset
                         self.START_BYTE,
                         ord(command.value),
                         *data,
                         0)  # where the checksum will go

        # Calculate the checksum and update the last byte of the buffer
        buffer[-1] = self.checksum(buffer)

        # Clear out the input buffer in case anything is still lingering from a previous command
        # self.__serial.reset_input_buffer()  # Removed so we can capture any tracebacks from connected Picos

        # Write out the buffer
        self.__serial.write(buffer)

    def receive(self, command: Command, timeout=DEFAULT_TIMEOUT):
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
        # print(received)
        expected_checksum = self.checksum(received)
        received_checksum = received[-1]
        if received_checksum != expected_checksum:
            print("\n--------------------------------------------------")
            print("Recv Len:", end=" ")
            print(receive_length)
            print("Recv'd:", end=" ")
            print(received)
            print(received.hex())
            print("In Buffer:", end=" ")
            read_all = self.__serial.read_all()
            print(read_all)
            print(read_all.hex())
            print("--------------------------------------------------")
            raise ValueError(f"Checksum mismatch! Expected {expected_checksum}, received {received_checksum}")

        buffer = struct.unpack(">BB" + command.format + "B", received)
        fmt_len = len(command.format)
        if fmt_len > 0:
            return buffer[2] if fmt_len == 1 else buffer[2:2 + fmt_len]
        else:
            return None

    def poke(self):
        self.send(COM_POKE_SEND)

    def identify(self, timeout=DEFAULT_TIMEOUT):
        self.send(COM_IDENTIFY_SEND)
        return self.receive(COM_IDENTIFY_RECV, timeout)
