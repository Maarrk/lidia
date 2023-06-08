# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html) from version 0.4.0 onwards.

## [Unreleased]

### Added

- Helicopter RPM indicator with configurable limits
- Target IAS and VSI indicator
- Traffic display on HSI

## [0.8.1] - 2023-04-17

### Fixed

- Serializing `a_ned` field of `AircraftState`
- Zero division error on some runs of `demo` source

## [0.8.0] - 2023-04-04

### Added

- Interactive editing of output filename in pack maker
- Accelerations in `AircraftState`
- Working sideslip angle indicator in on ADI
- Argument descriptions for generated code
- Pack maker for [MBDyn](https://www.mbdyn.org/)
- Basic arithmetic operations on `VectorModel`
- Current state displayed in info page

### Changed

- Name of `$schema` property of `Config`

### Fixed

- Path issues in `pack_maker`, improved Simulink compatibility
- Configuration of flight path vector on ADI
- Deserializing `AircraftData.instr` from SMOL
- Attitude target transform at non-zero attitude

## [0.7.1] - 2023-03-01

### Fixed

- `confighelp` file name in package manifest
- Interactive utilities included in package

## [0.7.0] - 2023-03-01

### Added

- `info` page showing available screens
- Target attitude and flight path vector on ADI
- Interactive generator for MATLAB packing function

### Changed

- `AircraftState` had not self-referencing fields moved to `AircraftData`
- `trgt` and `trim` fields of `AircraftState` can contain full state now
- Method of roll indication on PFD can be configured between moving scale and pointer

### Deprecated

- `rpctask` available on `/` address - to be replaced with `info`
- Sending `trgt` and `trim` as property of root object - should be `trgt.ctrl` and `trim.ctrl`

### Fixed

- FTR indicators in `rpctask` now correspond to the right button

## [0.6.0] - 2023-02-17

### Added

- MATLAB function to pack most fields of `AircraftState`
- Rudder indicator in RPC Task GUI. _Note: the old view can be shown on page load with this suffix `#text,collective,cyclic`_
- Rudder value in `demo` source
- Configurable IAS Vne in `pfd`

### Changed

- `confighelp` text in Markdown (instead of ReStructured Text)
- `--passthrough-host` now has a default value for localhost
- Limits for target in RPC Task are displayed only inside their respective region background, translation is not limited

### Fixed

- Control stick pull direction in `flightgear` source
- Graphical limits for target in RPC Task reflect configured limits

## [0.5.0] - 2022-12-19

### Added

- Instrument configuration
- Utilities for coordinate system conversion in `AircraftState`
- `smol` source for packets in [MessagePack](https://msgpack.org/) or [JSON](https://www.json.org/)
- `flightgear` source for [FlightGear](https://www.flightgear.org/) simulator
- Forwarding received state over UDP

### Changed

- Simulation of instrument values moved to `AircraftState` from `demo` source

### Fixed

- Using shared config state to sources
- Type annotations use quoted name instead of `Self` to support python < 3.11
- Radio altimeter activation condition

## [0.4.0] - 2022-12-16

### Added

- Configuration with nested dictionaries using JSON, YAML and TOML files or command line arguments
- Command line arguments to control verbosity
- JSON Schema and file templates for configuration files
- Mock source `confighelp` for configuration utilities

### Changed

- Reworked state representation from `dataclasses.dataclass` to `pydantic.BaseModel`

### Removed

- Removed default values from `AircraftState`

### Fixed

- Altitude tape showing full units #1

## [0.3.5] - 2022-12-09

### Added

- Barometric altitude in PFD
- Ship approach screen
- Visualising region extents with `showRegions()` JavaScript function

### Changed

- Renamed `types` module to `mytypes` to avoid collision with built-in module

## [0.3.4] - 2022-12-05

### Fixed

- Included PFD page in manifest

## [0.3.3] - 2022-11-28

### Added

- PFD (Primary Flight Display) view
- Extended `AircraftState` and `demo` source with information shown on PFD
- Roboto Mono font for all text

### Changed

- Reworked display options into generic system

## [0.3.2] - 2022-06-13

### Added

- CLI argument `--version` (comply to GNU recommendations)

## Changed

- Version is set as a module attribute
- Short CLI arguments are first to match `-h, --help` line
- Disabled `eventlet` server output to console

## [0.3.1] - 2022-06-09

### Fixed

- Handling `rpctask` packages without boundary data

## [0.3.0] - 2022-06-09

### Added

- Values that are out of range are displayed with a red contour and have limited translation
- Display settings are updating the URL region, and can be set with URL region (the part after #)

### Changed

- Specified compatible version of dependencies

## [0.2.1] - 2022-06-02

- Initial release with `demo` and `rpctask` sources

<!-- prettier-ignore -->
[Unreleased]: https://gitlab.com/Maarrk/lidia/-/compare/v0.8.1...dev
[0.8.1]: https://gitlab.com/Maarrk/lidia/-/compare/v0.8.0...v0.8.1
[0.8.0]: https://gitlab.com/Maarrk/lidia/-/compare/v0.7.1...v0.8.0
[0.7.1]: https://gitlab.com/Maarrk/lidia/-/compare/v0.7.0...v0.7.1
[0.7.0]: https://gitlab.com/Maarrk/lidia/-/compare/v0.6.0...v0.7.0
[0.6.0]: https://gitlab.com/Maarrk/lidia/-/compare/v0.5.0...v0.6.0
[0.5.0]: https://gitlab.com/Maarrk/lidia/-/compare/v0.4.0...v0.5.0
[0.4.0]: https://gitlab.com/Maarrk/lidia/-/compare/v0.3.5...v0.4.0
[0.3.5]: https://gitlab.com/Maarrk/lidia/-/compare/v0.3.4...v0.3.5
[0.3.4]: https://gitlab.com/Maarrk/lidia/-/compare/v0.3.3...v0.3.4
[0.3.3]: https://gitlab.com/Maarrk/lidia/-/compare/v0.3.2...v0.3.3
[0.3.2]: https://gitlab.com/Maarrk/lidia/-/compare/v0.3.1...v0.3.2
[0.3.1]: https://gitlab.com/Maarrk/lidia/-/compare/v0.3.0...v0.3.1
[0.3.0]: https://gitlab.com/Maarrk/lidia/-/compare/v0.2.1...v0.3.0
[0.2.1]: https://gitlab.com/Maarrk/lidia/-/tree/v0.2.1
