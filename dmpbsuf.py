import datareader
import os

"""
Tool for unpacking a solaredge .bsuf firmware update file.

Author: Willem Hengeveld <itsme@xs4all.nl>

see https://github.com/nlitsme/solaredge-bsuf

"""

def copyfile(ifh, ofh):
    """
    copy all data from one to another filehandle
    """
    while True:
        data = ifh.read(0x10000, throw=False)
        if not data:
            break
        ofh.write(data)

def saveunique(savedir, prefix, fh):
    """
    save data from filehandle to a unique file, starting with 'prefix'
    """
    for i in range(100):
        fn = f"{savedir}/{prefix}-{i:03d}.dat"
        if not os.path.exists(fn):
            break
    self.fh.seek(0)
    with open(fn, "wb") as ofh:
        copyfile(self.fh, ofh)

def savefirmware(savedir, fwtype, version, fh):
    """
    save firmware from filehandle 'fh' to a file with 'fwtype' and the specified version.
    """
    filename = f"{savedir}/fw{fwtype:04x}-{version[0]}.{version[1]}.{version[2]}.bin"
    if os.path.exists(filename):
        print("already saved")
        return
    with open(filename, "wb") as ofh:
        copyfile(fh, ofh)


class FirmwareType3:
    """
    The main arm binary of the firmware,
    there may be several different main binaries,
    With support for different inverters.
    """
    def __init__(self, fh):
        self.zero = fh.read32le()
        self.checksum = fh.read16le()
        self.zero2 = fh.read16le()
        self.imagesize = fh.read32le()
        self.version = (fh.reads16le(), fh.reads16le())
        self.data = fh.read(128)

    def dump(self):
        print(f"fw: z:{self.zero},{self.zero2} c:{self.checksum:04x} s:{self.imagesize:08x} v:{str(self.version)}  {self.data.hex()}")

class EntryType3Firmware:
    """
    the 'old' firmware entry, with only one version field.
    """
    def __init__(self, fh):
        self.fwtype = fh.read16le()
        self.version = tuple(fh.reads16le() for _ in range(3))

        self.fwfh = fh.subreader()

    def dump(self):
        print(f"t{self.fwtype:04x} v{str(self.version)}")

        if self.fwtype == 0x300:
            self.fwfh.seek(0)
            fw = FirmwareType3(self.fwfh)
            fw.dump()
        else:
            self.fwfh.seek(0)
            print("fwdata    ", self.fwfh.read(128).hex())

    def save(self, savedir):
        if self.fwtype == 0x300:
            self.fwfh.seek(0x10)
            savefirmware(savedir, self.fwtype, self.version, self.fwfh)
        else:
            self.fwfh.seek(0)
            savefirmware(savedir, self.fwtype, self.version, self.fwfh)



class EntryType6Firmware:
    """
    fwtype
    0300  - cpu firmware: arm
    0d00, 0e00, 1900 - dsp 2 firmware
    0200, 0800, 1400, 1800 - dsp 1 firmware
    """
    def __init__(self, fh):
        self.fwtype = fh.read16le()
        self.version1 = tuple(fh.reads16le() for _ in range(3))
        self.version2 = tuple(fh.reads16le() for _ in range(3))
        self.version3 = tuple(fh.reads16le() for _ in range(3))

        self.fwfh = fh.subreader()

    def dump(self):
        print(f"t{self.fwtype:04x} v{str(self.version1):<16} v{str(self.version2):<16} v{str(self.version3):<16}")

        if self.fwtype == 0x300:
            self.fwfh.seek(0)
            fw = FirmwareType3(self.fwfh)
            fw.dump()
        else:
            self.fwfh.seek(0)
            print("fwdata    ", self.fwfh.read(128).hex())

    def save(self, savedir):
        if self.fwtype == 0x300:
            self.fwfh.seek(0x10)
            savefirmware(savedir, self.fwtype, self.version1, self.fwfh)
        else:
            self.fwfh.seek(0)
            savefirmware(savedir, self.fwtype, self.version1, self.fwfh)


class EntryType0:
    """
     02 16 08 01 ff ff ff ff
     fd 16 07 13 ff ff ff ff
     fe 16 07 21 ff ff ff ff
     ff 10 01 08 ff ff ff ff
     ff 16 02 11 ff ff ff ff
     ff 16 03 25 ff ff ff ff
     ff 16 04 25 ff ff ff ff
     ff 17 06 28 ff ff ff ff
    """
    def __init__(self, fh):
        self.payload = fh.read()
    def dump(self):
        print("T0", self.payload.hex())

    def save(self, savedir): pass

class EntryType1:
    """
     5c 03 c8 01
     fd ff ff ff
     fc ff ff ff
     a6 03 01 00
     b8 0b 04 00
     41 54 2b 51 43 46 47 3d 22 6e 77 73 63 61 6e 6d 6f 64 65 22 2c 33 2c 31 0d 00
     88 13 00 00
    """
    def __init__(self, fh):
        self.payload = fh.read()
    def dump(self):
        print("T1", self.payload.hex())
    def save(self, savedir): pass

