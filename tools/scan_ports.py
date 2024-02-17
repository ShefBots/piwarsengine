import time
from serial import Serial, SerialException
from glob import glob

# Remember to add piwarsengine to the PYTHONPATH for the below imports to work
from comms.serial import SerialComms
from devices import MotorDriver, IOController, DEVICE_ID_LIST

# The path wildcard pattern to search
PATTERN = '/dev/ttyACM*'

motor_driver = None
io_controller = None


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

    if IOController.EXPECTED_ID in instances.keys():
        io_controller = IOController(instances[IOController.EXPECTED_ID])

while True:
    if motor_driver is not None:
        print("Motor Driver", end=" ")
        motor_driver.identify()

    if io_controller is not None:
        print("IO Controller", end=" ")
        io_controller.identify()
    time.sleep(0.5)
