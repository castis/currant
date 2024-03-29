#!/usr/bin/env python
# kill $(ps aux | awk '/[^]]tower.py/ {print $2}')

import logging
import os
import socket
import sys
from argparse import ArgumentParser
from time import sleep, strftime

import psutil
from paramiko import ECDSAKey, SFTPClient, SSHClient, AutoAddPolicy
from paramiko.ssh_exception import AuthenticationException, SSHException
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

parser = ArgumentParser(description="Tower, ground control utility")

parser.add_argument("--hostname", default="currant", help="Hostname of the vehicle")
parser.add_argument("--user", default="root", help="User name on the vehicle")
parser.add_argument("--identity", default="~/.ssh/currant_ecdsa", help="Path to the SSH identity file")
parser.add_argument("--local-dir", default="./currant", help="Local directory to watch and sync from")
parser.add_argument("--remote-dir", default="/opt/currant", help="Remote directory to sync to")
parser.add_argument("-c", "--configure", action="store_true", help="Run ansible configuration and exit")

args = parser.parse_args()
args.local_dir = os.path.abspath(args.local_dir)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s", datefmt="%H:%M:%S")
logging.getLogger("paramiko.transport").setLevel(logging.ERROR)
logger = logging.getLogger()

if args.configure:
    logger.info("here is where we run ansible playbooks")
    exit(0)

try:
    key_file = os.path.expanduser(args.identity)
    private_key = ECDSAKey.from_private_key_file(key_file)
except FileNotFoundError as e:
    logger.error(f"{args.identity} not found")
    exit(1)
except SSHException as e:
    logger.error(f"{key_file}; {e}")
    exit(1)

ssh = SSHClient()
ssh.set_missing_host_key_policy(AutoAddPolicy())
ssh.load_system_host_keys()

try:
    logger.info(f"connecting to {args.hostname}")
    ssh.connect(args.hostname, username=args.user, pkey=private_key)
except AuthenticationException as e:
    logger.error("authentication error")
    exit(1)
except socket.timeout:
    logger.error("connection timeout, is the vehicle awake?")
    exit(1)
except socket.error:
    logger.error("socket error")
    exit(1)
finally:
    logger.info("connected")


class SFTPClient(SFTPClient):
    # modified to recursively sync a directory tree
    def put_dir(self, source, target):
        for item in os.listdir(source):
            source_path = os.path.join(source, item)
            target_path = f"{target}/{item}"
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
        # when this file is modified, restart this process
        if os.path.basename(event.src_path) == os.path.basename(__file__):
            logger.info("restarting")
            try:
                p = psutil.Process(os.getpid())
                for handler in p.open_files() + p.connections():
                    os.close(handler.fd)
            except Exception as e:
                logging.error(e)

            os.execl(sys.executable, sys.executable, *sys.argv)

        elif event.src_path.startswith(args.local_dir):
            sync_code_folder()


def sync_code_folder():
    logger.info("syncing")
    try:
        sftp.put_dir(args.local_dir, args.remote_dir)
        ssh.exec_command(f'find {args.remote_dir} -type f -iname "*.pyc" -delete')
        # ssh.exec_command("systemctl restart currant.service")
        # ssh.exec_command("kill -SIGUSR1 $(ps -aux | awk '/[^]]fly.py/ {print $2}')")

    except FileNotFoundError as e:
        logger.error(f"{args.remote_dir} missing, trying to create")

        stdin, stdout, stderr = ssh.exec_command(f'mkdir {args.remote_dir}')
        if stdout.channel.recv_exit_status() == 0:
            logger.error(f'all good')
    except Exception as e:
        logger.error(e)
        exit(1)


observer = Observer()
observer.schedule(FSEventHandler(), ".", recursive=True)

try:
    date = strftime("%m%d%H%M%Y.%S")
    ssh.exec_command(f"date {date}")
    logger.info(f"set vehicle clock to {date}")

    sync_code_folder()

    observer.start()
    logger.info("watching for changes")

    # if args.getlogs:
    #     logger.info('Fetching debug logs')
    #     os.system(f'rsync -a {args.hostname}:{args.remote_dir}/logs ./')
    #     ssh.exec_command(f'find {args.remote_dir}/logs -type f -delete')

    while True:
        sleep(1)

except KeyboardInterrupt:
    logger.info(" quitting")

finally:
    observer.stop()
    try:
        sftp.close()
    except EOFError as e:
        # logger.info("Error closing sftp client, vehicle off?")
        pass
    ssh.close()

logger.info("aviation!")
