import typing

from common_runtime.base_types import Object
from defs import OpCode
from stack import Stack


INSTRUCTION_REGISTRY = {}

def register(opcode):
    def wrapper(cls):
        INSTRUCTION_REGISTRY[opcode] = cls
        return cls
    return wrapper



class InstructionResults(typing.NamedTuple):
    result: typing.Any
    is_running: bool = True
    object_return: typing.Optional[Object] = None


class Instruction:
    def __init__(self, op: OpCode, operand: typing.Optional[Object] = None):
        self.op = op
        self.operand = operand

    def _exec(self, stack: Stack, instr_ptr: typing.Optional[int]):
        pass

    def exec(self, stack: Stack, instr_ptr: int):
        return self._exec(stack, instr_ptr)


@register(OpCode.PUSH)
class Push(Instruction):
    def __init__(self, operand: typing.Optional[Object]):
        super().__init__(OpCode.PUSH, operand)

    def _exec(self, stack: Stack, instr_ptr: int):
        stack.push(self.operand)
        return InstructionResults(None)

@register(OpCode.POP)
class Pop(Instruction):
    def __init__(self, operand: typing.Optional[Object]):
        super().__init__(OpCode.POP, operand)

    def _exec(self, stack: Stack, instr_ptr: int):
        stack.pop()
        return InstructionResults(None)

@register(OpCode.PRINT)
class Print(Instruction):
    def __init__(self):
        super().__init__(OpCode.PRINT)

    def _exec(self, stack: Stack, instr_ptr: int):
        print(stack.peek())
        stack.pop()
        return InstructionResults(None)

@register(OpCode.HALT)
class Halt(Instruction):
    def __init__(self):
        super().__init__(OpCode.HALT)

    def _exec(self, stack: Stack, instr_ptr: int):
        return InstructionResults(None, False)

@register(OpCode.ADD)
class Add(Instruction):
    def __init__(self):
        super().__init__(OpCode.ADD)

    def _exec(self, stack: Stack, instr_ptr: int):
        stack.push(stack.pop() + stack.pop())
        return InstructionResults(None)

@register(OpCode.SUB)
class Sub(Instruction):
    def __init__(self):
        super().__init__(OpCode.SUB)

    def _exec(self, stack: Stack, instr_ptr: int):
        stack.push(stack.pop() - stack.pop())
        return InstructionResults(None)

@register(OpCode.MUL)
class Mul(Instruction):
    def __init__(self):
        super().__init__(OpCode.MUL)

    def _exec(self, stack: Stack, instr_ptr: int):
        stack.push(stack.pop() * stack.pop())
        return InstructionResults(None)

@register(OpCode.DIV)
class Div(Instruction):
    def __init__(self):
        super().__init__(OpCode.DIV)

    def _exec(self, stack: Stack, instr_ptr: int):
        stack.push(stack.pop() / stack.pop())
        return InstructionResults(None)

