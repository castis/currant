# Currant

Python flight controller setup for a Raspberry Pi.

<img src="https://gitlab.com/b1tzky/currant/raw/master/image.jpg">

## Hardware

- [Raspberry Pi 3 B+](https://www.raspberrypi.org/products/raspberry-pi-3-model-b-plus/), running [Raspian Stretch Lite](https://www.raspberrypi.org/downloads/raspbian/), housed in a [Pibow 3 Coupé](https://shop.pimoroni.com/products/pibow-coupe-for-raspberry-pi-3-b-plus)
- [LDPower D-250 ESC/Motor set](https://hobbyking.com/en_us/ldpower-d250-2-multicopter-power-system-2206-1900kv-6-x-3-4-pack.html)
- [Turnigy 2200mAh 3S 20C Battery](https://hobbyking.com/en_us/turnigy-2200mah-3s-25c-lipo-pack.html)
- [OCDAY 3A Power Distribution Board](https://www.amazon.com/gp/product/B01IOHWHI8)
- [8BitDo SN30 Pro](http://www.8bitdo.com/sn30-pro-g-classic-or-sn30-pro-sn/)
- [USB Wireless Adapter](https://www.edimax.com/edimax/merchandise/merchandise_detail/data/edimax/global/wireless_adapters_n150/ew-7811un) for connecting to the Pi over its own wifi network
- [MPU-9250 Accelerometer/Gyroscope/Compass](https://www.amazon.com/gp/product/B01I1J0Z7Y)
- [HC-SR04 Ultrasonic Sensor](https://www.sparkfun.com/products/13959)
- (not yet implemented) [MPL3115A2 Altitude/Pressure Sensor](https://www.sparkfun.com/products/11084)
- All mounted to a custom [polycarbonate](https://www.amazon.com/gp/product/B000G6SJS8) frame with [standoffs](https://www.amazon.com/gp/product/B01DD07PTW) and [velcro](https://www.amazon.com/gp/product/B01JNZ4R4W).


## Initial setup

### The vehicle

From a fresh install of [Raspian Stretch Lite](https://www.raspberrypi.org/downloads/raspbian/):

Connect it to the local network via ethernet (the wireless card is used to manage a network)

- note the IP
- set a root password
- Run `raspi-config`
	- Under `Localisation Options`, set the proper keyboard layout.
	- Under `Advanced`, expand the filesystem if it didn't automatically do this at first boot.
	- Under `Interfacing Options`, enable `SSH` and `I2C`.
- change `PermitRootLogin` for the moment: `sed -i -E "s/^#?(PermitRootLogin)/\1 yes/" /etc/ssh/sshd_config` and `systemctl restart ssh`

Ansible will change that `yes` to a `prohibit-password` later.

### The development machine

Assuming `git`, `python >= 3.6`, `ansible`, and `pipenv` are installed

For `/etc/hosts`:

    192.168.1.XXX currant

Create and sync an SSH key (the keys I generated from macOS with OpenSSH didn't play with paramiko nicely, I had to generate the keys on the Pi and move them locally):

    ssh-keygen -t ecdsa -f ~/.ssh/currant_ecdsa -b 521 -N ''
    ssh-copy-id -i ~/.ssh/id_ecdsa root@currant

For `~/.ssh/config`:

    Host currant
        User root
        IdentityFile ~/.ssh/currant_ecdsa

The ansible playbooks will configure the rest; go into `./ansible/` and run them

- `ansible-playbook python3.yml` installs the python version set in that file (takes like half an hour)
- `ansible-playbook setup.yml` configures the wireless network, interfaces, house-cleaning, etc

([these](https://frillip.com/using-your-raspberry-pi-3-as-a-wifi-access-point-with-hostapd/) are the instructions I used to originally configure the wireless setup)

The USB wireless card can now be used to connect to the vehicle's wireless network.
By default, the network is `currant`, as is the username. Password is `currantpw`.

Once connected, change the line in your `/etc/hosts/` to:

	172.24.1.1 currant

## Development

I've been using [`itermocil --here`](https://github.com/TomAnthony/itermocil) to open several shell instances.

One for git/local process work, one for running the main python process on the vehicle, and one for watching/syncing local code to it.

### The local processes

From the base dir, `pipenv shell ./tower.py` will watch and sync `./currant/*` to `/opt/currant` on the vehicle.

### The remote process

A `preflight` script is included to `cd` into `/opt/currant` and then start a pipenv shell.

The main process can be started with.

    ssh currant
    preflight
    ./fly.py

The first time `preflight` is run, it will install all the necessary dependencies. That takes about 30 minutes.
