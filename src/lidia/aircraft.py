import json
from math import cos, sin, sqrt
from time import time
from pydantic import BaseModel
from typing import Any, Dict, Iterable, List, Optional

from .config import Config as LidiaConfig
from .mytypes import VectorModel, IntFlagModel


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
    """Full state of displayed aircraft"""

    ned: Optional[NED] = None
    """Position in local horizon coordinate system, in meters"""
    att: Optional[Attitude] = None
    """Aircraft attitude, in radians"""
    v_body: Optional[XYZ] = None
    """Velocity in body frame, in meters per second"""
    v_ned: Optional[NED] = None
    """Velocity in local horizon coordinate system, in meters per second"""
    ctrl: Optional[Controls] = None
    """Current control inceptors position"""
    trgt: Optional[Controls] = None
    """Target inceptors position"""
    trim: Optional[Controls] = None
    """Controls trim"""
    brdr: Optional[Borders] = None
    """Task borders for inceptors"""
    btn: Optional[Buttons] = None
    """Currently pressed buttons"""
    instr: Optional[Instruments] = None
    """Instrument values"""
    t_boot: Optional[int] = None
    """Time from the start of simulation, in milliseconds"""

    class Config:
        json_encoders = {
            VectorModel: VectorModel.smol,
            Borders: Borders.smol,
            IntFlagModel: IntFlagModel.smol,
        }

    def smol(self) -> Dict[str, Any]:
        """Return self as dictionary with SMOL-defined keys"""
        # HACK: JSON roundtrip is required, because there is no encoder configuration for .dict()
        return json.loads(self.json(models_as_dict=False, exclude={f for f in self.__fields__ if getattr(self, f) is None}))

    @classmethod
    def from_smol(cls, smol: dict) -> 'AircraftState':
        state = cls()
        for name in ['ned', 'v_ned']:
            if name in smol:
                setattr(state, name, NED.from_list(smol[name]))
        if 'att' in smol:
            state.att = Attitude.from_list(smol['att'])
        if 'v_body' in smol:
            state.v_body = XYZ.from_list(smol['v_body'])
        for name in ['ctrl', 'trgt', 'trim']:
            if name in smol:
                setattr(state, name, Controls.from_list(smol[name]))
        # TODO: Borders
        if 'btn' in smol:
            state.btn = Buttons.from_list(smol[name])
        if 'instr' in smol:
            state.instr = Instruments()
            for name in ['ias', 'gs', 'alt', 'qnh', 'alt']:
                if name in smol['instr']:
                    setattr(state, name, smol['instr'][name])
        if 't_boot' in smol:
            state.t_boot = smol['t_boot']

        return state

    def _matmul(matrix: Iterable[float], multiplicand: Iterable[float]) -> List[float]:
        """Multiply 3x3 matrix by 3-element vector or 3x3 matrix"""
        assert len(matrix) == 9
        assert len(multiplicand) == 3 or len(multiplicand) == 9
        if len(multiplicand) == 3:
            m = matrix
            x, y, z = multiplicand
            return [
                x * m[0] + y * m[1] + z * m[2],
                x * m[3] + y * m[4] + z * m[5],
                x * m[6] + y * m[7] + z * m[8],
            ]
        if len(multiplicand) == 9:
            m = matrix
            n = multiplicand
            # aut
            return [
                m[0] * n[0] + m[1] * n[3] + m[2] * n[6], m[0] * n[1] + m[1] * n[4] + m[2] * n[7], m[0] * n[2] + m[1] * n[5] + m[2] * n[8],  # noqa
                m[3] * n[0] + m[4] * n[3] + m[5] * n[6], m[3] * n[1] + m[4] * n[4] + m[5] * n[7], m[3] * n[2] + m[4] * n[5] + m[5] * n[8],  # noqa
                m[6] * n[0] + m[7] * n[3] + m[8] * n[6], m[6] * n[1] + m[7] * n[4] + m[8] * n[7], m[6] * n[2] + m[7] * n[5] + m[8] * n[8],  # noqa
            ]

    def _transpose(matrix: Iterable[float]) -> List[float]:
        """Transpose 3x3 matrix"""
        assert len(matrix) == 9
        m = matrix
        return [
            m[0], m[3], m[6],
            m[1], m[4], m[7],
            m[2], m[5], m[8],
        ]

    def _rotmat(att: Attitude) -> List[float]:
        """Create 3x3 rotation matrix transforming body-frame vectors to outside frame"""
        s, c = sin(att.roll), cos(att.roll)
        rot_roll = [
            1, 0, 0,
            0, c, -s,
            0, s, c,
        ]
        s, c = sin(att.pitch), cos(att.pitch)
        rot_pitch = [
            c, 0, s,
            0, 1, 0,
            -s, 0, c
        ]
        s, c = sin(att.yaw), cos(att.yaw)
        rot_yaw = [
            c, -s, 0,
            s, c, 0,
            0, 0, 1
        ]

        return AircraftState._matmul(rot_yaw, AircraftState._matmul(rot_pitch, rot_roll))

    def xyz2ned(self, vec: XYZ) -> NED:
        """Transform from body frame vector to outside frame coordinates

        Assumes no rotation if `self.att` is missing"""
        if self.att is None:
            return NED.from_list([vec.x, vec.y, vec.z])
        else:
            return NED.from_list(AircraftState._matmul(AircraftState._rotmat(self.att), [vec.x, vec.y, vec.z]))

    def ned2xyz(self, vec: NED) -> XYZ:
        """Transform from outside frame to body frame coordinates

        Assumes no rotation if `self.att` is missing"""
        if self.att is None:
            return XYZ.from_list([vec.north, vec.east, vec.down])
        else:
            return XYZ.from_list(AircraftState._matmul(AircraftState._transpose(AircraftState._rotmat(self.att)), [vec.north, vec.east, vec.down]))

    def model_instruments(self, config: LidiaConfig):
        """Generate values for instruments based on known parameters and configuration"""
        self._model_ias(config)
        self._model_gs(config)
        self._model_alt(config)
        self._model_ralt(config)

    def _get_instr(self) -> Instruments:
        if self.instr is None:
            self.instr = Instruments()
        return self.instr

    def _model_ias(self, config: LidiaConfig) -> bool:
        ias = None
        if self.v_body is not None:
            ias = self.v_body.x
        elif self.v_ned is not None and self.att is not None:
            v_body = self.ned2xyz(self.v_ned)
            ias = v_body.x

        if ias is not None:
            self._get_instr().ias = ias * config.instruments.speed_multiplier
            return True
        return False

    def _model_gs(self, config: LidiaConfig) -> bool:
        gs = None
        if self.v_ned is not None:
            gs = sqrt(self.v_ned.north ** 2 + self.v_ned.east ** 2)
        elif self.v_body is not None and self.att is not None:
            v_ned = self.xyz2ned(self.v_body)
            gs = sqrt(v_ned.north ** 2 + v_ned.east ** 2)

        if gs is not None:
            self._get_instr().gs = gs * config.instruments.speed_multiplier
            return True
        return False

    def _model_alt(self, config: LidiaConfig) -> bool:
        if self.ned is not None:
            self._get_instr().alt = -self.ned.down * config.instruments.altitude_multiplier
            return True
        return False

    def _model_ralt(self, config: LidiaConfig) -> bool:
        if self.ned is not None:
            if abs(self.ned.down) <= config.instruments.radio_altimeter_activation:
                self._get_instr().ralt = -self.ned.down * config.instruments.altitude_multiplier
                return True
        return False

    def set_time(self, config: LidiaConfig):
        if config.start_time is not None:
            self.t_boot = int((time() - config.start_time) * 1000)


if __name__ == '__main__':
    # run this from src/ folder like this: python -m lidia.aircraft
    config = LidiaConfig()
    state = AircraftState()
    state.ned = NED.from_list([1, 2, 3])
    state.att = Attitude.from_list([4, 5, 6])
    state.v_body = XYZ.from_list([5, 0, 0])
    state.model_instruments(config)
    print(state.smol())
