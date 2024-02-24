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


# Define the color ranges for each LED segment
color_segments = [
    (255//2, 0, 0),       # Red
    (255//2, 165//2, 0),  # Orange
    (255//2, 255//2, 0),  # Yellow
    (0, 255//2, 0),       # Green
    (0, 0, 255//2),       # Blue
    (75//2, 0, 130//2)    # Indigo
]

max_cm = 30  # Maximum value for cm

if io_controller is not None:
    while True:
        print("Read ToFs", end=" ")
        cm = io_controller.read_tof()
        print(cm)

        # Determine which LED segment corresponds to the input value
        segment_index = min(int(cm / ((max_cm + 1) / 6)), 5)

        # Set LEDs based on the segment index and color
        for led in range(6):
            if led <= segment_index:
                io_controller.set_led(led, *color_segments[segment_index])
            else:
                io_controller.set_led(led, 0, 0, 0)

        time.sleep(0.1)

