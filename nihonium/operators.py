import sys
from typing import Any
from .defs import *
from .error import *
from .base_types import Int, Bool



class Operator:

    unary_operators = {
        TOKEN_TYPE_PLUS: lambda x: x,
        TOKEN_TYPE_MINUS: lambda x: -x,
        TOKEN_TYPE_NOT: lambda x: x.lognot(),
        TOKEN_TYPE_REV: lambda x: ~x,
        TOKEN_TYPE_SIZEOF: lambda x: Int(sys.getsizeof(x))
    }

    binary_operators = {
        TOKEN_TYPE_PLUS: lambda x, y: x + y,
        TOKEN_TYPE_MINUS: lambda x, y: x - y,
        TOKEN_TYPE_STAR: lambda x, y: x * y,
        TOKEN_TYPE_SLASH: lambda x, y: x / y,
        TOKEN_TYPE_DOUBLE_SLASH: lambda x, y: x // y,
        TOKEN_TYPE_DOUBLE_STAR: lambda x, y: x ** y,
        TOKEN_TYPE_MOD: lambda x, y: x % y,
        TOKEN_TYPE_AND: lambda x, y: x & y,
        TOKEN_TYPE_OR: lambda x, y: x | y,
        TOKEN_TYPE_XOR: lambda x, y: x ^ y,
        TOKEN_TYPE_LOGICAL_AND: lambda x, y: x.logand(y),
        TOKEN_TYPE_LOGICAL_OR: lambda x, y: x.logor(y),
        TOKEN_TYPE_EQUALITY: lambda x, y: Bool(x == y),
        TOKEN_TYPE_RIGHTSHIFT: lambda x, y: x >> y,
        TOKEN_TYPE_LEFTSHIFT: lambda x, y: x << y,
        TOKEN_TYPE_GREATER: lambda  x, y: x > y,
        TOKEN_TYPE_SMALLER: lambda x, y: x < y,
        TOKEN_TYPE_GREATER_EQ: lambda x, y: x >= y,
        TOKEN_TYPE_SMALLER_EQ: lambda x, y: x <= y,
        TOKEN_TYPE_INEQUALITY: lambda x, y: Bool(x != y),
        TOKEN_TYPE_REFERENCE: lambda x, y: x.reference_equals(y)
    }

    def __init__(self, op: str):
        self.op = op

    def __call__(self, x: Any, y: Any = None):

        if not self.op in Operator.unary_operators and not self.op in Operator.binary_operators:
            error(f"{self.op} => unknown operator")

        try:
            if y is None:
                return Operator.unary_operators[self.op](x)
            return Operator.binary_operators[self.op](x, y)
        except:
            raise

    def __repr__(self):
        return f"{self.op} operator"
