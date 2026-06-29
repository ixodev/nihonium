import typing


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
