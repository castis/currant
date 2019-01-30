# Flight Controller

<img src="https://raw.githubusercontent.com/castis/flightcontroller/master/image.jpg">

## Hardware

- [Raspberry Pi 3 B](https://www.raspberrypi.org/products/raspberry-pi-3-model-b/), running [Raspian Stretch Lite](https://www.raspberrypi.org/downloads/raspbian/), housed in a [Pibow 3 Coupé](https://shop.pimoroni.com/products/pibow-coupe-for-raspberry-pi-3-b-plus)
- [MPU-9250 Accelerometer/Gyroscope/Compass](https://www.amazon.com/gp/product/B01I1J0Z7Y)
- [HC-SR04 Ultrasonic Sensor](https://www.sparkfun.com/products/13959)
- (not yet implemented) [MPL3115A2 Altitude/Pressure Sensor](https://www.sparkfun.com/products/11084)
- [LDPower D-250 ESC/Motor set](https://hobbyking.com/en_us/ldpower-d250-2-multicopter-power-system-2206-1900kv-6-x-3-4-pack.html) with [JST connectors](https://www.amazon.com/gp/product/B01M5AHF0Z) for convenience
- [Turnigy 2200mAh 3S 20C Battery](https://hobbyking.com/en_us/turnigy-2200mah-3s-25c-lipo-pack.html)
- [OCDAY 3A Power Distribution Board](https://www.amazon.com/gp/product/B01IOHWHI8) with bonus 5v output
- [8BitDo SN30 Pro](http://www.8bitdo.com/sn30-pro-g-classic-or-sn30-pro-sn/)
- [USB Wireless Adapter](https://www.amazon.com/Edimax-EW-7811Un-150Mbps-Raspberry-Supports/dp/B003MTTJOY) for connecting to the Pi over its own wifi network
- All mounted to a custom [polycarbonate](https://www.amazon.com/gp/product/B000G6SJS8) frame with [standoffs](https://www.amazon.com/gp/product/B01DD07PTW) and [velcro](https://www.amazon.com/gp/product/B01JNZ4R4W).


## Software

- [Python 3.6.4](https://docs.python.org/3/) with smbus2, psutils, and numpy
- [hostapd and dnsmasq for hosting a wifi network](https://frillip.com/using-your-raspberry-pi-3-as-a-wifi-access-point-with-hostapd/)


## Setup

### From the Raspberry Pi

With a fresh install of [Raspian Stretch Lite](https://www.raspberrypi.org/downloads/raspbian/), you should:

Run `raspi-config` and;
- Under `Advanced`, expand the filesystem.
- Under `Interfacing Options`, enable SSH and I2C.

Exit, restart, set root password, note the IP, mine was `192.168.1.235`, yours may vary.

### From the development machine

Passwords are for suckers:

    ssh-keygen -t ecdsa -f ~/.ssh/id_ecdsa -N ''
    ssh-copy-id -i ~/.ssh/id_ecdsa root@192.168.1.235

Assuming `git`, `python`, `pipenv` and `ansible` are already installed locally.

Includes two ansible playbooks:

- `ansible-playbook python3.yml` installs python 3.6.4 (takes a while)
- `ansible-playbook setup.yml` configures the wireless network, house-cleaning, etc

The Pi should now be broadcasting a wifi network called `flightcontroller`. Credentials are in `./ansible/files/hostapd.conf`.

For `~/.ssh/config`:

    Host havok
        User root
        IdentityFile ~/.ssh/id_ecdsa

For `/etc/hosts`:

    192.168.1.235    havok

## Development

### Locally

`python tower.py` will watch and sync `flightcontroller/*` to `/opt/flightcontroller` on the Pi.

### Open a new terminal

`preflight` will put you in the right environment to run `./fly.py`

    ssh havok
    preflight
    ./fly.py

The initial `pipenv install` takes about 30 minutes.

### Extra

Symlink the [`.itermocil`](https://github.com/TomAnthony/itermocil) file with `ln -s $(pwd)/.itermocil ~/.itermocil/flightcontroller.yml`

### To do

Have ansible configure the Pi python virtualenv
