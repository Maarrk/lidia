from argparse import _SubParsersAction, ArgumentDefaultsHelpFormatter, ArgumentParser, Namespace
from multiprocessing import Queue
import socket
from struct import unpack_from
from typing import Tuple

from ..mytypes import AircraftState, Buttons, Controls, RunFn


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
                # Contents of UDP packet is 4 doubles:
                # - Position of helicopter north of ship, in meters
                # - Position of helicopter east of ship, in meters
                # - Position of helicopter above  ship, in meters
                # - Helicopter heading, in radians
                #   - 0 pointing north, pi/2 (90⁰) pointing east
                (north, east, altitude, yaw) = unpack_from('>' + 'd' * 4, data)

                state = AircraftState()
                state.ned.north = north
                state.ned.east = east
                state.ned.down = -altitude
                state.att.yaw = yaw

                q.put(('smol', state.smol()))
            except socket.timeout:
                continue