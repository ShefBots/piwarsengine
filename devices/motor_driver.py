from comms.serial import make_command, SerialComms, SSHORT

COM_SET_FORWARD_VELOCITY = make_command('#', SSHORT)
COM_SET_RIGHT_VELOCITY = make_command('&', SSHORT)
COM_SET_LINEAR_VELOCITIES = make_command('$', SSHORT * 2)
COM_SET_ANGULAR_VELOCITY = make_command('^', SSHORT)
COM_SET_ALL_VELOCITIES = make_command('+', SSHORT * 3)
COM_STOP_MOVING = make_command('!')

COM_SET_MOTION_ORIGIN_TO = make_command('@')
COM_RESET_MOTION_ORIGIN = make_command('~')

COM_POKE = make_command('P')
COM_READ_VELOCITIES_SEND = make_command('V')
COM_READ_VELOCITIES_RECV = make_command('V', SSHORT * 3)
COM_READ_ENCODERS_SEND = make_command('?')
COM_READ_ENCODERS_RECV = make_command('?', SSHORT * 4)


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
        self.__comms.send(COM_SET_FORWARD_VELOCITY,
                          int(metres_per_second * self.METRES_SCALING))

    def set_right_velocity(self, metres_per_second):
        self.__comms.send(COM_SET_RIGHT_VELOCITY,
                          int(metres_per_second * self.METRES_SCALING))

    def set_linear_velocities(self, metres_per_second_forward, metres_per_second_right):
        self.__comms.send(COM_SET_LINEAR_VELOCITIES,
                          int(metres_per_second_forward * self.METRES_SCALING),
                          int(metres_per_second_right * self.METRES_SCALING))

    def set_angular_velocity(self, degrees_per_second):
        self.__comms.send(COM_SET_ANGULAR_VELOCITY,
                          int(degrees_per_second * self.DEGREES_SCALING))

    def set_all_velocities(self, metres_per_second_forward, metres_per_second_right, degrees_per_second):
        self.__comms.send(COM_SET_ALL_VELOCITIES,
                          int(metres_per_second_forward * self.METRES_SCALING),
                          int(metres_per_second_right * self.METRES_SCALING),
                          int(degrees_per_second * self.DEGREES_SCALING))

    def stop_moving(self):
        self.__comms.send(COM_STOP_MOVING)

    def set_motion_origin_to(self, right, forward):
        self.__comms.send(COM_SET_MOTION_ORIGIN_TO,
                          int(right * self.METRES_SCALING),
                          int(forward * self.METRES_SCALING))

    def reset_motion_origin(self):
        self.__comms.send(COM_RESET_MOTION_ORIGIN)

    def poke(self):
        self.__comms.poke()

    def identify(self, timeout=SerialComms.DEFAULT_TIMEOUT):
        return self.__comms.identify(timeout)

    def read_velocities(self, timeout=SerialComms.DEFAULT_TIMEOUT):
        self.__comms.send(COM_READ_VELOCITIES_SEND)
        z, x, r = self.__comms.receive(COM_READ_VELOCITIES_RECV, timeout)
        return z / self.METRES_SCALING, x / self.METRES_SCALING, r / self.DEGREES_SCALING

    def read_encoders(self, timeout=SerialComms.DEFAULT_TIMEOUT):
        self.__comms.send(COM_READ_ENCODERS_SEND)
        a, b, c, d = self.__comms.receive(COM_READ_ENCODERS_RECV, timeout)
        return a / self.ENCODER_SCALING, b / self.ENCODER_SCALING, c / self.ENCODER_SCALING, d / self.ENCODER_SCALING
