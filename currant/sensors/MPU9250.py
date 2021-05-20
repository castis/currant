# coding: utf-8
# @package MPU9250
#  This is a FaBo9Axis_MPU9250 library for the FaBo 9AXIS I2C Brick.
#
#  http://fabo.io/202.html
#
#  Released under APACHE LICENSE, VERSION 2.0
#
#  http://www.apache.org/licenses/
#
#  FaBo <info@fabo.io>


import time

from smbus2 import SMBus

# MPU9250 Default I2C slave address
SLAVE_ADDRESS = 0x68

# AK8963 I2C slave address
AK8963_SLAVE_ADDRESS = 0x0C
DEVICE_ID = 0x71

# MPU-9250 Register Addresses
# sample rate driver
SMPLRT_DIV = 0x19
CONFIG = 0x1A
GYRO_CONFIG = 0x1B
ACCEL_CONFIG = 0x1C
ACCEL_CONFIG_2 = 0x1D
LP_ACCEL_ODR = 0x1E
WOM_THR = 0x1F
FIFO_EN = 0x23
I2C_MST_CTRL = 0x24
I2C_MST_STATUS = 0x36
INT_PIN_CFG = 0x37
INT_ENABLE = 0x38
INT_STATUS = 0x3A
ACCEL_OUT = 0x3B
TEMP_OUT = 0x41
GYRO_OUT = 0x43

I2C_MST_DELAY_CTRL = 0x67
SIGNAL_PATH_RESET = 0x68
MOT_DETECT_CTRL = 0x69
USER_CTRL = 0x6A
PWR_MGMT_1 = 0x6B
PWR_MGMT_2 = 0x6C
FIFO_R_W = 0x74
WHO_AM_I = 0x75

# Gyro Full Scale Select
GFS_250 = 0x00
GFS_500 = 0x01
GFS_1000 = 0x02
GFS_2000 = 0x03

# Accel Full Scale Select
AFS_2G = 0x00
AFS_4G = 0x01
AFS_8G = 0x02
AFS_16G = 0x03

# AK8963 Register Addresses
AK8963_ST1 = 0x02
AK8963_MAGNET_OUT = 0x03
AK8963_CNTL1 = 0x0A
AK8963_CNTL2 = 0x0B
AK8963_ASAX = 0x10

# CNTL1 Mode select
AK8963_MODE_DOWN = 0x00  # power down mode
AK8963_MODE_ONE = 0x01  # one shot data output

# Continous data output 8Hz
AK8963_MODE_C8HZ = 0x02

# Continous data output 100Hz
AK8963_MODE_C100HZ = 0x06

# Magneto Scale Select
AK8963_BIT_14 = 0x00  # 14bit
AK8963_BIT_16 = 0x01  # 16bit

bus = SMBus(1)

# MPU9250 I2C Control class

# Data Convert
# @param [in] self The object pointer.
# @param [in] data1 LSB
# @param [in] data2 MSB
# @retval Value MSB+LSB(int 16bit)
def dataConv(data1, data2):
    value = data1 | (data2 << 8)
    if value & (1 << 16 - 1):
        value -= 1 << 16
    return value


