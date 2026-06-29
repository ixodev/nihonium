import typing

from defs import OpCode
from instruction import *


def parse(bytecode: list[int]):
    instructions = []
    ip = 0

    while ip < len(bytecode):
        opcode = OpCode(bytecode[ip])
        ip += 1

        stride = opcode.stride

        operands = bytecode[ip:ip + stride]
        ip += stride

        instr_cls = INSTRUCTION_REGISTRY[opcode]

        instr = instr_cls(*operands)

        instructions.append(instr)

    return instructions