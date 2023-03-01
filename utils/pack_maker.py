import argparse
from enum import auto, IntEnum
import inspect
from io import StringIO
import os
import platform
from pydantic import BaseModel
import sys
from typing import Any, List, Optional, Tuple

# setup cross-platform getch() and clear()
if platform.system() == "Windows":
    import msvcrt

    def getch():
        return msvcrt.getwch()

    def clear():
        os.system('cls')
else:
    import tty
    import termios
    import sys

    def getch():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    def clear():
        os.system('clear')

this_path = os.path.dirname(os.path.realpath(__file__))
lidia_path = os.path.join(this_path, '..', 'src')
sys.path.append(lidia_path)
from lidia.aircraft import AircraftData, VectorModel  # noqa prevent moving to top of file


class Model:
    def __init__(self, output: str, verbose=False):
        self.output = output
        self.verbose = verbose
        self.last_key = 0

        self.parts = ['main', 'trgt', 'trim']
        self.selected_part = self.parts[0]
        self.field_source = {f: next((doc.strip().replace('"""', ''), decl, AircraftData.__fields__[f].annotation.__args__[0]) for (decl, doc)
                                     in zip(inspect.getsourcelines(AircraftData)[0], inspect.getsourcelines(AircraftData)[0][1:])
                                     if decl.strip().startswith(f))
                             for f in AircraftData.__fields__}
        # only serialization of vectors is supported
        self.toggles = [(f, *src) for f, src in self.field_source.items()
                        if (issubclass(src[2], VectorModel) or src[2] is int)]
        self.enabled = {part: ([False] * len(self.toggles))
                        for part in self.parts}

        self.extra_choices = 2
        self.selected_choice = 0

        self.status = ''

    def _get_choices_num(self):
        return len(self.toggles) + len(self.parts) + self.extra_choices

    choices_num = property(fget=_get_choices_num)

    def _get_selected_part_index(self):
        return next(i for i, p in enumerate(self.parts) if p == self.selected_part)

    selected_part_index = property(fget=_get_selected_part_index)

    def _get_enabled_num(self):
        return sum(len([en for en in self.enabled[p] if en]) for p in self.parts)

    enabled_num = property(fget=_get_enabled_num)


class Command(IntEnum):
    QUIT = auto()
    MAKE = auto()


class Message(IntEnum):
    KEY = auto()
    STATUS = auto()


def view(model: Model):
    clear()
    print('Choose fields to be serialized in message')
    print('Use arrows or j, k to move, select with Enter or Space\n')
    for i, ((name, doc, decl, cls), enabled) in enumerate(zip(model.toggles, model.enabled[model.selected_part])):
        print('{}({}) {:<16}{} ({})'.format(
            '->' if i == model.selected_choice else '  ',
            '*' if enabled else ' ',
            name if model.selected_part == model.parts[0] else '{}.{}'.format(
                model.selected_part, name),
            doc,
            cls.__name__))
    print()
    for i, part in enumerate(model.parts):
        print('{}({}) {} edit {} message'.format(
            '->' if i == model.selected_choice - len(model.toggles) else '  ',
            '*' if part == model.selected_part else ' ',
            '[Tab]' if i == (model.selected_part_index +
                             1) % len(model.parts) else '     ',
            part))

    print('\n{}[m]ake packer for {} field{}'.format(
        '->' if model.selected_choice == model.choices_num - 2 else '  ',
        model.enabled_num,
        '' if model.enabled_num == 1 else 's'))
    print('{}[q]uit'.format(
        '->' if model.selected_choice == model.choices_num - 1 else '  '))

    print('\n{}'.format(model.status))
    if model.verbose:
        print('last key pressed {}'.format(model.last_key))


def update(model: Model, message: Message, data: Any) -> Tuple[Model, List[Command]]:
    commands = []
    if message == Message.KEY:
        key: str = data
        model.last_key = key

        if key in [ord('q'), ord('Q'), 3]:  # Ctrl+C
            commands.append(Command.QUIT)
        elif key in [ord('j'), ord('J'), 80]:
            model.selected_choice = (
                model.selected_choice + 1) % model.choices_num
        elif key in [ord('k'), ord('K'), 72]:
            model.selected_choice = (
                model.selected_choice - 1) % model.choices_num
        elif key in [ord('m'), ord('M')]:
            commands.append(Command.MAKE)
        elif key in [9]:  # Tab
            model.selected_part = model.parts[(
                model.selected_part_index + 1) % len(model.parts)]

        elif key in [13, 32]:  # Enter, Space
            if model.selected_choice < len(model.toggles):
                model.enabled[model.selected_part][model.selected_choice] = not model.enabled[model.selected_part][model.selected_choice]
            elif model.selected_choice < len(model.toggles) + len(model.parts):
                model.selected_part = model.parts[model.selected_choice - len(
                    model.toggles)]
            elif model.selected_choice == model.choices_num - 2:
                commands.append(Command.MAKE)
            elif model.selected_choice == model.choices_num - 1:
                commands.append(Command.QUIT)
    elif message == Message.STATUS:
        status: str = data
        model.status = status

    return model, commands


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', action='store_true', dest='verbose')
    parser.add_argument('-o', '--output', default='pack_lidia.m')
    args = parser.parse_args()
    model = Model(args.output, args.verbose)
    messages = []
    while True:
        commands = []
        for msg, data in messages:
            mdl, c = update(model, msg, data)
            model = mdl
            commands.extend(c)
            messages.clear()

        for cmd in commands:
            if cmd == Command.QUIT:
                sys.exit(0)
            if cmd == Command.MAKE:
                selected = {p: [f[0] for f, en in zip(
                    model.toggles, model.enabled[p]) if en] for p in model.parts}
                with open(model.output, 'w') as out:
                    codegen(out, model.field_source,
                            selected['main'], selected['trgt'], selected['trim'])
                messages.append(
                    (Message.STATUS, 'Saved to {}'.format(model.output)))

        view(model)
        if len(messages) > 0:
            continue

        key = ord(getch())
        messages.append((Message.KEY, key))


