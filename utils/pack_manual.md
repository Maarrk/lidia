# Packet format for smol input

This is a description of an example packet for `smol` source serialized with [MessagePack](https://msgpack.org/).

**All multi-byte numbers are big-endian**

Names of variables correspond to `src/lidia/aircraft.py` module.

| Index<br>(inclusive) | Type   | Value                                                | Description                |
| -------------------- | ------ | ---------------------------------------------------- | -------------------------- |
| 0                    | const  | 0x87                                                 | Map with 7 key-value pairs |
| 1-6                  | const  | 0xA3, 0x6E, 0x65, 0x64, 0x93, 0xCB                   | `ned` start                |
| 7-14                 | double | `ned.n`                                              |                            |
| 15                   | const  | 0xCB                                                 | Next value is double       |
| 16-23                | double | `ned.e`                                              |                            |
| 24                   | const  | 0xCB                                                 |                            |
| 25-32                | double | `ned.d`                                              |                            |
| 33-38                | const  | 0xA3, 0x61, 0x74, 0x74, 0x93, 0xCA                   | `att` start                |
| 39-42                | float  | `att.roll`                                           |                            |
| 43                   | const  | 0xCA                                                 | Next value is float        |
| 44-47                | float  | `att.pitch`                                          |                            |
| 48                   | const  | 0xCA                                                 |                            |
| 49-52                | float  | `att.yaw`                                            |                            |
| 53-61                | const  | 0xA6, 0x76, 0x5F, 0x62, 0x6F, 0x64, 0x79, 0x93, 0xCA | `v_body` start             |
| 62-65                | float  | `v_body.x`                                           |                            |
| 66                   | const  | 0xCA                                                 |                            |
| 67-70                | float  | `v_body.y`                                           |                            |
| 71                   | const  | 0xCA                                                 |                            |
| 72-75                | float  | `v_body.z`                                           |                            |
| 76-83                | const  | 0xA5, 0x76, 0x5F, 0x6E, 0x65, 0x64, 0x93, 0xCA       | `v_ned` start              |
| 84-87                | float  | `v_ned.n`                                            |                            |
| 88                   | const  | 0xCA                                                 |                            |
| 89-92                | float  | `v_ned.e`                                            |                            |
| 93                   | const  | 0xCA                                                 |                            |
| 94-97                | float  | `v_ned.d`                                            |                            |
| 98-104               | const  | 0xA4, 0x63, 0x74, 0x72, 0x6C, 0x95, 0xCA             | `ctrl` start               |
| 105-108              | float  | `ctrl.stick_right`                                   |                            |
| 109                  | const  | 0xCA                                                 |                            |
| 110-113              | float  | `ctrl.stick_pull`                                    |                            |
| 114                  | const  | 0xCA                                                 |                            |
| 115-118              | float  | `ctrl.throttle`                                      |                            |
| 119                  | const  | 0xCA                                                 |                            |
| 120-123              | float  | `ctrl.pedals_right`                                  |                            |
| 124                  | const  | 0xCA                                                 |                            |
| 125-128              | float  | `ctrl.collective_up`                                 |                            |
| 129-135              | const  | 0xA4, 0x74, 0x72, 0x67, 0x74, 0x95, 0xCA             | `trgt` start               |
| 136-139              | float  | `trgt.stick_right`                                   |                            |
| 140                  | const  | 0xCA                                                 |                            |
| 141-144              | float  | `trgt.stick_pull`                                    |                            |
| 145                  | const  | 0xCA                                                 |                            |
| 146-149              | float  | `trgt.throttle`                                      |                            |
| 150                  | const  | 0xCA                                                 |                            |
| 151-154              | float  | `trgt.pedals_right`                                  |                            |
| 155                  | const  | 0xCA                                                 |                            |
| 156-159              | float  | `trgt.collective_up`                                 |                            |
| 160-167              | const  | 0xA6, 0x74, 0x5F, 0x62, 0x6F, 0x6F, 0x74, 0xCE       | `t_boot` start             |
| 168-171              | int32  | `t_boot`                                             |                            |
