# Flight Controller

## Development

    pipenv run python sync.py

to send `./code` to `rpi:/home/flightcontroller`.

log in to the machine and run the controlling program

    ssh rpi -t "cd ~/flightcontroller; bash --login"
    pipenv run python main.py

## RPi setup

Machine configuration in `ansible/`

`cd ansible && ansible-playbook setup.yml`

### install python 3.6.4

`cd ansible && ansible-playbook python3.6.yml`

### xboxdrv debugging

`xboxdrv --wid 0 -l 2 --dpad-as-button --deadzone 12000`