class MPU9250:

    # Constructor
    #  @param [in] address MPU-9250 I2C slave address default:0x68
    def __init__(self, address=SLAVE_ADDRESS):
        self.address = address
        self.configMPU9250(GFS_500, AFS_2G)
        self.configAK8963(AK8963_MODE_C8HZ, AK8963_BIT_16)

    # Search Device
    #  @retval true device connected
    #  @retval false device error
    def searchDevice(self):
        return bus.read_byte_data(self.address, WHO_AM_I) == DEVICE_ID

    # Configure MPU-9250
    #  @param [in] gfs Gyro Full Scale Select(default:GFS_250[+250dps])
    #  @param [in] afs Accel Full Scale Select(default:AFS_2G[2g])
    def configMPU9250(self, gfs, afs):
        if gfs == GFS_250:
            self.gres = 250.0 / 32768.0
        elif gfs == GFS_500:
            self.gres = 500.0 / 32768.0
        elif gfs == GFS_1000:
            self.gres = 1000.0 / 32768.0
        else:  # gfs == GFS_2000
            self.gres = 2000.0 / 32768.0

        if afs == AFS_2G:
            self.ares = 2.0 / 32768.0
        elif afs == AFS_4G:
            self.ares = 4.0 / 32768.0
        elif afs == AFS_8G:
            self.ares = 8.0 / 32768.0
        else:  # afs == AFS_16G:
            self.ares = 16.0 / 32768.0

        # sleep off
        bus.write_byte_data(self.address, PWR_MGMT_1, 0x00)
        time.sleep(0.1)

        # auto select clock source
        bus.write_byte_data(self.address, PWR_MGMT_1, 0x01)
        time.sleep(0.1)

        # DLPF_CFG
        bus.write_byte_data(self.address, CONFIG, 0x03)

        # sample rate divider
        bus.write_byte_data(self.address, SMPLRT_DIV, 0x04)

        # gyro full scale select
        bus.write_byte_data(self.address, GYRO_CONFIG, gfs << 3)

        # accel full scale select
        bus.write_byte_data(self.address, ACCEL_CONFIG, afs << 3)

        # A_DLPFCFG
        bus.write_byte_data(self.address, ACCEL_CONFIG_2, 0x03)

        # BYPASS_EN
        bus.write_byte_data(self.address, INT_PIN_CFG, 0x02)
        time.sleep(0.1)

    # Configure AK8963
    #  @param [in] mode Magneto Mode Select(default:AK8963_MODE_C8HZ[Continous 8Hz])
    #  @param [in] mfs Magneto Scale Select(default:AK8963_BIT_16[16bit])
    def configAK8963(self, mode, mfs):
        if mfs == AK8963_BIT_14:
            self.mres = 4912.0 / 8190.0
        else:  # mfs == AK8963_BIT_16:
            self.mres = 4912.0 / 32760.0

        bus.write_byte_data(AK8963_SLAVE_ADDRESS, AK8963_CNTL1, 0x00)
        time.sleep(0.01)

        # set read FuseROM mode
        bus.write_byte_data(AK8963_SLAVE_ADDRESS, AK8963_CNTL1, 0x0F)
        time.sleep(0.01)

        # read coef data
        data = bus.read_i2c_block_data(AK8963_SLAVE_ADDRESS, AK8963_ASAX, 3)

        self.magXcoef = (data[0] - 128) / 256.0 + 1.0
        self.magYcoef = (data[1] - 128) / 256.0 + 1.0
        self.magZcoef = (data[2] - 128) / 256.0 + 1.0

        # set power down mode
        bus.write_byte_data(AK8963_SLAVE_ADDRESS, AK8963_CNTL1, 0x00)
        time.sleep(0.01)

        # set scale&continous mode
        bus.write_byte_data(AK8963_SLAVE_ADDRESS, AK8963_CNTL1, (mfs << 4 | mode))
        time.sleep(0.01)

    # brief Check data ready
    #  @retval True data is ready
    #  @retval False data is not ready
    def checkDataReady(self):
        return bus.read_byte_data(self.address, INT_STATUS) & 0x01

    # Read accelerometer
    #  @retval x : x-axis data
    #  @retval y : y-axis data
    #  @retval z : z-axis data
    def readAccel(self):
        data = bus.read_i2c_block_data(self.address, ACCEL_OUT, 6)
        return {
            "x": round(dataConv(data[1], data[0]) * self.ares, 3),
            "y": round(dataConv(data[3], data[2]) * self.ares, 3),
            "z": round(dataConv(data[5], data[4]) * self.ares, 3),
        }

    # Read gyro
    #  @retval x : x-gyro data
    #  @retval y : y-gyro data
    #  @retval z : z-gyro data
    def readGyro(self):
        data = bus.read_i2c_block_data(self.address, GYRO_OUT, 6)
        return {
            "x": round(dataConv(data[1], data[0]) * self.gres, 3),
            "y": round(dataConv(data[3], data[2]) * self.gres, 3),
            "z": round(dataConv(data[5], data[4]) * self.gres, 3),
        }

    # Read magneto
    #  @retval x : X-magneto data
    #  @retval y : y-magneto data
    #  @retval z : Z-magneto data
    def readMagnet(self):

        # check data ready
        drdy = bus.read_byte_data(AK8963_SLAVE_ADDRESS, AK8963_ST1)
        if drdy & 0x01:
            data = bus.read_i2c_block_data(AK8963_SLAVE_ADDRESS, AK8963_MAGNET_OUT, 7)

            # check overflow
            if (data[6] & 0x08) != 0x08:
                x = dataConv(data[0], data[1])
                y = dataConv(data[2], data[3])
                z = dataConv(data[4], data[5])

                return {
                    "x": round(x * self.mres * self.magXcoef, 3),
                    "y": round(y * self.mres * self.magYcoef, 3),
                    "z": round(z * self.mres * self.magZcoef, 3),
                }

    # Read temperature
    #  @param [out] temperature temperature(degrees C)
    def readTemperature(self):
        data = bus.read_i2c_block_data(self.address, TEMP_OUT, 2)
        temp = dataConv(data[1], data[0])

        return round((temp / 333.87 + 21.0), 3)
