from argparse import _SubParsersAction, ArgumentError, ArgumentParser, Namespace
from math import pi, sin
from multiprocessing import Queue
from time import sleep, time
from typing import Tuple

from ..types import AircraftState, RunFn


def setup(subparsers: _SubParsersAction) -> Tuple[str, RunFn]:
    NAME = 'demo'
    parser: ArgumentParser = subparsers.add_parser(NAME,
                                                   help='looping simulation demonstrating GUI')
    parser.add_argument('--period', '-T', type=float,
                        help='loop time in seconds', default=5.0)
    parser.add_argument('--frequency', '-f', type=float,
                        help='number of messages sent per second', default=30.0)

    return (NAME, run)


def run(q: Queue, args: Namespace):
    if args.period <= 0:
        raise ArgumentError(args.frequency, 'period must be positive')
    if args.frequency <= 0:
        raise ArgumentError(args.frequency, 'frequency must be positive')

    def val(phase):
        """Generate a sinusoidal value with phase offset (from 0 to 1)"""
        return 0.6 * sin((time() / args.period + phase) * 2 * pi)

    while True:
        state = AircraftState()

        state.ctrl.stick_pull = val(0.1)
        state.ctrl.stick_right = val(0.35)
        state.ctrl.collective_up = 0.3 + 0.5 * val(0.2)

        state.trgt.stick_pull = val(0.55)
        state.trgt.stick_right = val(0.3)
        state.trgt.collective_up = 0.3 + 0.5 * val(0.4)

        q.put(('smol', state.smol()))
        sleep(1 / args.frequency)
