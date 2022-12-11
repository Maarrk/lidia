from argparse import _SubParsersAction, ArgumentDefaultsHelpFormatter, ArgumentError, ArgumentParser, Namespace
from math import cos, pi, sin
from multiprocessing import Queue
from time import sleep, time
from typing import Tuple

from ..mytypes import AircraftState, Buttons, Controls, RunFn


def setup(subparsers: _SubParsersAction) -> Tuple[str, RunFn]:
    NAME = 'demo'
    parser: ArgumentParser = subparsers.add_parser(
        NAME,
        help='looping simulation demonstrating GUI',
        formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument('-T', '--period', type=float,
                        help='loop time in seconds', default=5.0)
    parser.add_argument('-f', '--frequency', type=float,
                        help='number of messages sent per second', default=30.0)
    parser.add_argument('--no-trim', action='store_false', dest='trim',
                        help='do not demonstrate trim function')
    parser.add_argument('--no-borders', action='store_false', dest='borders',
                        help='do not demonstrate borders function')
    parser.add_argument('--outside-range', action='store_true',
                        help='demonstrate values outside allowed range')
    parser.add_argument('--alt-zero', type=float,
                        help='altitude to hover around', default=65.0)
    parser.add_argument('--alt-change', type=float,
                        help='altitude change amplitude', default=10.0)

    return (NAME, run)


def run(q: Queue, args: Namespace):
    if args.period <= 0:
        raise ArgumentError(args.frequency, 'period must be positive')
    if args.frequency <= 0:
        raise ArgumentError(args.frequency, 'frequency must be positive')

    outside_offset = 0.6 if args.outside_range else 0.0

    def val(phase):
        """Generate a sinusoidal value with phase offset (from 0 to 1)"""
        return 0.6 * sin((time() / args.period + phase) * 2 * pi) + outside_offset

    def cycle_index(): return int(time() // args.period) % 3
    def current_phase(): return (time() / args.period) % 1

    last_trim = Controls()

    while True:
        state = AircraftState()

        state.ned.down = -args.alt_zero - args.alt_change * val(0.75)

        state.att.pitch = 0.5 * val(0)
        state.att.roll = 0.5 * val(0.25)
        state.att.yaw = 0.5 * val(0.5)

        state.v_body.x = 15 + 2.5 * val(0.5)

        state.v_ned.down = state.v_body.x * sin(state.att.pitch)

        state.ctrl.stick_pull = val(0.1)
        state.ctrl.stick_right = val(0.35)
        state.ctrl.collective_up = 0.3 + 0.5 * (val(0.2) + outside_offset)

        state.trgt.stick_pull = val(0.55)
        state.trgt.stick_right = val(0.3)
        state.trgt.collective_up = 0.3 + 0.5 * (val(0.4) + outside_offset)

        if cycle_index() == 1 and args.trim:
            if current_phase() < 0.4:
                state.btn.coll_ftr = True
            if current_phase() > 0.6:
                state.btn.cyc_ftr = True

        if state.btn.coll_ftr:
            last_trim.collective_up = state.ctrl.collective_up
        if state.btn.cyc_ftr:
            last_trim.stick_right = state.ctrl.stick_right
            last_trim.stick_pull = state.ctrl.stick_pull
        state.trim = last_trim

        if cycle_index() == 2 and args.borders:
            if current_phase() < 0.5:
                state.brdr.low = Controls.from_list(
                    [-0.8, -0.8, 0.1, -0.8, 0.1])
                state.brdr.high = Controls.from_list(
                    [0.8, 0.8, 0.9, 0.8, 0.9])
            if current_phase() > 0.5:
                state.brdr.low = Controls.from_list(
                    [-0.5, -0.5, 0.25, -0.5, 0.25])
                state.brdr.high = Controls.from_list(
                    [0.5, 0.5, 0.75, 0.5, 0.75])

        # only converts from m/s to kt
        state.instr.ias = state.v_body.x * 3600.0 / 1852.0
        state.instr.alt = 3.28084 * (-state.ned.down)
        if cycle_index() > 0:
            state.instr.gs = state.instr.ias * cos(state.att.pitch)
            state.instr.ralt = state.instr.alt
        else:
            state.instr.qnh = None

        q.put(('smol', state.smol()))
        sleep(1 / args.frequency)
