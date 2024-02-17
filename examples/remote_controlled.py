from serial import SerialException
from glob import glob
from comms.serial import SerialComms
from comms.sbus import SBusReceiver, analog_decoder, analog_biased_decoder, binary_decoder
from devices import MotorDriver, DEVICE_ID_LIST

SBUS_PORT = "/dev/serial0"
SBUS_CHANNELS = 8
SBUS_TIMEOUT = 0.1

FORWARD_CHANNEL = 2
RIGHT_CHANNEL = 3
TURN_CHANNEL = 0
SPEED_CHANNEL = 5
EN_CHANNEL = 4

LIN_SCALE = 1.0
ANG_SCALE = 180.0

# The path wildcard pattern to search
PATTERN = '/dev/ttyACM*'

motor_driver = None


def find_serial_ports(pattern):
    return glob(pattern)

def create_serial_instances(port_list):
    serial_instances = {}
    for port in port_list:
        try:
            comms = SerialComms(port)
            print(f"Serial port {port} opened successfully.")
            try:
                identity = comms.identify()
                if identity in DEVICE_ID_LIST:
                    print(f"Found device: {hex(identity)} ({DEVICE_ID_LIST[identity]})")
                else:
                    print(f"Found unknown device: {hex(identity)}")
                serial_instances[identity] = comms
            except ValueError:
                print("Not a recognised device")

        except SerialException as e:
            print(f"Error opening serial port {port}: {e}")
    return serial_instances


# Find serial ports matching the pattern
port_list = find_serial_ports(PATTERN)

if not port_list:
    print(f"No serial ports found matching the pattern '{PATTERN}'.")
else:
    # Create instances for each serial port
    instances = create_serial_instances(port_list)

    if MotorDriver.EXPECTED_ID in instances.keys():
        motor_driver = MotorDriver(instances[MotorDriver.EXPECTED_ID])


if motor_driver is not None:
    controller = SBusReceiver(SBUS_PORT, SBUS_CHANNELS, SBUS_TIMEOUT)

    controller.assign_channel_decoder(FORWARD_CHANNEL, analog_decoder)  # Forward/Backward
    controller.assign_channel_decoder(RIGHT_CHANNEL, analog_decoder)  # Right/Left
    controller.assign_channel_decoder(TURN_CHANNEL, analog_decoder)
    controller.assign_channel_decoder(EN_CHANNEL, binary_decoder)
    controller.assign_channel_decoder(SPEED_CHANNEL, analog_biased_decoder)

    print("Establishing Connection")

    while not controller.is_connected():
        controller.check_receive()

    print("Connection Established")

    while controller.is_connected():
        if controller.check_receive():
            enable = not controller.read_channel(EN_CHANNEL)
            if enable:
                max_speed = controller.read_channel(SPEED_CHANNEL)
                forward_vel = controller.read_channel(FORWARD_CHANNEL) * LIN_SCALE * max_speed
                right_vel = controller.read_channel(RIGHT_CHANNEL) * LIN_SCALE * max_speed
                turn_vel = controller.read_channel(TURN_CHANNEL) * ANG_SCALE * max_speed
                motor_driver.set_all_velocities(forward_vel, right_vel, turn_vel)
            else:
                motor_driver.stop_moving()

        print("Read Velocities and Encoders", end=" ")
        print(motor_driver.read_velocities(), motor_driver.read_encoders())

    print("Connection Lost")
