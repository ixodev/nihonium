import typing

from .instruction import Instruction
from .frame import Locals, Stack, Registers
from .io_streams import IO


class VM:
    def __init__(self, instructions: typing.List[Instruction]):
        self.instructions = instructions

        self.stack = Stack()
        self.locals = Locals()
        self.registers = Registers()

        IO.open_standard_streams()

        self.instr_ptr = 0

        self.is_running = True

    def run(self):

        while self.instr_ptr < len(self.instructions) and self.is_running:

            instruction = self.instructions[self.instr_ptr]

            self.is_running = instruction.exec(self.locals, self.registers, self.stack, self.instr_ptr).is_running

            self.instr_ptr += 1

            #print(self.locals.locals)

        self.stack.clear()