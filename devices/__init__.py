from .motor_driver import MotorDriver
from .io_controller import IOController

DEVICE_ID_LIST = {
    MotorDriver.EXPECTED_ID: MotorDriver.NAME,
    IOController.EXPECTED_ID: IOController.NAME
}
