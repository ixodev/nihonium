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

    @property
    def stride(self) -> int:
        match self:
            case OpCode.PUSH:
                return 1
            case OpCode.POP:
                return 1
            case OpCode.JUMP:
                return 1
            case _:
                return 0
