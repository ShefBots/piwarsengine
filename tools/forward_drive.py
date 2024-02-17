import time
import serial
from glob import glob
from comms.serial import SerialComms
from devices import MotorDriver, DEVICE_ID_LIST

# The path wildcard pattern to search
PATTERN = '/dev/ttyACM*'

motor_driver = None


def find_serial_ports(pattern='/dev/ttyACM*'):
    return glob(pattern)

def create_serial_instances(port_list):
    serial_instances = {}
    for port in port_list:
        try:
            ser = SerialComms(port)
            print(f"Serial port {port} opened successfully.")
            try:
                identity = ser.identify()
                if identity in DEVICE_ID_LIST:
                    print(f"Found device: {hex(identity)} ({DEVICE_ID_LIST[identity]})")
                else:
                    print(f"Found unknown device: {hex(identity)}")
                serial_instances[identity] = ser
            except ValueError:
                print("Not a recognised device")

        except serial.SerialException as e:
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
    while True:
        print("Read Velocities and Encoders", end=" ")
        motor_driver.set_forward_velocity(0.1)
        print(motor_driver.read_velocities(), motor_driver.read_encoders())

        time.sleep(0.1)
