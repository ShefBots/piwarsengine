from comms.serial import Command, SerialComms

COM_SET_SERVO_GRAB_ANGLE = Command('G', 0)
COM_SET_SERVO_LAUNCH_ANGLE = Command('L', 0)
COM_SET_LAUNCH_SPEED = Command('S', 0)
COM_WS2812_COLOUR = Command('C', 0)
COM_RC_RECEIVER = Command('R', 0)


COM_READ_TOF_SEND = Command('T', 0)
COM_READ_TOF_RECV = Command('T', 2)


class IOController:
    NAME = "IO Controller"
    EXPECTED_ID = 0x01

    COM_SET_SERVO_GRAB_ANGLE = 'G'
    COM_SET_SERVO_LAUNCH_ANGLE = 'L'
    COM_SET_LAUNCH_SPEED = 'S'
    COM_WS2812_COLOUR = 'C'
    COM_RC_RECEIVER = 'R'

    def __init__(self, comms: SerialComms):
        self.__comms = comms

    def __del__(self):
        self.__comms.__del__()

    def poke(self):
        self.__comms.poke()

    def identify(self, timeout=SerialComms.DEFAULT_TIMEOUT):
        return self.__comms.identify(timeout)

    def read_tof(self, timeout=SerialComms.DEFAULT_TIMEOUT):
        self.__comms.send(COM_READ_TOF_SEND)
        cm = self.__comms.receive(COM_READ_TOF_RECV, "H", timeout) / 10
        return cm