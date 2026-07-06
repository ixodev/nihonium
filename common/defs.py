import enum


class OpCode(enum.IntEnum):
    PUSH = 0x00
    POP = 0x01

    ADD = 0x10
    SUB = 0x11
    MUL = 0x12
    DIV = 0x13

    EQ = 0x20
    NE = 0x21

    HALT = 0x30
    JUMP = 0x31

    PRINT = 0x40
    READ = 0x41
    OPEN = 0x42
    CLOSE = 0x43

    STORE = 0x50
    LOAD = 0x51
    MOV = 0x52

    @property
    def stride(self):
        match self:
            case OpCode.PUSH:
                return 1
            case OpCode.JUMP:
                return 1
            case OpCode.STORE:
                return 1
            case OpCode.LOAD:
                return 1
            case OpCode.MOV:
                return 2
            case OpCode.OPEN:
                return 1
            case _:
                return 0


class FileMode(enum.IntEnum):
    READ = 1
    WRITE = 2
    APP = 4
    BIN = 8

    @property
    def mode_str(self):
        match self:
            case FileMode.READ:
                return "r"
            case FileMode.WRITE:
                return "w"
            case FileMode.APP:
                return "a"
            case FileMode.BIN:
                return "b"
            case _:
                return ""


class StreamType(enum.IntEnum):
    STDIN = 0
    STDOUT = 1
    STDERR = 2
    FILE = 3
    SOCKET = 4