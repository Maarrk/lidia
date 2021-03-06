# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

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
[Unreleased]: https://gitlab.com/Maarrk/lidia/-/compare/v0.3.2...dev
[0.3.2]: https://gitlab.com/Maarrk/lidia/-/compare/v0.3.1...v0.3.2
[0.3.1]: https://gitlab.com/Maarrk/lidia/-/compare/v0.3.0...v0.3.1
[0.3.0]: https://gitlab.com/Maarrk/lidia/-/compare/v0.2.1...v0.3.0
[0.2.1]: https://gitlab.com/Maarrk/lidia/-/tree/v0.2.1
