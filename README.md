# flightcontroller

`./sync.py` is a local watch script to send `/code` to the RPi.

### Xbox Controller Support

#### Install I2C communications libraries
    sudo apt-get install python-smbus
    sudo apt-get install i2c-tools
    sudo modprobe i2c-bcm2708
    sudo modprobe i2c-dev

#### Install the XBox controller driver
    sudo apt-get install xboxdrv

#### Prove that it works... (wiggle the controller sticks)
    sudo xboxdrv --wid 0 -l 2 --dpad-as-button --deadzone 12000


https://www.devdungeon.com/content/creating-systemd-service-files
