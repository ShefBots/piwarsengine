from comms.serial import make_command, SerialComms, SSHORT, UBYTE

COM_SET_SERVO_GRAB_ANGLE = make_command('G')
COM_SET_SERVO_LAUNCH_ANGLE = make_command('L')
COM_SET_LAUNCH_SPEED = make_command('S')
COM_WS2812_COLOUR = make_command('C')
COM_RC_RECEIVER = make_command('R')


COM_READ_TOF_SEND = make_command('T', UBYTE)
COM_READ_TOF_RECV = make_command('T', SSHORT)

COM_SET_LED_SEND = make_command('L', UBYTE * 4)


class IOController:
    NAME = "IO Controller"
    EXPECTED_ID = 0x01

    TOF_SCALING = 10.0

    def __init__(self, comms: SerialComms):
        self.__comms = comms

    def __del__(self):
        self.__comms.__del__()

    def poke(self):
        self.__comms.poke()

    def identify(self, timeout=SerialComms.DEFAULT_TIMEOUT):
        return self.__comms.identify(timeout)

    def read_tof(self, index=0, timeout=SerialComms.DEFAULT_TIMEOUT):
        self.__comms.send(COM_READ_TOF_SEND, index)

        # Catch an infrequent checksum error that occurs
        try:
            return self.__comms.receive(COM_READ_TOF_RECV, timeout) / self.TOF_SCALING
        except ValueError as e:
            print(e)
            return -99

    def set_led(self, led, r, g, b):
        self.__comms.send(COM_SET_LED_SEND, led, r, g, b)