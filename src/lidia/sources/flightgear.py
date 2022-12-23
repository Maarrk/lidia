"""listen to UDP packets from FlightGear native socket protocol"""
from argparse import _SubParsersAction, ArgumentDefaultsHelpFormatter, ArgumentParser, Namespace
from math import pi
from multiprocessing import Queue
import socket
from struct import unpack_from
from typing import Tuple
import xml.etree.ElementTree as ET

from ..aircraft import *
from ..config import Config, FGChunk, FGPropertyNode
from .mytypes import RunFn, FGNetFDM


FT = 0.3048
"""conversion multiplier from feet to meters"""
DEG = pi / 180.0
"""conversion multiplier from degrees to radians"""


def setup(subparsers: _SubParsersAction) -> Tuple[str, RunFn]:
    NAME = 'flightgear'
    parser: ArgumentParser = subparsers.add_parser(
        NAME,
        help=__doc__,
        formatter_class=ArgumentDefaultsHelpFormatter,
        epilog="""To send packets at 30Hz from a local FlightGear instance,
add this command line argument: --native-fdm=socket,out,30,127.0.0.1,5004,udp""")
    parser.add_argument('-i', '--ip', type=str,
                        help='listen UDP adress', default='0.0.0.0')
    parser.add_argument('-p', '--port', type=int,
                        help='listen UDP port', default=5004)
    parser.add_argument('-g', '--generic-protocol', type=str,
                        help='generic protocol XML definition')

    return (NAME, run)


def run(q: Queue, args: Namespace, config: Config):
    if args.generic_protocol is not None:
        config.flightgear.chunks = []
        tree = ET.parse(args.generic_protocol)
        input_node = tree.getroot().find('generic').find('input')
        mode_node = input_node.find('binary_mode')
        assert mode_node.text == 'true', 'Currently only binary mode is supported'
        chunks_nodes = input_node.findall('chunk')
        for chunk_node in chunks_nodes:
            name = chunk_node.find('name').text
            node = chunk_node.find('node').text
            data_type = chunk_node.find('type').text
            chunk = FGChunk(name=name, node=node, data_type=data_type)
            if chunk_node.find('factor') is not None:
                chunk.factor = float(chunk_node.find('factor').text)
            config.flightgear.chunks.append(chunk)

    struct_fmt = ''
    if config.flightgear.chunks is not None:
        struct_fmt = '>' + ''.join([c.data_type.struct_char()
                                   for c in config.flightgear.chunks])

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        # Timeout is required to handle leaving with Ctrl+C
        sock.settimeout(1.0)
        sock.bind((args.ip, args.port))
        if args.verbosity >= 0:
            print(f'Listening for UDP packets on {args.ip}:{args.port}')

        while True:
            try:
                data, _ = sock.recvfrom(1024)

                state = AircraftState()
                if config.flightgear.chunks is None:
                    fg = FGNetFDM.from_bytes(data)

                    state.ned = NED()
                    # TODO: Add argument for reference location, calculate north and east from that
                    state.ned.down = -fg.altitude
                    state.att = Attitude()
                    state.att.roll = fg.phi
                    state.att.pitch = fg.theta
                    state.att.yaw = fg.psi
                    # Velocities in ft/s
                    state.v_body = XYZ()
                    state.v_body.x = fg.v_body_u * FT
                    state.v_body.y = fg.v_body_v * FT
                    state.v_body.z = fg.v_body_w * FT
                    state.v_ned = NED()
                    state.v_ned.north = fg.v_north * FT
                    state.v_ned.east = fg.v_east * FT
                    state.v_ned.down = fg.v_down * FT
                    state.ctrl = Controls()
                    # TODO: Check direction and range of the following
                    state.ctrl.stick_pull = fg.elevator
                    state.ctrl.stick_right = fg.right_aileron
                    state.ctrl.pedals_right = fg.rudder

                    state.model_instruments(config)
                    if state.instr.ralt is not None:
                        state.instr.ralt = fg.agl * config.instruments.altitude_multiplier

                else:  # Using generic protocol
                    unpacked = unpack_from(struct_fmt, data)
                    for val, c in zip(unpacked, config.flightgear.chunks):
                        scaled = val * c.factor
                        # TODO: Handle latitude and longitude
                        if c.node == FGPropertyNode.altitude:
                            state._get_ned().down = -scaled * FT
                        elif c.node == FGPropertyNode.roll:
                            state._get_att().roll = scaled * DEG
                        elif c.node == FGPropertyNode.pitch:
                            state._get_att().pitch = scaled * DEG
                        elif c.node == FGPropertyNode.heading:
                            state._get_att().yaw = scaled * DEG
                        elif c.node == FGPropertyNode.aileron:
                            state._get_ctrl().stick_right = scaled
                        elif c.node == FGPropertyNode.elevator:
                            state._get_ctrl().stick_right = scaled
                        elif c.node == FGPropertyNode.throttle_all:
                            # This is how it is used in helicopters
                            state._get_ctrl().collective_up = scaled
                    state.model_instruments(config)

                state.set_time(config)

                q.put(('smol', state.smol()))
            except socket.timeout:
                continue
