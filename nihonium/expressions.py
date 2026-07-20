from typing import Union
from .element import *
from .operators import *
from .error import *
from .base_types import *


class Expression(Element):

    def __init__(self, line_str: str):
        super().__init__(line_str)

    def __repr__(self):
        return "Nihonium Expression " + super().__repr__()

    def eval(self, program, scope_variables):
        pass

    def is_unknown(self):
        return isinstance(self, UnknownExpression)

    def __call__(self, program, scope_variables):
        # EXTREME DEBUGGING
        # super().__call__(program, scope_variables)
        return self.eval(program, scope_variables)


class Atomic(Expression):
    def __init__(self, line_str: str, value: Union[int, float, str, bool]):
        super().__init__(line_str)
        self.value = value

    def get_extracted_expression(self):
        return self.value

class Literal(Atomic):
    def __init__(self, line_str: str, literal: Union[int, float, str, bool]):
        super().__init__(line_str, literal)
        self.literal = literal

    def get_extracted_expression(self):
        return self.literal

class BooleanExpression(Literal):
    def __init__(self, line_str: str, literal: bool):
        super().__init__(line_str, literal)

    def eval(self, program, scope_variables):
        return Bool(self.literal)

class VariableExpression(Atomic):
    def __init__(self, line_str: str, name: str):
        super().__init__(line_str, name)

    def eval(self, program, scope_variables):

        if not self.value in scope_variables:
            error(f"variable {self.value} not declared")

        return scope_variables[self.value]

class FunctionCallExpression(Expression):
    def __init__(self, line_str: str, name: str, parameters: List[Expression]):
        super().__init__(line_str)

        self.name = name
        self.parameters = parameters

    def eval(self, program, scope_variables):
        return program.call_object_by_name(self.name,
                                     [parameter(program, scope_variables) for parameter in self.parameters], scope_variables)


class NativeFunctionCallExpression(FunctionCallExpression):
    def __init__(self, line_str: str, name: str, parameters: List[Expression]):
        super().__init__(line_str, name, parameters)

    def eval(self, program, scope_variables):
        return program.call_native_function(self.name, [parameter(program, scope_variables) for parameter in self.parameters])

class DirectCallExpression(Expression):
    def __init__(self, line_str: str, obj: Object, args: List[Expression]):
        super().__init__(line_str)
        self.obj = obj
        self.args = args

    def eval(self, program, scope_variables):
        evaluated_args = [
            arg.eval(program, scope_variables) if isinstance(arg, Expression) else arg
            for arg in self.args
        ]

        return program.call_object(self.obj, evaluated_args, scope_variables)

class StringExpression(Literal):
    def __init__(self, line_str: str, literal: str):
        super().__init__(line_str, literal)

    def eval(self, program, scope_variables):
        return String(self.literal[1:-1])

class NumberExpression(Literal):
    def __init__(self, line_str: str, literal: Union[int, float]):
        super().__init__(line_str, literal)

    def eval(self, program, scope_variables):

        if type(self.literal) is int:
            return Int(self.literal)

        return Float(self.literal)

class OperatorExpression(Expression):
    def __init__(self, line_str: str, op: str, already_evaluated: bool = False):
        super().__init__(line_str)
        self.op = Operator(op)
        self.already_evaluated = already_evaluated


class UnaryExpression(OperatorExpression):
    def __init__(self, line_str: str, operand: Union[Expression, Object], op: str):
        super().__init__(line_str, op)
        self.operand = operand

    def eval(self, program, scope_variables):

        evaluated_operand = self.operand

        if issubclass(type(self.operand), Expression):
            evaluated_operand = self.operand.eval(program, scope_variables)

        return self.op(evaluated_operand)

class BinaryExpression(OperatorExpression):
    def __init__(self, line_str: str, left: Union[Object, Expression], right: Union[Expression, Object], op: str):
        super().__init__(line_str, op)

        self.left = left
        self.right = right

    def eval(self, program, scope_variables):

        left_evaluated = self.left
        right_evaluated = self.right

        if issubclass(type(self.left), Expression):
            left_evaluated = self.left.eval(program, scope_variables)
        if issubclass(type(self.right), Expression):
            right_evaluated = self.right.eval(program, scope_variables)


        return self.op(left_evaluated, right_evaluated)


class ListExpression(Expression):

    def __init__(self, line_str: str, list_expression: List[Expression]):
        super().__init__(line_str)

        self.list_expression = list_expression

    def eval(self, program, scope_variables):
        return ArrayList([expr(program, scope_variables) for expr in self.list_expression])


class LambdaExpression(Expression):
    def __init__(self, line_str: str, parameters: List[str], expression: Expression):
        super().__init__(line_str)

        self.parameters = parameters
        self.expression = expression

    def eval(self, program, scope_variables):
        from .function import LambdaFunction
        return LambdaFunction(self.parameters, self.expression)


class ReadBufferExpression(Expression):
    def __init__(self, line_str: str, file_expression: Expression):
        super().__init__(line_str)
        self.file_expression = file_expression

    def eval(self, program, scope_variables):

        file = self.file_expression(program, scope_variables)

        if not issubclass(type(file), IOStream):
            error(f"\"{self.line_str}\"\nFatal: ReadBufferExpression only accepts i/o files as operand")

        file.read()

        return file.read_buffer().decode()

class ImaginaryUnitExpression(Expression):
    def __init__(self, line_str: str):
        super().__init__(line_str)

    def eval(self, program, scope_variables):
        return Complex(from_number=None, real=Int(0), imag=Int(1))

class ComplexCallExpression(Expression):
    def __init__(self, line_str, parameters: List[Expression]):
        super().__init__(line_str)
        self.parameters = parameters

    def eval(self, program, scope_variables):
        num_params = len(self.parameters)

        if num_params != 2:
            error(f"Complex call expression requires real and imag part but {num_params} were given")

        values = list(map(lambda param: param(program, scope_variables), self.parameters))

        if not issubclass(values[0].__class__, RealNumber) or not issubclass(values[1].__class__, RealNumber):
            error(f"Complex call expression requires two real numbers to build a complex number but ({values[0]}, {values[1]}) were given")

        return Complex(from_number=None, real=values[0], imag=values[1])


class ParsedExpression(Expression):
    def __init__(self, line_str: str, value: Any):
        super().__init__(line_str)
        self.value = value

    def eval(self, program, scope_variables):
        return self.value

class NullExpression(Expression):
    def __init__(self, line_str: str):
        super().__init__(line_str)

    def eval(self, program, scope_variables):
        return Null()

class UnknownExpression(Expression):
    def __init__(self, line_str: str):
        super().__init__(line_str)

    def eval(self, program, scope_variables):
        error(f"error: {self.line_str} => unknown expression")