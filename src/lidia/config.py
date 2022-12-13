from .mytypes import NestingModel


class RpctaskConfig(NestingModel):
    """Configuration for `rpctask`"""
    correct_tolerance: float = 0.03
    """Acceptable margin for green color"""
    warning_tolerance: float = 0.05
    """Acceptable margin for yellow color"""


class ApproachConfig(NestingModel):
    nominal_alt: float = 3
    """Altitude at which the scale is 1, in meters"""
    camera_height: float = 10
    """Position of camera above aircraft origin, in meters

    Larger values of this make the scale change less drastically at low altitude"""


class Config(NestingModel):
    """Root of configuration structure

    Every config field in this and children should be provided with defaults,
    that can be overriden by config files"""

    rpctask = RpctaskConfig()
    approach = ApproachConfig()
