from enum import Enum
import os
from os import path
from typing import List, Optional
from pydantic import Field

from .mytypes import NestingModel


class RpctaskConfig(NestingModel):
    """Configuration for `rpctask`"""
    correct_tolerance: float = 0.03
    """Acceptable margin for green color"""
    warning_tolerance: float = 0.05
    """Acceptable margin for yellow color"""


class ApproachConfig(NestingModel):
    """Ship approach configuration"""
    nominal_alt: float = 3
    """Altitude at which the scale is 1, in meters"""
    camera_height: float = 10
    """Position of camera above aircraft origin, in meters

    Larger values of this make the scale change less drastically at low altitude"""


class InstrumentsConfig(NestingModel):
    """Configuration for instruments visualisation, units etc."""
    speed_multiplier: float = 3600.0 / 1852.0
    """Scaling factor to change state velocity in meters per second to displayed IAS and GS, default for knots"""
    altitude_multiplier: float = 1 / 0.3048
    """Scaling factor to change state altitude in meters to displayed altitude, default for feet"""
    radio_altimeter_activation: float = 2500.0 * 0.3048
    """Activation height of radio altimeter above which it is not modeled, default 2500ft"""


class FGPropertyNode(str, Enum):
    """Supported [FlightGear property tree](https://sourceforge.net/p/flightgear/fgdata/ci/next/tree/Docs/README.properties) paths"""
    latitude = '/position/latitude-deg'
    longitude = '/position/longitude-deg'
    altitude = '/position/altitude-ft'
    roll = '/orientation/roll-deg'
    pitch = '/orientation/pitch-deg'
    heading = '/orientation/heading-deg'
    aileron = '/controls/flight/aileron'
    elevator = '/controls/flight/elevator'
    rudder = '/controls/flight/rudder'
    throttle_all = '/controls/engines/throttle-all'


class FGDataType(str, Enum):
    """Supported FlightGear binary types"""
    double_t = 'double'
    float_t = 'float'
    int_t = 'int'

    def struct_char(self):
        if self == FGDataType.double_t:
            return 'd'
        elif self == FGDataType.float_t:
            return 'f'
        elif self == FGDataType.int_t:
            return 'i'


class FGChunk(NestingModel):
    """Chunk in [FlightGear Generic protocol](https://wiki.flightgear.org/Generic_protocol)"""
    name: Optional[str] = None
    node: FGPropertyNode
    data_type: FGDataType
    factor: float = 1.0


class FlightGearConfig(NestingModel):
    chunks: Optional[List[FGChunk]] = None
    """List of chunks as they would be in protocol XML file"""


class Config(NestingModel):
    """Root of configuration structure

    Every config field in this and children should be provided with defaults,
    that can be overriden by config files"""

    dollar_schema: Optional[str] = Field(alias='$schema', default=None)
    """Allow the `$schema` property for specifying JSON Schema URL"""
    rpctask = RpctaskConfig()
    approach = ApproachConfig()
    instruments = InstrumentsConfig()
    flightgear = FlightGearConfig()
    start_time: Optional[float] = None
    """Epoch time in seconds of starting the program (see `time.time()`)"""


def schema_location():
    root_path = path.abspath(path.dirname(__file__))
    data_path = path.join(root_path, 'data')
    os.makedirs(data_path, exist_ok=True)
    return path.join(data_path, 'lidia-config.json')


def write_schema():
    with open(schema_location(), 'w') as out:
        out.write(Config.schema_json(by_alias=True))
