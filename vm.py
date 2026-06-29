import typing

from instruction import Instruction
from stack import Stack


class VM:
    def __init__(self, instructions: typing.List[Instruction]):
        self.instructions = instructions

        self.stack = Stack()
        self.instr_ptr = 0

        self.is_running = True

    def run(self):
        while self.instr_ptr < len(self.instructions) and self.is_running:
            instruction = self.instructions[self.instr_ptr]

            self.is_running = instruction.exec(self.stack, self.instr_ptr).is_running

            self.instr_ptr += 1
