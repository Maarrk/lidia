# Lidia

![lidia](https://img.shields.io/pypi/v/lidia)

_Lightweight Instrument Display Interface for Aircraft_

lidia is a Python package for serving an aircraft instruments panel as a web page.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install lidia.

```bash
pip install lidia
```

## Usage

```bash
lidia demo

# if your Scripts folder isn't in Path:
python3 -m lidia demo

# use other source
lidia rpctask

# show general help
lidia --help

# show help for a specific source
lidia demo --help

# pass the main server arguments before the source name
lidia -P 5556 demo
```

Then open the served page in a browser, by default [localhost:5555](http://localhost:5555).
The controls for showing and hiding elements of the GUI are shown when hovering the mouse in the bottom left region of the page.

<!-- TODO: visuals
- demo GIF with moving parts
- static screenshot with elements explained -->

## Support

Report problems in [GitLab Issues](https://gitlab.com/Maarrk/lidia/-/issues)

## Roadmap

- USB HID joystick source

## Contributing

- Contributions should be made to the [GitLab repository](https://gitlab.com/Maarrk/lidia)
- Python code should be formatted with autopep8
- Other source files should be formatted with Prettier
- Install packages for development with `pip install -r requirements.txt`
- To properly run as a module without building and installing, **cd into `src/`** and run `python3 -m lidia`

## Acknowledgements

This software was developed in [Department of Aerospace Science and Technology](https://www.aero.polimi.it/) of Politecnico di Milano.

Instrument graphics designed by Davide Marchesoli and Qiuyang Xia.

## License

[MIT](https://choosealicense.com/licenses/mit/)
