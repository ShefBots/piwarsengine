from comms.serial import Command, SerialComms

COM_SET_FORWARD_VELOCITY = Command('#', 2)
COM_SET_RIGHT_VELOCITY = Command('&', 2)
COM_SET_LINEAR_VELOCITIES = Command('$', 4)
COM_SET_ANGULAR_VELOCITY = Command('^', 2)
COM_SET_ALL_VELOCITIES = Command('+', 6)
COM_STOP_MOVING = Command('!', 0)

COM_SET_MOTION_ORIGIN_TO = Command('@', 0)
COM_RESET_MOTION_ORIGIN = Command('~', 0)

COM_READ_VELOCITIES_SEND = Command('V', 0)
COM_READ_VELOCITIES_RECV = Command('V', 6)
COM_READ_ENCODERS_SEND = Command('?', 0)
COM_READ_ENCODERS_RECV = Command('?', 8)


class MotorDriver:
    NAME = "Motor Driver"
    EXPECTED_ID = 0x00

    METRES_SCALING = 20000
    DEGREES_SCALING = 50
    ENCODER_SCALING = 60

    def __init__(self, comms: SerialComms):
        self.__comms = comms

    def __del__(self):
        self.__comms.__del__()

    def set_forward_velocity(self, metres_per_second):
        self.__comms.send(COM_SET_FORWARD_VELOCITY, "h",
                          int(metres_per_second * self.METRES_SCALING))

    def set_right_velocity(self, metres_per_second):
        self.__comms.send(COM_SET_RIGHT_VELOCITY, "h",
                          int(metres_per_second * self.METRES_SCALING))

    def set_linear_velocities(self, metres_per_second_forward, metres_per_second_right):
        self.__comms.send(COM_SET_LINEAR_VELOCITIES, "hh",
                          int(metres_per_second_forward * self.METRES_SCALING),
                          int(metres_per_second_right * self.METRES_SCALING))

    def set_angular_velocity(self, degrees_per_second):
        self.__comms.send(COM_SET_ANGULAR_VELOCITY, "h",
                          int(degrees_per_second * self.DEGREES_SCALING))

    def set_all_velocities(self, metres_per_second_forward, metres_per_second_right, degrees_per_second):
        self.__comms.send(COM_SET_ALL_VELOCITIES, "hhh",
                          int(metres_per_second_forward * self.METRES_SCALING),
                          int(metres_per_second_right * self.METRES_SCALING),
                          int(degrees_per_second * self.DEGREES_SCALING))

    def stop_moving(self):
        self.__comms.send(COM_STOP_MOVING)

    def set_motion_origin_to(self, right, forward):
        self.__comms.send(COM_SET_MOTION_ORIGIN_TO, "hh",
                          int(right * self.METRES_SCALING),
                          int(forward * self.METRES_SCALING))

    def reset_motion_origin(self):
        self.__comms.send(COM_RESET_MOTION_ORIGIN)

    def identify(self, timeout=SerialComms.DEFAULT_TIMEOUT):
        print(f"ID is {hex(self.__comms.identify(timeout))}")

    def read_velocities(self, timeout=SerialComms.DEFAULT_TIMEOUT):
        self.__comms.send(COM_READ_VELOCITIES_SEND)
        z, x, r, _ = self.__comms.receive(COM_READ_VELOCITIES_RECV, "hhh", timeout)
        return z / self.METRES_SCALING, x / self.METRES_SCALING, r / self.DEGREES_SCALING

    def read_encoders(self, timeout=SerialComms.DEFAULT_TIMEOUT):
        self.__comms.send(COM_READ_ENCODERS_SEND)
        a, b, c, d, _ = self.__comms.receive(COM_READ_ENCODERS_RECV, "hhhh", timeout)
        return a / self.ENCODER_SCALING, b / self.ENCODER_SCALING, c / self.ENCODER_SCALING, d / self.ENCODER_SCALING
