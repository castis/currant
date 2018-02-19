# Flight Controller

Python flight control software.

## Built with
- [Raspberry Pi 3 B](https://www.raspberrypi.org/products/raspberry-pi-3-model-b/), running [Raspian Stretch Lite](https://www.raspberrypi.org/downloads/raspbian/), housed in a [Pibow 3 Coupé](https://shop.pimoroni.com/collections/raspberry-pi/products/pibow-coupe-for-raspberry-pi-3)
- [MPU-9250 Accelerometer/Gyroscope/Compass](https://www.amazon.com/gp/product/B01I1J0Z7Y)
- [HC-SR04 Ultrasonic Sensor](https://www.sparkfun.com/products/13959)
- (not yet implemented) [MPL3115A2 Altitude/Pressure Sensor](https://www.sparkfun.com/products/11084)
- [LDPower D-250](https://hobbyking.com/en_us/ldpower-d250-2-multicopter-power-system-2206-1900kv-6-x-3-4-pack.html) ESC/Motor set with some [JST connectors](https://www.amazon.com/gp/product/B01M5AHF0Z) for convenience
- [Turnigy 2200mAh 3S 20C Battery](https://hobbyking.com/en_us/turnigy-2200mah-3s-25c-lipo-pack.html)
- [OCDAY 3A Power Distribution Board](https://www.amazon.com/gp/product/B01IOHWHI8) to split battery power and provides a 5v line to power the Raspberry Pi

### Control
- [Xbox 360 controller](https://en.wikipedia.org/wiki/List_of_Xbox_360_accessories#Xbox_360_controllers)
- [Wireless Controller Receiver](https://en.wikipedia.org/wiki/List_of_Xbox_360_accessories#Wireless_Gaming_Receiver) with housing removed and a shortened cable
- [USB Wireless Adapter](https://www.amazon.com/Edimax-EW-7811Un-150Mbps-Raspberry-Supports/dp/B003MTTJOY) for connecting to the Pi over its own wifi network

Mounted to a [plexiglas frame](https://www.amazon.com/gp/product/B000G6SJS8) using [standoffs](https://www.amazon.com/gp/product/B01DD07PTW) and [velcro straps](https://www.amazon.com/gp/product/B01JNZ4R4W).

### Software
- [Python 3.6.4](https://docs.python.org/3/) with smbus2, psutils, and numpy
- [xboxdrv](https://github.com/xboxdrv/xboxdrv) daemon for xbox controller support
- [`hostapd` and `dnsmasq` for hosting a wifi network](https://frillip.com/using-your-raspberry-pi-3-as-a-wifi-access-point-with-hostapd/)

## Installation

### Local

Assuming `pipenv` and python 3.6 are installed.

Install the USB Wireless Adapter on your local machine, then

    git clone git@github.com:castis/flightcontroller.git
    cd flightcontroller

Run `pipenv --python 3.6` followed by `pipenv install`, enabling the `ansible` and `fab` commands.

For easy network access, put this in `~/.ssh/config`

    Host havok
        User root
        IdentityFile ~/.ssh/id_rsa

and

    192.168.10.1    havok

in `/etc/hosts` so `ssh havok` works.

Copy `~/.ssh/id_rsa.pub` to your clipboard.

### On the Pi

Assuming a fresh install of [Raspian Stretch Lite](https://www.raspberrypi.org/downloads/raspbian/):

- boot up and log in with username `pi` and password `raspberry`
- run `raspi-config`;
  - expand the filesystem
  - turn on ssh
  - enable I2C

Drop the public key stored in your clipboard into `~/.ssh/authorized_keys` (remember to `chmod 700` the directory and `chmod 600` the file if you just created them!)

#### Automated configuration

From your local machine, `cd ansible/` and run the following (both will take a few minutes)

- `ansible-playbook python3.6.yml` will install python 3.6.4 (takes a while, compiles python from source)
- `ansible-playbook setup.yml` will:
  - set the hostname
  - remove the default `pi` user
  - erase the contents of `/etc/motd`
  - install the python libraries for the flight controller
  - install and configure xboxdrv
  - install and configure dnsmasq and hostapd (using [this guide](https://frillip.com/using-your-raspberry-pi-3-as-a-wifi-access-point-with-hostapd/) as a starting point)
  - install pipenv

Using the USB wireless adapter, you should now be able to connect to the Pi through its own wifi network.

## Development

`pipenv run python sync.py` will watch `code/*` for changes and sync `code/` to `/opt/flightcontroller` on the Pi.

To run the program, log in, fire up a pipenv shell, and run it.

    ssh havok -t "cd /opt/flightcontroller; pipenv shell; bash --login"
    python main.py

`.itermocil` is the [itermocil](https://github.com/TomAnthony/itermocil) file I use for development, makes things a little easier.
