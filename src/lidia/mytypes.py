from argparse import _SubParsersAction, Namespace
from dataclasses import dataclass, asdict
from enum import IntFlag
from multiprocessing import Queue
from typing import Callable, List, NoReturn, Optional, Tuple


RunFn = Callable[[Queue, Namespace], NoReturn]
SetupFn = Callable[[_SubParsersAction], Tuple[str, RunFn]]


@dataclass
class Attitude:
    roll: float = 0
    pitch: float = 0
    yaw: float = 0

    def smol(self) -> List[float]:
        return [
            self.roll,
            self.pitch,
            self.yaw
        ]


@dataclass
class XYZ:
    """Vector in aircraft coordinate system"""
    x: float = 0
    """Longitudinal axis forward"""
    y: float = 0
    """Lateral axis to the right"""
    z: float = 0
    """Vertical axis downward"""

    def smol(self) -> List[float]:
        return [self.x, self.y, self.z]


@dataclass
class NED:
    """Vector in local horizon coordinate system"""
    north: float = 0
    east: float = 0
    down: float = 0

    def smol(self) -> List[float]:
        return [
            self.north,
            self.east,
            self.down
        ]


@dataclass
class Controls:
    stick_right: float = 0
    stick_pull: float = 0
    throttle: float = 0
    pedals_right: float = 0
    collective_up: float = 0

    def smol(self) -> List[float]:
        return [
            self.stick_right,
            self.stick_pull,
            self.throttle,
            self.pedals_right,
            self.collective_up
        ]


class Borders:
    def __init__(self) -> None:
        self.low = Controls(-1, -1, 0, -1, 0)
        self.high = Controls(1, 1, 1, 1, 1)

    def smol(self) -> dict:
        return {
            'low': self.low.smol(),
            'high': self.high.smol()
        }


class Buttons(IntFlag):
    NONE = 0
    CYC_FTR = 1 << 0
    COLL_FTR = 1 << 1

    def smol(self) -> List[int]:
        return [int(self)]


@dataclass
class Instruments:
    ias: float = 0
    """Indicated airspeed"""
    gs: Optional[float] = None
    """Groundspeed"""
    alt: float = 0
    """Barometric altitude"""
    qnh: Optional[float] = 1013
    """Altimeter setting, None for STD"""
    ralt: Optional[float] = None
    """Radio altimeter"""

    def smol(self) -> dict:
        return asdict(self)


class AircraftState:
    """Full state of displayed aircraft initialised with defaults"""

    def __init__(self) -> None:
        self.ned = NED()
        """Position in local horizon coordinate system, in meters"""
        self.att = Attitude()
        """Aircraft attitude, in radians"""
        self.v_body = XYZ()
        """Velocity in body frame, in meters per second"""
        self.v_ned = NED()
        """Velocity in local horizon coordinate system, in meters per second"""
        self.ctrl = Controls()
        """Current control inceptors position"""
        self.trgt = Controls()
        """Target inceptors position"""
        self.trim = Controls()
        """Controls trim"""
        self.brdr = Borders()
        """Task borders for inceptors"""
        self.btn = Buttons.NONE
        """Currently pressed buttons"""
        self.instr = Instruments()
        """Instrument values"""

    def smol(self) -> dict:
        """Return self as dictionary with SMOL-defined keys"""
        d = dict()
        for key in ['ned', 'att', 'v_body', 'v_ned', 'ctrl', 'trgt', 'trim', 'brdr', 'btn', 'instr']:
            d[key] = getattr(self, key).smol()
        return d
