from defs import OpCode
from instruction import *
from vm import VM
from common_runtime.base_types import *
from parser_like import parse


def main(instructions):
    vm = VM(instructions)
    vm.run()


if __name__ == "__main__":
    main(parse([0x00, 432, 0x40, 0x00, 4, 0x00, 1, 0x10, 0x40, 0x00, "TestString", 0x40, 0x30]))