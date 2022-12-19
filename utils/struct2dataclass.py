import json
from typing import Dict, List, Tuple


def main():
    parsed: dict = json.load(open('net_fdm.json', 'rb'))
    constants, fields = get_fields(parsed)
    described_fields = get_descriptions(fields)
    write_dataclass(constants, described_fields)


def get_fields(parsed: dict) -> Tuple[Dict[str, int], List[Tuple[str, str, int]]]:
    constants = {
        'FG_NET_FDM_VERSION': int(parsed['namespace']['variables'][0]['value']['tokens'][0]['value'])
    }
    enum_constants = parsed['namespace']['classes'][0]['enums'][0]['values']
    for ec in enum_constants:
        constants[ec['name']] = int(ec['value']['tokens'][0]['value'])

    fields = []
    class_fields = parsed['namespace']['classes'][0]['fields']
    for field in class_fields:
        name = field['name']
        typename = ''
        count = 1
        if 'size' in field['type']:
            typename = field['type']['array_of']['typename']['segments'][0]['name']
            count = constants[field['type']['size']['tokens'][0]['value']]
        else:
            typename = field['type']['typename']['segments'][0]['name']
        fields.append((name, typename, count))

    # print(f'{constants=}')
    # print(f'{fields=}')
    return constants, fields


def get_descriptions(fields: List[Tuple[str, str, int]]) -> List[Tuple[str, str, int, str]]:
    lines = []
    with open('net_fdm.hxx') as file:
        lines = file.readlines()

    result = []
    line_idx = 0
    for name, typename, count in fields:
        prefix = f'{typename} {name}'
        while not lines[line_idx].strip().startswith(prefix):
            line_idx += 1
        line = lines[line_idx].strip()
        comment = (line + '// ').split('// ')[1]
        result.append((name, typename, count, comment))

    # print(f'{result=}')
    return result


def write_dataclass(constants: Dict[str, int], described_fields: List[Tuple[str, str, int, str]]):
    python_types = {
        'uint32_t': 'int',
        'int32_t': 'int',
        'double': 'float',
        'float': 'float'
    }
    print(f'''
FG_NET_FDM_VERSION = {constants['FG_NET_FDM_VERSION']}


class FGNetFDM(BaseModel):
    """FlightGear network communication structure from src/Network/net_fdm.hxx"""''')
    for name, typename, count, comment in described_fields:
        print(f'    {name}: ', end='')
        pt = python_types[typename]
        if count == 1:
            print(f'{pt} = 0')
        else:
            print(
                f'Tuple[{", ".join([pt] * count)}] = ({", ".join(["0" for i in range(count)])})')
        if comment != '':
            print(f'    """{comment}"""')

    format_types = {
        'uint32_t': 'I',
        'int32_t': 'i',
        'double': 'd',
        'float': 'f'
    }
    struct_format = []
    for _, typename, count, _ in described_fields:
        pt = format_types[typename]
        struct_format.append(pt * count)

    print("""

    @classmethod
    def from_bytes(cls, data):
        version = unpack_from("!I", data)[0]
        if version != FG_NET_FDM_VERSION:
            raise ValueError(f"Expected protocol version {FG_NET_FDM_VERSION}, got {version}")
        this = cls()
        decoded = unpack_from(""", end='')
    print(f'"!{"".join(struct_format)}", data)')

    i = 0
    for name, _, count, _ in described_fields:
        print(f'        this.{name} = decoded', end='')
        if count == 1:
            print(f'[{i}]')
        else:
            print(f'[{i}:{i + count}]')
        i += count
    print('        return this\n')


if __name__ == '__main__':
    main()
