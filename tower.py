#!/usr/bin/env python3
# kill $(ps aux | grep tower.p[y] | awk '{print $2}')

import sys
import os
import socket
import logging

from argparse import ArgumentParser
from psutil import Process
from paramiko import RSAKey, SFTPClient, SSHClient
from paramiko.ssh_exception import SSHException, AuthenticationException
from time import sleep
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


parser = ArgumentParser(description='Tower, ground control utility for the raspberry fli')

parser.add_argument('-u', '--user', default='root', help='Specify SSH user')
parser.add_argument('-i', '--identity', default='~/.ssh/id_rsa', help='Specify SSH identity file location')
parser.add_argument('-l', '--local-dir', default='./vehicle', help='Local directory to watch and sync from')
parser.add_argument('-r', '--remote-dir', default='/opt/flightcontroller', help='Remote directory to sync to')
parser.add_argument('host', nargs='?', default='havok', help='Hostname of the remote machine')

args = parser.parse_args()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
logger = logging.getLogger()

try:
    key_file = os.path.expanduser(args.identity)
    ssh_kwargs = {
        'username': args.user,
        'timeout': 2,
        'pkey': RSAKey.from_private_key_file(key_file),
    }
except FileNotFoundError as e:
    logger.error('%s not found' % args.identity)
    exit(1)


logger.info('connecting')
try:
    ssh = SSHClient()
    ssh.load_system_host_keys()
    ssh.connect(args.host, **ssh_kwargs)
except AuthenticationException as e:
    logger.error('authentication error')
    exit(1)
except socket.timeout:
    logger.error('connection timeout, is the pi awake?')
    exit(1)
logger.info('connected')


class SFTPClient(SFTPClient):
    # modified to recursively sync a directory tree
    def put_dir(self, source, target):
        # target folder needs to already exist
        for item in os.listdir(source):
            source_path = os.path.join(source, item)
            target_path = '%s/%s' % (target, item)
            if os.path.isfile(source_path):
                self.put(source_path, target_path)
            else:
                self.mkdir(target_path, ignore_existing=True)
                self.put_dir(source_path, target_path)

    def mkdir(self, path, mode=511, ignore_existing=False):
        try:
            super(SFTPClient, self).mkdir(path, mode)
        except IOError:
            if not ignore_existing:
                raise

sftp = SFTPClient.from_transport(ssh.get_transport())

class FSEventHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if os.path.basename(event.src_path) == os.path.basename(__file__):
            logger.info("restarting self")
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

def sync_code_folder():
    try:
        logger.info('syncing')
        sftp.put_dir(args.local_dir, args.remote_dir)
        ssh.exec_command('find %s -type f -iname "*.pyc" -delete' % args.remote_dir)
    except Exception as e:
        logger.error(e)

observer = Observer()
observer.schedule(FSEventHandler(), '.', recursive=True)

try:
    logger.info('starting file watcher')
    observer.start()
    sync_code_folder()

    while True:
        sleep(1)

except KeyboardInterrupt:
    logger.info('caught ^C, quitting')

except Exception as e:
    logger.error(e)

finally:
    observer.stop()
    sftp.close()
    ssh.close()

logger.info('done')
