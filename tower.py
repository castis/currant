#!/usr/bin/env python3
# kill $(ps aux | grep tower.p[y] | awk '{print $2}')

import sys
import os
import paramiko
from paramiko.ssh_exception import SSHException, AuthenticationException
import time
import getpass
import socket
import logging
import psutil
import argparse

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


parser = argparse.ArgumentParser(description='Tower, flight controller software')

# parser.add_argument('-v', '--verbose', action='count', default=0, help='increase verbosity')
parser.add_argument('-u', '--user', default='root', help='Specify SSH user')
parser.add_argument('-i', '--identity', default='~/.ssh/id_rsa', help='Specify SSH identity file location')
parser.add_argument('-p', '--password', action='store_true', default=False, help='Prompt for SSH password')
parser.add_argument('-l', '--local-dir', default='./vehicle', help='Local directory to watch and sync from')
parser.add_argument('-r', '--remote-dir', default='/opt/flightcontroller', help='Remote directory to sync to')
parser.add_argument('host', nargs='?', default='havok', help='what host to connect to')

args = parser.parse_args()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger()


connect_kwargs = {
    'username': args.user,
    'timeout': 2,
}
if args.password:
    connect_kwargs.update({
        'password': getpass.getpass(),
    })
elif args.identity:
    try:
        key_file = os.path.expanduser(args.identity)
        connect_kwargs.update({
            'pkey': paramiko.RSAKey.from_private_key_file(key_file),
        })
    except FileNotFoundError as e:
        logger.error('cannot access %s' % args.identity)
        exit(1)


logger.info('Connecting...')
try:
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.connect(args.host, **connect_kwargs)
except AuthenticationException as e:
    logger.error(e)
    exit(1)
except socket.timeout:
    logger.error("Connection timeout, is the pi awake?")
    exit(1)


from utils import SFTPClient

class FSEventHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if os.path.basename(event.src_path) == os.path.basename(__file__):
            logger.info("Restarting self")
            try:
                p = psutil.Process(os.getpid())
                for handler in p.open_files() + p.connections():
                    os.close(handler.fd)
            except Exception as e:
                logging.error(e)

            os.execl(sys.executable, sys.executable, *sys.argv)
            return

        if event.src_path.startswith(args.local_dir):
            sync_code_folder()

sftp = SFTPClient.from_transport(ssh.get_transport())

def sync_code_folder():
    try:
        logger.info('Syncing')
        sftp.put_dir(args.local_dir, args.remote_dir)
        ssh.exec_command('find %s -type f -iname "*.pyc" -delete' % args.remote_dir)
    except Exception as e:
        logger.error(e)



sync_code_folder()

observer = Observer()
observer.schedule(FSEventHandler(), '.', recursive=True)

try:
    observer.start()

    while True:
        time.sleep(10)

except KeyboardInterrupt:
    logger.info('Caught ^C, quitting')

except Exception as e:
    logger.error(e)

finally:
    observer.stop()
    sftp.close()
    ssh.close()

logger.info('Done')
