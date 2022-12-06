from argparse import _SubParsersAction, ArgumentDefaultsHelpFormatter, ArgumentParser, Namespace
from multiprocessing import Queue
import socket
from struct import unpack_from
from typing import Tuple

from ..types import AircraftState, Buttons, Controls, RunFn


def setup(subparsers: _SubParsersAction) -> Tuple[str, RunFn]:
    NAME = 'approach'
    parser: ArgumentParser = subparsers.add_parser(
        NAME,
        help='listen to UDP packets from Rotorcraft-Pilot Coupling Task simulator',
        formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument('-i', '--ip',
                        help='listen UDP adress', default='0.0.0.0')
    parser.add_argument('-p', '--port', type=int,
                        help='listen UDP port', default=5004)

    return (NAME, run)


def run(q: Queue, args: Namespace):

    last_trim = Controls()

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        # Timeout is required to handle leaving with Ctrl+C
        sock.settimeout(1.0)
        sock.bind((args.ip, args.port))
        print(f'Listening for UDP packets on {args.ip}:{args.port}')

        while True:
            try:
                data, _ = sock.recvfrom(1024)
                # As named in the original FlightGear protocol file
                # cyclic has coordinates 0,0 in bottom left and 1,1 in top right
                (pitch_ctrl, roll_ctrl, pwr_ctrl) = unpack_from('>' + 'd' * 3, data)
                
                # the controls should be in (-1, 1)
                # we receive inside (0, 1)
                state = AircraftState()
                state.ctrl.stick_right = (roll_ctrl * 2.0) - 1.0
                state.ctrl.stick_pull = (pitch_ctrl * 2.0) - 1.0 # this is correct: fwd cyclic --> fwd flight, so the ship moves aft from ownship position
                state.ctrl.collective_up = pwr_ctrl
                
                

                q.put(('smol', state.smol()))
            except socket.timeout:
                continue