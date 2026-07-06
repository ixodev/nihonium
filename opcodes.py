import enum


class OpCode(enum.IntEnum):
    PUSH = 0x00
    POP = 0x01
    PEEK = 0x02

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
            case OpCode.PRINT:
                return 1
            case OpCode.READ:
                return 1
            case _:
                return 0
