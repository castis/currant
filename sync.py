#!/usr/bin/env python
# kill $(ps aux | grep sync.p[y] | awk '{print $2}')

import sys
import os
import paramiko
import time
import logging
import psutil

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger()


hostname = 'havok'
username = 'root'
key_file = os.path.expanduser('~/.ssh/id_rsa')


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


try:
    transport = paramiko.Transport((hostname, 22))
except paramiko.ssh_exception.SSHException:
    exit(1)

pkey = paramiko.RSAKey.from_private_key_file(key_file)
transport.connect(username=username, pkey=pkey)
sftp = SFTPClient.from_transport(transport)


class FSEventHandler(FileSystemEventHandler):
    def on_modified(self, event):
        # if this file was modified
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

        if event.src_path.startswith('./code'):
            try:
                logger.info("syncing")
                sftp.put_dir('./code', '/opt/flightcontroller')
            except Exception as e:
                logger.error(e)

observer = Observer()
observer.schedule(FSEventHandler(), '.', recursive=True)
observer.start()

try:
    while True:
        time.sleep(1)
except:
    observer.stop()
    if sftp:
        sftp.close()
    transport.close()
    raise
