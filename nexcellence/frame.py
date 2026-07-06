import typing

LOCALS_SIZE = 200
N_REGISTERS = 8


class Stack:
    def __init__(self):
        self.stack = []

    def push(self, value: typing.Any):
        self.stack.append(value)

    def pop(self):

        if len(self.stack) > 0:
            return self.stack.pop(-1)

        raise Exception("Stack is empty")

    def peek(self):

        if len(self.stack) > 0:
            return self.stack[-1]

        raise Exception("Stack is empty")

    def empty(self):
        return len(self.stack) == 0

    def size(self):
        return len(self.stack)

    def clear(self):
        self.stack.clear()


class Locals:
    def __init__(self):
        self.locals = [0] * LOCALS_SIZE
        self.occupied_places = [False] * LOCALS_SIZE

    def load(self, address: int):
        if address < 0 or address >= len(self.locals):
            raise RuntimeError("Invalid local address")
        return self.locals[address]

    def store(self, address: int, value):
        if address < 0 or address >= len(self.locals):
            raise RuntimeError("Invalid local address")

        self.locals[address] = value
        self.occupied_places[address] = True

    def is_occupied(self, address: int):
        return self.occupied_places[address]

    def free(self, address: int):
        if address < 0 or address >= len(self.locals):
            raise RuntimeError("Invalid local address")

        if not self.is_occupied(address):
            raise RuntimeError("Cannot free address which was not occupied")

        value = self.locals[address]

        self.locals[address] = 0
        self.occupied_places[address] = False

        return value

    def available_size(self):
        return len(self.locals)


    # LATER
    def _ensure_size(self, addr):
        if addr >= len(self.locals):
            new_size = len(self.locals) * 2
            while new_size <= addr:
                new_size *= 2
            self.locals.extend([0] * (new_size - len(self.locals)))


class Registers:
    def __init__(self):
        self.registers = [0] * N_REGISTERS

    def mov(self, src: int, dst: int):
        self.registers[dst] = self.registers[src]

    def put(self, dst: int, value: typing.Any):
        self.registers[dst] = value

    def clean(self):
        self.registers.clear()
