# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

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
[Unreleased]: https://gitlab.com/Maarrk/lidia/-/compare/v0.4.0...dev
[0.4.0]: https://gitlab.com/Maarrk/lidia/-/compare/v0.3.5...v0.4.0
[0.3.5]: https://gitlab.com/Maarrk/lidia/-/compare/v0.3.4...v0.3.5
[0.3.4]: https://gitlab.com/Maarrk/lidia/-/compare/v0.3.3...v0.3.4
[0.3.3]: https://gitlab.com/Maarrk/lidia/-/compare/v0.3.2...v0.3.3
[0.3.2]: https://gitlab.com/Maarrk/lidia/-/compare/v0.3.1...v0.3.2
[0.3.1]: https://gitlab.com/Maarrk/lidia/-/compare/v0.3.0...v0.3.1
[0.3.0]: https://gitlab.com/Maarrk/lidia/-/compare/v0.2.1...v0.3.0
[0.2.1]: https://gitlab.com/Maarrk/lidia/-/tree/v0.2.1
