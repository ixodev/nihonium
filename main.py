from opcodes import OpCode
from instruction import *
from vm import VMRunner
from common_runtime.base_types import *
from parser_like import parse


def main(instructions):
    vm = VMRunner(instructions)
    vm.run()


if __name__ == "__main__":
    main(parse([
        0x00, Int(-43),
        0x40, 0x01,
        0x00, Complex(None, Int(32), Int(32)),
        0x40, 0x02,
        0x41, 0x00,
        0x40, 0x01
    ]))