def codegen(out: StringIO, field_source: dict, main_fields: List[str], trgt_fields: List[str], trim_fields: List[str]):
    out.write('function data = pack_lidia( ...\n    ')
    arglist = []
    for f in main_fields:
        if issubclass(field_source[f][2], BaseModel):
            arglist.extend('{}_{}'.format(f, a)
                           for a in field_source[f][2].__fields__)
        else:
            arglist.append(f)
    for f in trgt_fields:
        if issubclass(field_source[f][2], BaseModel):
            arglist.extend('trgt_{}_{}'.format(f, a)
                           for a in field_source[f][2].__fields__)
        else:
            arglist.append('trgt_{}'.format(f))
    for f in trim_fields:
        if issubclass(field_source[f][2], BaseModel):
            arglist.extend('trim_{}_{}'.format(f, a)
                           for a in field_source[f][2].__fields__)
        else:
            arglist.append('trim_{}'.format(f))

    out.write(', ...\n    '.join(arglist))
    out.write(''')
%PACK_LIDIA Pack aircraft data into binary format
%   The output is array of bytes in MsgPack format, as expected by
%   'smol' source of lidia package
%
%   This is generated using pack_maker.py to create code suitable for
%   use in Simulink - known size of I/O, no map or struct usage

    data = [...
''')
    length = 0

    field_count = len(main_fields) + \
        (1 if len(trgt_fields) > 0 else 0) + \
        (1 if len(trim_fields) > 0 else 0)
    length += pack_map(out, field_count)

    for field in main_fields:
        length += pack_field(out, field_source, field, '')

    for fieldgroup, prefix in [(trgt_fields, 'trgt'), (trim_fields, 'trim')]:
        if len(fieldgroup) > 0:
            length += pack_str(out, prefix)
            length += pack_map(out, len(fieldgroup))
            for field in fieldgroup:
                length += pack_field(out, field_source, field, prefix)

    out.write('''    ];
% data length {} bytes
end

function bytes = b(value)
    % reverse byte order to convert from little endian to big endian
    bytes = typecast(swapbytes(value), 'uint8');
end
'''.format(length))


def pack_field(out: StringIO, field_source: dict, field: str, prefix: str) -> int:
    length = 0
    length += pack_str(out, field)
    cls = field_source[field][2]
    if issubclass(cls, VectorModel):
        length += pack_vector(out, field, cls, prefix)
    elif cls is int:
        length += pack_int(out, field if len(prefix) ==
                           0 else '{}_{}'.format(prefix, field))
    else:
        raise NotImplementedError('No code generation for class:', cls)
    return length


def pack_vector(out: StringIO, field: str, cls: VectorModel, prefix: str) -> int:
    length = 0
    length += pack_array(out, len(cls.__fields__))
    for inner in cls.__fields__:
        length += pack_float(out, '{}{}_{}'.format(
            '' if len(prefix) == 0 else (prefix + '_'),
            field, inner), double=(field == 'ned'))  # special case for positional accuracy
    return length


def pack_map(out: StringIO, count: int) -> int:
    if count > 15:
        raise NotImplementedError('only fixmap handled for now')
    out.write('        0x8{:x}, ... % map length {}\n'.format(count, count))
    return 1


def pack_array(out: StringIO, count: int) -> int:
    if count > 15:
        raise NotImplementedError('only fixarray handled for now')
    out.write('        0x9{:x}, ... % array length {}\n'.format(count, count))
    return 1


def pack_str(out: StringIO, data: str) -> int:
    if len(data) > 31:
        raise NotImplementedError('only fixstr handled for now')
    out.write("        0x{:x}, '{}', ... % string length {}\n".format(
        0b10100000 + len(data), data, len(data)))
    return 1 + len(data)


def pack_float(out: StringIO, name: str, double=False) -> int:
    out.write('        0xc{}, b({}({})), ... % {}\n'.format(
        'b' if double else 'a',
        'double' if double else 'single',
        name,
        'double' if double else 'float',
    ))
    return 9 if double else 5


def pack_int(out: StringIO, name: str) -> int:
    out.write(
        '        0xce, b(uint32({})), ... % 32-bit unsigned integer\n'.format(name))
    return 5


if __name__ == '__main__':
    main()
