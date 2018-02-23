#!/usr/bin/env python3
# kill $(ps aux | grep sync.p[y] | awk '{print $2}')

import sys
import os
import paramiko
from paramiko.ssh_exception import SSHException, AuthenticationException
import time
import getpass
import logging
import psutil
import argparse

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


parser = argparse.ArgumentParser(description='Flight controller development utility')
# parser.add_argument('-v', '--verbose', action='count', default=0, help='increase verbosity')
parser.add_argument('-u', '--user', default='root', help='ssh user')
parser.add_argument('-i', '--identity', default='~/.ssh/id_rsa', help='ssh key')
parser.add_argument('-p', '--password', action='store_true', default=None, help='ssh password')
parser.add_argument('-l', '--local-dir', default='./engine', help='local directory')
parser.add_argument('-r', '--remote-dir', default='/opt/flightcontroller', help='remote directory')

parser.add_argument('host', nargs='?', default='havok', help='what host to connect to')

args = parser.parse_args()


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger()


ssh_kwargs = {
    'username': args.user,
    'timeout': 10,
}
if args.password:
    logger.info('Using password')
    ssh_kwargs.update({
        'password': getpass.getpass(),
    })
elif args.identity:
    logger.info('Using SSH key: %s' % (args.identity,))
    try:
        key_file = os.path.expanduser(args.identity)
        pkey = paramiko.RSAKey.from_private_key_file(key_file)
    except FileNotFoundError as e:
        logger.error(e)
        exit(1)
    ssh_kwargs.update({
        'pkey': pkey,
    })

logger.info('Connecting')

try:
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.connect(args.host, **ssh_kwargs)
except AuthenticationException as e:
    logger.error(e)
    exit(1)

class SFTPClient(paramiko.SFTPClient):
    # subclass that recursively sync a directory tree
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

def sync_code_folder():
    try:
        logger.info('Syncing')
        sftp.put_dir(args.local_dir, args.remote_dir)
        ssh.exec_command('find %s -type f -iname "*.pyc" -delete' % args.remote_dir)
    except Exception as e:
        logger.error(e)

class FSEventHandler(FileSystemEventHandler):
    def on_modified(self, event):
        # if this file was modified
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

sync_code_folder()

observer = Observer()
observer.schedule(FSEventHandler(), '.', recursive=True)

try:
    observer.start()

    while True:
        time.sleep(5)

except KeyboardInterrupt:
    logger.info('Caught ^C, quitting')

except Exception as e:
    logger.error(e)

finally:
    observer.stop()
    sftp.close()
    ssh.close()

logger.info('Done')
