from comms.serial import make_command, SerialComms, SSHORT, UBYTE, USHORT


COM_READ_TOF_SEND = make_command('T', UBYTE)
COM_READ_TOF_RECV = make_command('T', SSHORT)

COM_SET_LED_SEND = make_command('L', UBYTE * 4)

COM_SET_GRIPPER_SEND = make_command('G', UBYTE)
COM_READ_GRIPPER_SEND = make_command('g')
COM_READ_GRIPPER_RECV = make_command('g', UBYTE)

COM_READ_BARREL_SEND = make_command('B')
COM_READ_BARREL_RECV = make_command('B', UBYTE)

COM_POWER_TURRET_SEND = make_command('W', UBYTE)
COM_SET_TURRET_TILT_SEND = make_command('E', USHORT)
COM_SET_TURRET_SPEED_SEND = make_command('S', USHORT)
COM_FIRE_TURRET_SEND = make_command('F')

GRIPPER_CLOSED = 0
GRIPPER_OPEN = 1
GRIPPER_UNKNOWN = 2
GRIPPER_CLOSING = 3
GRIPPER_OPENING = 4

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

    def open_gripper(self):
        # could also check here if it was in the process of opening so
        # as not to send open twice
        if self.gripper_state() == GRIPPER_OPEN:
            return
        self.__comms.send(COM_SET_GRIPPER_SEND, GRIPPER_OPEN)

    def close_gripper(self):
        # same again but could check if it was already closing
        if self.gripper_state() == GRIPPER_CLOSED:
            return
        self.__comms.send(COM_SET_GRIPPER_SEND, GRIPPER_CLOSED)

    def gripper_state(self):
        self.__comms.send(COM_READ_GRIPPER_SEND)

        # Catch an infrequent checksum error that occurs
        try:
            return self.__comms.receive(COM_READ_GRIPPER_RECV)
        except ValueError as e:
            print(e)
            return GRIPPER_UNKNOWN

    def barrel_state(self):
        self.__comms.send(COM_READ_BARREL_SEND)

        # Catch an infrequent checksum error that occurs
        try:
            return self.__comms.receive(COM_READ_BARREL_RECV)
        except ValueError as e:
            print(e)
            return 0

    def power_turret(self, state=0):
        self.__comms.send(COM_POWER_TURRET_SEND, state)

    def turret_tilt(self, angle=0):
        self.__comms.send(COM_SET_TURRET_TILT_SEND, angle)

    def turret_speed(self, speed=0):
        self.__comms.send(COM_SET_TURRET_SPEED_SEND, speed)

    def fire(self):
        # could potentially add a timeout on calling this?
        return self.__comms.send(COM_FIRE_TURRET_SEND)

    def set_led(self, led, r, g, b):
        self.__comms.send(COM_SET_LED_SEND, led, r, g, b)
