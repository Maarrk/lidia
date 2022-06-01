from argparse import _SubParsersAction, ArgumentParser, Namespace
from multiprocessing import Queue
from time import sleep
from typing import Tuple

from ..types import RunFn, SetupFn


def setup(subparsers: _SubParsersAction) -> Tuple[str, RunFn]:
    NAME = 'demo'
    parser: ArgumentParser = subparsers.add_parser(NAME,
                                                   help='looping simulation demonstrating GUI')
    parser.add_argument('--period', '-T', type=float,
                        help='loop time in seconds', default=1.0)

    return (NAME, run)


def run(q: Queue, args: Namespace):
    print('Sending demo messages')
    while True:
        q.put(('echo', 'message from main loop'))
        sleep(args.period)
