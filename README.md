# Flight Controller

Python flight control software.

### Built with
 - [Raspberry Pi 3 B](https://www.raspberrypi.org/products/raspberry-pi-3-model-b/) running [Raspian Stretch Lite](https://www.raspberrypi.org/downloads/raspbian/) tucked into a [pimoroni case](https://shop.pimoroni.com/collections/raspberry-pi/products/pibow-coupe-for-raspberry-pi-3)
 - [Python 3.6.4](https://docs.python.org/3/)
 - [MPU-9250 Accelerometer/Gyroscope/Compass](https://www.newegg.com/Product/Product.aspx?Item=9SIADS55SB0686)
 - [HC-SR04 Ultrasonic Sensor](https://www.sparkfun.com/products/13959)
 - [MPL3115A2 Altitude/Pressure Sensor](https://www.sparkfun.com/products/11084)

### Power
- [LDPower D-250](https://hobbyking.com/en_us/ldpower-d250-2-multicopter-power-system-2206-1900kv-6-x-3-4-pack.html) ESC/Motor set with some [JST connectors](https://www.amazon.com/gp/product/B01M5AHF0Z/ref=oh_aui_detailpage_o09_s00?ie=UTF8&psc=1) soldered on for convenience.
- [Turnigy 2200mAh 3S 20C Battery](https://hobbyking.com/en_us/turnigy-2200mah-3s-25c-lipo-pack.html)
- [OCDAY 3A Power Distribution Board](https://www.amazon.com/gp/product/B01IOHWHI8/ref=oh_aui_detailpage_o04_s00?ie=UTF8&psc=1) to split battery power and provides a 5v line to power the Raspberry Pi.

### Control
 - [Xbox 360 controller](https://en.wikipedia.org/wiki/List_of_Xbox_360_accessories#Xbox_360_controllers)
 - [Wireless Controller Receiver](https://en.wikipedia.org/wiki/List_of_Xbox_360_accessories#Wireless_Gaming_Receiver) with shortened cable.
 - [xboxdrv](https://github.com/xboxdrv/xboxdrv) for xbox controller support
 - [USB Wireless Adapter](https://www.amazon.com/Edimax-EW-7811Un-150Mbps-Raspberry-Supports/dp/B003MTTJOY)

All mounted on a cutout piece of plexiglas.

## Installation

    git clone git@github.com:castis/flightcontroller.git
    cd flightcontroller

After installing the USB Wireless Adapter, run `pipenv install` so you can `ansible`.

### On the RPi

- Flash a fresh copy of [Raspian Stretch Lite](https://www.raspberrypi.org/downloads/raspbian/) to a card
- Boot it up and log in with `pi:raspberry`, run `raspi-config`, expand the filesystem, turn on ssh, and enable I2C.
- Drop an ssh key into `/root/.ssh/authorized_keys` on the Pi,

and put

    Host havok
        User root
        IdentityFile ~/.ssh/id_rsa

into the local `~/.ssh/config` so `ssh havok` works.

#### Automated configuration

Jump into `ansible/` and run the following (both will take a few minutes)
- `ansible-playbook python3.6.yml` will install python 3.6.4
- `ansible-playbook setup.yml` will configure the controller daemon, wireless network, and some python libraries.

Using the USB wireless adapter, connect to the new network, make sure you can ssh into havok, then store that IP address in local `/etc/hosts`.

## Development

`pipenv run python sync.py` will watch `code/*` for changes and sync `code/` to `/opt/flightcontroller` on the Pi.

To run the program, log in, fire up a pipenv shell, and run it.

    ssh havok -t "cd /opt/flightcontroller; pipenv shell; bash --login"
    python main.py
