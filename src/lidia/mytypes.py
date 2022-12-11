from argparse import _SubParsersAction, Namespace
import json
from multiprocessing import Queue
from typing import Any, Callable, Dict, List, NoReturn, Optional, Tuple
from pydantic import BaseModel

RunFn = Callable[[Queue, Namespace], NoReturn]
SetupFn = Callable[[_SubParsersAction], Tuple[str, RunFn]]


# HACK: These classes rely on iteration through dict of fields in the order they were defined
#       So far observed to work in CPython, but isn't guaranteed by language implementations

class VectorModel(BaseModel):
    """Vector data to be serialized as array in SMOL"""

    def smol(self) -> List[float]:
        return [getattr(self, name) for name in self.__fields__]

    @classmethod
    def from_list(cls, values):
        return cls(**dict(zip(cls.__fields__, values)))


class IntFlagModel(BaseModel):
    """Data like `enum.IntFlag` to be serialized as int bits in SMOL"""

    def smol(self) -> List[int]:
        result = []
        for i, name in enumerate(self.__fields__):
            if i % 32 == 0:
                result.append(0)
            if getattr(self, name):
                result[i // 32] |= 1 << (i % 32)
        return result

    @classmethod
    def from_list(cls, values):
        b_values = []
        for i, intval in enumerate(values):
            b_values.append(intval[i // 32] & (1 << (i % 32)))
        return cls(dict(zip(cls.__fields__, b_values)))


class Attitude(VectorModel):
    """Aircraft attitude applied in order: roll, pitch, yaw"""
    roll: float = 0
    """Rotation along longitudinal axis to the right, in radians"""
    pitch: float = 0
    """Rotation along lateral axis nose up, in radians"""
    yaw: float = 0
    """Rotation along vertical axis clockwise seen from above, in radians"""


class XYZ(VectorModel):
    """Vector in aircraft coordinate system"""
    x: float = 0
    """Longitudinal axis forward"""
    y: float = 0
    """Lateral axis to the right"""
    z: float = 0
    """Vertical axis downward"""


class NED(VectorModel):
    """Vector in local horizon coordinate system"""
    north: float = 0
    east: float = 0
    down: float = 0


class Controls(VectorModel):
    stick_right: float = 0
    stick_pull: float = 0
    throttle: float = 0
    pedals_right: float = 0
    collective_up: float = 0


class Borders(BaseModel):
    low = Controls.from_list([-1, -1, 0, -1, 0])
    high = Controls.from_list([1, 1, 1, 1, 1])

    def smol(self) -> Dict[str, Any]:
        return {
            'low': self.low.smol(),
            'high': self.high.smol(),
        }


class Buttons(IntFlagModel):
    cyc_ftr: bool = False
    coll_ftr: bool = False


class Instruments(BaseModel):
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


class AircraftState(BaseModel):
    """Full state of displayed aircraft initialised with defaults"""

    ned = NED()
    """Position in local horizon coordinate system, in meters"""
    att = Attitude()
    """Aircraft attitude, in radians"""
    v_body = XYZ()
    """Velocity in body frame, in meters per second"""
    v_ned = NED()
    """Velocity in local horizon coordinate system, in meters per second"""
    ctrl = Controls()
    """Current control inceptors position"""
    trgt = Controls()
    """Target inceptors position"""
    trim = Controls()
    """Controls trim"""
    brdr = Borders()
    """Task borders for inceptors"""
    btn = Buttons()
    """Currently pressed buttons"""
    instr = Instruments()
    """Instrument values"""

    class Config:
        json_encoders = {
            VectorModel: VectorModel.smol,
            Borders: Borders.smol,
            IntFlagModel: IntFlagModel.smol,
        }

    def smol(self) -> Dict[str, Any]:
        """Return self as dictionary with SMOL-defined keys"""
        # HACK: JSON roundtrip is required, because there is no encoder configuration for .dict()
        return json.loads(self.json(models_as_dict=False))


if __name__ == '__main__':
    state = AircraftState()
    print(state.smol())