class EntryType7:
    """
     00 02 7e 02 f4 01 00 00 -- int:500
     00 03 6a 03 e4 0c 00 00 -- int:3300
    
     00 02 f2 01 00 00 48 42 -- float:50.0
     00 03 4c 03 00 00 c0 40 -- float:6.0
     00 03 6a 03 00 40 4e 45 -- float:3300.0
     00 03 77 03 00 00 80 3f -- float:1.0
    
     00 03 70 03 00 00 00 00 70 72 6f 64 32 2e 73 6f 6c 61 72 65 64 67 65 2e 63 6f 6d 00
    """
    def __init__(self, fh):
        self.payload = fh.read()
    def dump(self):
        print("T7", self.payload.hex())
    def save(self, savedir): pass

class EntryType13:
    """
    contains .tar archive wiht stthc.bhx and stpod_master.bhx
    """
    def __init__(self, fh):
        self.fh = fh
    def dump(self):
        pass
    def save(self, savedir):
        saveunique(savedir, "t13", self.fh)

class EntryType14:
    """ 0x0000ea60 = 60000 """
    def __init__(self, fh):
        self.payload = fh.read()
    def dump(self):
        print("T14", self.payload.hex())
    def save(self, savedir): pass

class EntryType15:
    """
     00 01 64 00 00 00
     01 00 00 00 00 00
    """
    def __init__(self, fh):
        self.payload = fh.read()
    def dump(self):
        print("T15", self.payload.hex())
    def save(self, savedir): pass

class EntryType20:
    """
    arm thumb binary
    """
    def __init__(self, fh):
        self.fh = fh
    def dump(self): pass

    def save(self, savedir):
        saveunique(savedir, "t20", self.fh)

class EntryType21:
    """
     00 00 00 00 c1 00 01 00 00 00 00 00
     01 00 00 00 79 03 01 00 01 00 00 00
     01 00 01 00 30 00 01 00 01 00 00 00
     03 00 ff ff ff ff 00 00
    """
    def __init__(self, fh):
        self.payload = fh.read()
    def dump(self):
        print("T21", self.payload.hex())
    def save(self, savedir): pass

class EntryUnknown:
    def __init__(self, type, fh):
        self.type = type
        self.payload = fh.read()

    def dump(self):
        print(f"UNK{self.type}", self.payload.hex())
    def save(self, savedir): pass


class BsufEntry:
    """
    Represent One entry in a .bsuf file.
    """
    def __init__(self, fh):
        self.size = fh.read32le()
        self.type = fh.read16le()
        self.ofs = fh.tell()

        self.entfh = fh.subreader(self.size)

        fh.skip(self.size)
        self.checksum = fh.read16le()


class BsufFile:
    """
    Analyze a .bsuf file.

    In the constructor, all entries are identified.
    """
    def __init__(self, fh):
        magic = fh.read64le()
        if magic != 0x663919145fab6655:
            raise Exception("invalid header magic")
        self.version = fh.read32le()
        filesize = fh.read32le()

        if filesize+0x12 != fh.size():
            print(f"WARNING: unexpected filesize stored:{filesize:08x} != real:{fh.size():08x}")

        self.entries = []

        while fh.tell() < filesize+0x10:
            self.entries.append(BsufEntry(fh))

        self.filechecksum = fh.read16le()

    def enumentries(self):
        for ent in self.entries:
            ent.entfh.seek(0)
            match ent.type:
                case 0: obj = EntryType0(ent.entfh)
                case 1: obj = EntryType1(ent.entfh)
                case 3: obj = EntryType3Firmware(ent.entfh)
                case 6: obj = EntryType6Firmware(ent.entfh)
                case 7: obj = EntryType7(ent.entfh)
                case 13: obj = EntryType13(ent.entfh)
                case 14: obj = EntryType14(ent.entfh)
                case 15: obj = EntryType15(ent.entfh)
                case 20: obj = EntryType20(ent.entfh)
                case 21: obj = EntryType21(ent.entfh)
                case _: obj = EntryUnknown(ent.type, ent.entfh)

            obj.ent = ent

            yield obj


    def dump(self):
        print(f"file v{self.version:08x} c:{self.filechecksum:04x}")

        for obj in self.enumentries():
            print(f"ENT  {obj.ent.size:08x} t{obj.ent.type:04x} c:{obj.ent.checksum:04x}  @{obj.ent.ofs:08x}")

            obj.dump()

    def save(self, savedir):
        for obj in self.enumentries():
            obj.save(savedir)

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Decode SolarEdge .bsuf firmware file')
    parser.add_argument('--debug', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('--savedir', '-d', type=str, help='extract firmware to the specified directory')
    parser.add_argument('files', nargs='*')
    args = parser.parse_args()

    for fn in args.files:
        try:
            print("==>", fn, "<==")
            with open(fn, "rb") as fh:
                fh = datareader.new(fh)

                f = BsufFile(fh)
                if args.savedir:
                    f.save(args.savedir)
                else:
                    f.dump()

        except Exception as e:
            print("ERROR:", e)
            if args.debug:
                raise

if __name__=='__main__':
    main()
