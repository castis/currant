import argparse
import functools
import logging
import os
import signal
import sys
from time import time

import asyncio
import engine
import psutil
from importlib import reload

parser = argparse.ArgumentParser(description="The power of FLIGHT!")

parser.add_argument(
    "--debug", action="store_true", dest="debug", help="Sets debug mode"
)

args = parser.parse_args()

logging.basicConfig(
    level=logging.DEBUG if args.debug else logging.INFO,
    format="%(asctime)s - %(name)s - %(message)s",
    datefmt="%H:%M:%S",
)

logger = logging.getLogger()

eng = engine.Engine(args)
loop = asyncio.get_event_loop()

try:

    def restart():
        logger.info("restarting")
        try:
            p = psutil.Process(os.getpid())
            for handler in p.open_files() + p.connections():
                os.close(handler.fd)
        except Exception as e:
            logging.error(e)

        os.execl(sys.executable, sys.executable, *sys.argv)

    loop.add_signal_handler(signal.SIGUSR1, functools.partial(restart))

    code = loop.run_until_complete(eng.start())
    exit(code)

except KeyboardInterrupt as e:
    print("caught ^C")
    eng.stop()

    # eat CancelledError exceptions during shutdown
    def shutdown_exception_handler(loop, context):
        if "exception" not in context or not isinstance(
            context["exception"], asyncio.CancelledError
        ):
            loop.default_exception_handler(context)

    loop.set_exception_handler(shutdown_exception_handler)

    # wait for all tasks to be cancelled
    tasks = asyncio.gather(
        *asyncio.Task.all_tasks(loop=loop), loop=loop, return_exceptions=True
    )
    tasks.add_done_callback(lambda t: loop.stop())
    tasks.cancel()

    # keep the event loop running until it is either destroyed or all
    # tasks have really terminated
    while not tasks.done() and not loop.is_closed():
        loop.run_forever()

finally:
    loop.close()
