import types
from typing import *
from .statements import *
from .base_types import *
from .defs import *


class Function(CallableObject):
    def __init__(self, name: str, parameters, body: List[Statement]):
        super().__init__()

        self.name = name
        self.parameters = parameters
        self.body = body

    def call(self, program, scope_variables):
        for statement in self.body:
            result, function_finished = statement(program, scope_variables)

            if function_finished:
                return result

        return Null()

    def __repr__(self):
        return f"(<Nihonium Function {self.name}>)"


class NativeFunction(CallableObject):
    def __init__(self, symbol: types.FunctionType, allowed_modules: Optional[List[str]], export_for_all: bool=False):
        super().__init__()

        self.symbol = symbol
        self._allowed_modules = allowed_modules
        self._export_for_all = export_for_all

    def is_module_allowed(self, client_module_name: str):

        if self._export_for_all:
            return True

        return client_module_name in self._allowed_modules

    def __call__(self, *args, **kwargs):
        return self.call(*args, **kwargs)

    def call(self, *args, **kwargs):
        return self.symbol(*args, **kwargs)

    def ast_repr(self):
        return self.__repr__()

    def __repr__(self):
        return f"(<Nihonium native function {self.symbol}>)"


class LambdaFunction(CallableObject):
    def __init__(self, parameters: List[str], expression: Expression):
        super().__init__()

        self.parameters = parameters
        self.expression = expression

    def call(self, program, scope_variables):
        return self.expression.eval(program, scope_variables)

    def _ast_inject_binop(self, op: str, other: Object, reverse: bool = False):
        from .expressions import BinaryExpression, VariableExpression

        args = [VariableExpression("", [Token(TOKEN_TYPE_IDENT, name)]) for name in self.parameters]

        left = self.expression

        if other.is_lambda_function():
            right = other.expression if isinstance(other, LambdaFunction) else other

            if self.get_num_parameters() != other.get_num_parameters():
                error(f"lambda functions {self} and {other} when applying {op} operator not dimensionally fitting")

        else:
            right = other

        if reverse:
            left, right = right, left

        return LambdaFunction(self.parameters, BinaryExpression("", left, right, op))


    def _ast_inject_unop(self, op: str):
        from expressions import UnaryExpression

        return LambdaFunction(self.parameters, UnaryExpression("", self.expression, op))

    def __add__(self, other):
        return self._ast_inject_binop(TOKEN_TYPE_PLUS, other)

    def __radd__(self, other):
        return self._ast_inject_binop(TOKEN_TYPE_PLUS, other, reverse=True)

    def __mul__(self, other):
        return self._ast_inject_binop(TOKEN_TYPE_STAR, other)

    def __rmul__(self, other):
        return self._ast_inject_binop(TOKEN_TYPE_STAR, other, reverse=True)

    def __sub__(self, other):
        return self._ast_inject_binop(TOKEN_TYPE_MINUS, other)

    def __rsub__(self, other):
        return self._ast_inject_binop(TOKEN_TYPE_MINUS, other, reverse=True)

    def __truediv__(self, other):
        return self._ast_inject_binop(TOKEN_TYPE_SLASH, other)

    def __rtruediv__(self, other):
        return self._ast_inject_binop(TOKEN_TYPE_SLASH, other, reverse=True)

    def __floordiv__(self, other):
        return self._ast_inject_binop(TOKEN_TYPE_DOUBLE_SLASH, other)

    def __rfloordiv__(self, other):
        return self._ast_inject_binop(TOKEN_TYPE_DOUBLE_SLASH, other, reverse=True)

    def __mod__(self, other):
        return self._ast_inject_binop(TOKEN_TYPE_MOD, other)

    def __rmod__(self, other):
        return self._ast_inject_binop(TOKEN_TYPE_MOD, other, reverse=True)

    def __pow__(self, other):
        return self._ast_inject_binop(TOKEN_TYPE_DOUBLE_STAR, other)

    def __rpow__(self, other):
        return self._ast_inject_binop(TOKEN_TYPE_DOUBLE_STAR, other, reverse=True)

    def __lshift__(self, other):
        return self._ast_inject_binop(TOKEN_TYPE_LEFTSHIFT, other)

    def __rlshift__(self, other):
        return self._ast_inject_binop(TOKEN_TYPE_LEFTSHIFT, other, reverse=True)

    def __rshift__(self, other):
        return self._ast_inject_binop(TOKEN_TYPE_RIGHTSHIFT, other)

    def __rrshift__(self, other):
        return self._ast_inject_binop(TOKEN_TYPE_RIGHTSHIFT, other, reverse=True)

    def __and__(self, other):
        return self._ast_inject_binop(TOKEN_TYPE_AND, other)

    def __rand__(self, other):
        return self._ast_inject_binop(TOKEN_TYPE_AND, other, reverse=True)

    def __or__(self, other):
        return self._ast_inject_binop(TOKEN_TYPE_OR, other)

    def __ror__(self, other):
        return self._ast_inject_binop(TOKEN_TYPE_OR, other, reverse=True)

    def __xor__(self, other):
        return self._ast_inject_binop(TOKEN_TYPE_XOR, other)

    def __rxor__(self, other):
        return self._ast_inject_binop(TOKEN_TYPE_XOR, other, reverse=True)

    def __eq__(self, other):
        return self._ast_inject_binop(TOKEN_TYPE_EQUAL, other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        return self._ast_inject_binop(TOKEN_TYPE_SMALLER, other)

    def __le__(self, other):
        return self._ast_inject_binop(TOKEN_TYPE_SMALLER_EQ, other)

    def __gt__(self, other):
        return self._ast_inject_binop(TOKEN_TYPE_GREATER, other)

    def __ge__(self, other):
        return self._ast_inject_binop(TOKEN_TYPE_GREATER_EQ, other)

    def logand(self, other):
        return self._ast_inject_binop(TOKEN_TYPE_LOGICAL_AND, other)

    def logor(self, other):
        return self._ast_inject_binop(TOKEN_TYPE_LOGICAL_OR, other)

    def __pos__(self):
        return self._ast_inject_unop(TOKEN_TYPE_PLUS)

    def __neg__(self):
        return self._ast_inject_unop(TOKEN_TYPE_MINUS)

    def __invert__(self):
        return self._ast_inject_unop(TOKEN_TYPE_REV)

    def lognot(self):
        return self._ast_inject_unop(TOKEN_TYPE_NOT)
