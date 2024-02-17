import time
from serial import Serial

PORT = "/dev/serial0"
BAUD_RATE = 9600

serial = Serial(PORT, BAUD_RATE)

try:
    while True:
        data_to_send = "Hello, world!\n"

        # Send data
        serial.write(data_to_send.encode('utf-8'))
        print(f"Sent data: {data_to_send}")

        # Non-blocking receive
        while serial.in_waiting > 0:
            char_received = serial.read(1).decode('utf-8')
            print(f"{char_received}", end="")
        print()

        time.sleep(1)

except KeyboardInterrupt:
    print("Exiting program.")

finally:
    serial.close()
