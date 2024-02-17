# Remember to add piwarsengine to the PYTHONPATH for the below imports to work
from comms.sbus import SBusReceiver, analog_decoder, binary_decoder, analog_biased_decoder, trinary_decoder

PORT = "/dev/serial0"
CHANNELS = 8
TIMEOUT = 0.1

# Create the SBusReceiver class to receive data from our controller
controller = SBusReceiver(PORT, CHANNELS, TIMEOUT)

# Assign decoder functions to each of the channels
controller.assign_channel_decoder(0, analog_decoder)
controller.assign_channel_decoder(1, analog_decoder)
controller.assign_channel_decoder(2, analog_decoder)
controller.assign_channel_decoder(3, analog_decoder)
controller.assign_channel_decoder(4, binary_decoder)
controller.assign_channel_decoder(5, analog_biased_decoder)
controller.assign_channel_decoder(6, trinary_decoder)
controller.assign_channel_decoder(7, binary_decoder)

print("Establishing Connection")

while not controller.is_connected():
    controller.check_receive()

print("Connection Established")

while controller.is_connected():
    if controller.check_receive():
        for i in range(controller.num_channels()):
            print("Ch", i + 1, "=", controller.read_channel(i), end=", ")
        print()

print("Connection Lost")
