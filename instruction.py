import typing

from common_runtime.base_types import Object
from opcodes import OpCode
from frame import Locals, Stack, Registers
from io_streams import IO


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

    def _exec(self, locals: Locals, registers: Registers, stack: Stack, instr_ptr: int):
        pass

    def exec(self, locals: Locals, registers: Registers, stack: Stack, instr_ptr: int):
        return self._exec(locals, registers, stack, instr_ptr)


@register(OpCode.PUSH)
class Push(Instruction):
    def __init__(self, operand: typing.Optional[Object]):
        super().__init__(OpCode.PUSH, operand)

    def _exec(self, locals: Locals, registers: Registers, stack: Stack, instr_ptr: int):
        stack.push(self.operand)
        return InstructionResults(None)


@register(OpCode.POP)
class Pop(Instruction):
    def __init__(self):
        super().__init__(OpCode.POP)

    def _exec(self, locals: Locals, registers: Registers, stack: Stack, instr_ptr: int):
        stack.pop()
        return InstructionResults(None)

@register(OpCode.PEEK)
class Peek(Instruction):
    def __init__(self):
        super().__init__(OpCode.PEEK)

    def _exec(self, locals: Locals, registers: Registers, stack: Stack, instr_ptr: int):
        return InstructionResults


@register(OpCode.PRINT)
class Print(Instruction):
    def __init__(self, fd: int):
        super().__init__(OpCode.PRINT)
        self.fd = fd

    def _exec(self, locals: Locals, registers: Registers, stack: Stack, instr_ptr: int):
        IO.write(self.fd, stack.peek())
        stack.pop()
        return InstructionResults(None)


@register(OpCode.READ)
class Read(Instruction):
    def __init__(self, fd: int):
        super().__init__(OpCode.READ)
        self.fd = fd

    def _exec(self, locals: Locals, registers: Registers, stack: Stack, instr_ptr: int):
        stack.push(IO.read(self.fd))
        return InstructionResults(None)


@register(OpCode.HALT)
class Halt(Instruction):
    def __init__(self):
        super().__init__(OpCode.HALT)

    def _exec(self, locals: Locals, registers: Registers, stack: Stack, instr_ptr: int):
        return InstructionResults(None, False)


@register(OpCode.ADD)
class Add(Instruction):
    def __init__(self):
        super().__init__(OpCode.ADD)

    def _exec(self, locals: Locals, registers: Registers, stack: Stack, instr_ptr: int):
        stack.push(stack.pop() + stack.pop())
        return InstructionResults(None)


@register(OpCode.SUB)
class Sub(Instruction):
    def __init__(self):
        super().__init__(OpCode.SUB)

    def _exec(self, locals: Locals, registers: Registers, stack: Stack, instr_ptr: int):
        stack.push(stack.pop() - stack.pop())
        return InstructionResults(None)


@register(OpCode.MUL)
class Mul(Instruction):
    def __init__(self):
        super().__init__(OpCode.MUL)

    def _exec(self, locals: Locals, registers: Registers, stack: Stack, instr_ptr: int):
        stack.push(stack.pop() * stack.pop())
        return InstructionResults(None)


@register(OpCode.DIV)
class Div(Instruction):
    def __init__(self):
        super().__init__(OpCode.DIV)

    def _exec(self, locals: Locals, registers: Registers, stack: Stack, instr_ptr: int):
        stack.push(stack.pop() / stack.pop())
        return InstructionResults(None)


@register(OpCode.LOAD)
class Load(Instruction):
    def __init__(self, address: int):
        super().__init__(OpCode.LOAD)
        self.address = address

    def _exec(self, locals: Locals, registers: Registers, stack: Stack, instr_ptr: int):
        stack.push(locals.load(self.address))
        return InstructionResults(None)


@register(OpCode.STORE)
class Store(Instruction):
    def __init__(self, address):
        super().__init__(OpCode.STORE)
        self.address = address

    def _exec(self, locals: Locals, registers: Registers, stack: Stack, instr_ptr: int):
        locals.store(self.address, stack.peek())
        stack.pop()
        return InstructionResults(None)


@register(OpCode.MOV)
class Mov(Instruction):
    def __init__(self, src: int, dst: int):
        super().__init__(OpCode.MOV)
        self.src = src
        self.dst = dst

    def _exec(self, locals: Locals, registers: Registers, stack: Stack, instr_ptr: int):
        registers.mov(self.src, self.dst)
        return InstructionResults(None)

