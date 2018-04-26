import paramiko
import os

from watchdog.events import FileSystemEventHandler


class Tower():
    args = []

    def __init__(self, args):
        self.args = args

    def restart():
        pass

    def sync_code_folder():
        try:
            logger.info('Syncing')
            sftp.put_dir(self.args.local_dir, self.args.remote_dir)
            ssh.exec_command('find %s -type f -iname "*.pyc" -delete' % self.args.remote_dir)
        except Exception as e:
            logger.error(e)





# class FSEventHandler(FileSystemEventHandler):
#     def on_modified(self, event):
#         if os.path.basename(event.src_path) == os.path.basename(__file__):
#             logger.info("Restarting self")
#             try:
#                 p = psutil.Process(os.getpid())
#                 for handler in p.open_files() + p.connections():
#                     os.close(handler.fd)
#             except Exception as e:
#                 logging.error(e)

#             os.execl(sys.executable, sys.executable, *sys.argv)
#             return

#         if event.src_path.startswith(args.local_dir):
#             sync_code_folder()
