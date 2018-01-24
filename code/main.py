#!/usr/bin/python3.6

import argparse
import logging
import orion

parser = argparse.ArgumentParser(description='The power of FLIGHT!')
parser.add_argument(
    '--headless',
    action='store_true',
    help='Run without curses frontend'
)
# parser.add_argument(
#     '--verbose',
#     action='store_true',
#     help='Be noisy'
# )

args = parser.parse_args()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(message)s",
    datefmt="%H:%M:%S",
)

if __name__ == "__main__":
    orion.Engine(args)
