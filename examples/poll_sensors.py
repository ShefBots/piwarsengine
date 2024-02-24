import time
from serial import SerialException
from glob import glob
from comms.serial import SerialComms
from devices import IOController, DEVICE_ID_LIST

# The path wildcard pattern to search
PATTERN = '/dev/ttyACM*'

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

    if IOController.EXPECTED_ID in instances.keys():
        io_controller = IOController(instances[IOController.EXPECTED_ID])


if io_controller is not None:
    while True:
        print("Read ToFs", end=" ")
        print(io_controller.read_tof())
        time.sleep(0.5)

