# Flight Controller


## Built with

- [Raspberry Pi 3 B](https://www.raspberrypi.org/products/raspberry-pi-3-model-b/), running [Raspian Stretch Lite](https://www.raspberrypi.org/downloads/raspbian/), housed in a [Pibow 3 Coupé](https://shop.pimoroni.com/collections/raspberry-pi/products/pibow-coupe-for-raspberry-pi-3)
- [MPU-9250 Accelerometer/Gyroscope/Compass](https://www.amazon.com/gp/product/B01I1J0Z7Y)
- [HC-SR04 Ultrasonic Sensor](https://www.sparkfun.com/products/13959)
- (not yet implemented) [MPL3115A2 Altitude/Pressure Sensor](https://www.sparkfun.com/products/11084)
- [LDPower D-250 ESC/Motor set](https://hobbyking.com/en_us/ldpower-d250-2-multicopter-power-system-2206-1900kv-6-x-3-4-pack.html) with [JST connectors](https://www.amazon.com/gp/product/B01M5AHF0Z) for convenience
- [Turnigy 2200mAh 3S 20C Battery](https://hobbyking.com/en_us/turnigy-2200mah-3s-25c-lipo-pack.html)
- [OCDAY 3A Power Distribution Board](https://www.amazon.com/gp/product/B01IOHWHI8) with bonus 5v output
- [Xbox 360 controller](https://en.wikipedia.org/wiki/List_of_Xbox_360_accessories#Xbox_360_controllers)
- [Wireless Controller Receiver](https://en.wikipedia.org/wiki/List_of_Xbox_360_accessories#Wireless_Gaming_Receiver) with removed housing and shortened cable
- [USB Wireless Adapter](https://www.amazon.com/Edimax-EW-7811Un-150Mbps-Raspberry-Supports/dp/B003MTTJOY) for connecting to the Pi over its own wifi network
- Mounted to a [plexiglas frame](https://www.amazon.com/gp/product/B000G6SJS8) using [standoffs](https://www.amazon.com/gp/product/B01DD07PTW) and [velcro straps](https://www.amazon.com/gp/product/B01JNZ4R4W).


### Software

- [Python 3.6.4](https://docs.python.org/3/) with smbus2, psutils, and numpy
- [xboxdrv](https://github.com/xboxdrv/xboxdrv) for xbox controller support
- [hostapd and dnsmasq for hosting a wifi network](https://frillip.com/using-your-raspberry-pi-3-as-a-wifi-access-point-with-hostapd/)


## Setup

### On the Raspberry PI

From a fresh install of [Raspian Stretch Lite](https://www.raspberrypi.org/downloads/raspbian/), here's what I did.

Hook up a display, keyboard, and ethernet, run `raspi-config` and:
- Advanced > Expand Filesystem
- Interfacing Options > SSH > Enable
- Interfacing Options > I2C > Enable

Exit, restart, set root password, note the IP, mine was `192.168.1.235`, yours may vary.

### On your laptop

Make a new ssh key:

    ssh-keygen -t ecdsa -f ~/.ssh/id_ecdsa -N ''
    ssh-copy-id -i ~/.ssh/id_ecdsa root@192.168.1.235

Drop this in your `~/.ssh/config`:

    Host havok
        User root
        IdentityFile ~/.ssh/id_ecdsa

And `192.168.1.235 havok` in my `/etc/hosts`

Assuming `git`, [`pipenv`](https://docs.pipenv.org/install/#installing-pipenv) and [`ansible`](http://docs.ansible.com/ansible/latest/intro_installation.html) are already installed locally.

    git clone git@github.com:castis/flightcontroller.git && cd flightcontroller

#### Ansible configuration

From the flightcontroller directory, `cd ansible/` and run the following (both will take a few minutes)

- `ansible-playbook python3.yml` will install python 3.6.4 (took my RPi 3 around 20 minutes, compiles python from source)
- `ansible-playbook setup.yml` will:
  - set the hostname
  - remove the default `pi` user
  - erase the contents of `/etc/motd`
  - install the python libraries for the flight controller
  - install and configure xboxdrv
  - install and configure dnsmasq and hostapd (using [this guide](https://frillip.com/using-your-raspberry-pi-3-as-a-wifi-access-point-with-hostapd/) as a starting point)
  - install pipenv

Using the USB wireless adapter and the credentials from `./ansible/hostapd.conf`, you should now be able to connect to the WiFi network the Pi is broadcasting.

## Development

Locally, start a `pipenv shell`.

`python tower.py` will watch and sync `vehicle/*` to `/opt/flightcontroller` on the Pi.

On first run, you should

    ssh havok
    cd flightcontroller
    pipenv --python 3.6
    pipenv install

Should be able to log in now `ssh havok`, `cd flightcontroller`,

To run the program, log in, fire up a pipenv shell, and run it.

    ssh havok -t "cd /opt/flightcontroller; pipenv shell; bash --login"
    python main.py

### Extra

`.itermocil` is the [itermocil](https://github.com/TomAnthony/itermocil) file I use for development to make things a little easier. `ln -s $(pwd)/.itermocil ~/.itermocil/flightcontroller` should symlink it into the right spot.

### To do

Have ansible configure the remote python virtual environment
