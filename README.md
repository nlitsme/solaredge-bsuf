# SolarEdge firmware

solaredge firmware comes in files with a `.bsuf` extension.

The layout is as follows:

| ofs  | type  | description
| ---- | ----- | --------------
| +00  | u64   | magic number: 0x663919145fab6655
| +08  | u32   | version
| +0c  | u32   | payload size
| +10  | entry | ...
| ...  | ...   | ...
| end-2 | u16  | crc-16

Each entry has this format:


| ofs  | type  | description
| ---- | ----- | --------------
| +00  | u32   | data size
| +04  | u16   | the entry type
| +06  | u8[]  | the entry data
| ...  | ...   | ...
| end-2 | u16  | crc-16


Overview of entry types.

| type | description
| ---- | ------------
| 0x00 | 2 dwords
| 0x01 | 6 dwords + config string, 
| 0x03 | firmware with 1 version
| 0x06 | firmware with 3 version fields
| 0x07 | properties
| 0x0d | large binary, some are .tar files.
| 0x0e | 1 dword
| 0x0f | 6 bytes
| 0x14 | arm binary
| 0x15 | 8 or 12 bytes


Overview of firmware types

| type | description
| ---- | ------------
| 0x03 | main ARM cpu firmware
| 0x0d | DSP2 firmware
| 0x0e | DSP2 firmware
| 0x19 | DSP2 firmware
| 0x02 | DSP1 firmware
| 0x08 | DSP1 firmware
| 0x14 | DSP1 firmware
| 0x18 | DSP1 firmware


# The firmware files

## arm

the binaries with v3.x are all arm code.

## dsp

the binaries with v1.x and v2.x are mostly for the DSPs.

## t20

these contain arm code.


## t13

several t13 blocks are a .tar file, containing:

 * `stpod_master.bhx`
 * `stthc.bhx`


# protocol
