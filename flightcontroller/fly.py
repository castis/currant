import asyncio
import argparse
import signal
import functools
import logging

from importlib import reload
from time import time

import engine


logging.basicConfig(
    level=logging.INFO,  # if args.quiet else logging.INFO,
    format="%(asctime)s - %(name)s - %(message)s",
    datefmt="%H:%M:%S",
)

logger = logging.getLogger()


parser = argparse.ArgumentParser(description='The power of FLIGHT!')
parser.add_argument(
    '--headless',
    action='store_true',
    dest='headless',
    help='Run without curses frontend'
)
parser.add_argument(
    '--quiet',
    action='store_true',
    dest='quiet',
    help='Sets logging level to ERROR'
)

args = parser.parse_args()

engine = engine.Engine(args)
loop = asyncio.get_event_loop()

try:
    # def hot_reload(signame):
    #     logger.info('SIGUSR1 received')

    # signame = 'SIGUSR1'
    # loop.add_signal_handler(
    #     getattr(signal, signame),
    #     functools.partial(hot_reload, signame)
    # )

    exit(loop.run_until_complete(engine.run()))
except KeyboardInterrupt as e:
    print('caught ^C')
    engine.stop()

    # Do not show `asyncio.CancelledError` exceptions during shutdown
    # (a lot of these may be generated, skip this if you prefer to see them)
    def shutdown_exception_handler(loop, context):
        if "exception" not in context or not isinstance(context["exception"], asyncio.CancelledError):
            loop.default_exception_handler(context)
    # loop.set_exception_handler(shutdown_exception_handler)

    # Handle shutdown gracefully by waiting for all tasks to be cancelled
    tasks = asyncio.gather(*asyncio.Task.all_tasks(loop=loop),
                           loop=loop, return_exceptions=True)
    tasks.add_done_callback(lambda t: loop.stop())
    tasks.cancel()

    # Keep the event loop running until it is either destroyed or all
    # tasks have really terminated
    while not tasks.done() and not loop.is_closed():
        loop.run_forever()

finally:
    loop.close()
