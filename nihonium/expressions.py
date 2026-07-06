import typing
from .element import *
from .patterns import *
from .operators import *
from .error import *
from .lexer import *
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
    def __init__(self, line_str: str, expression: typing.List[Token]):
        super().__init__(line_str)
        self.expression = expression

    def get_extracted_expression(self):
        return self.expression[0].get_value()

class BooleanAtomicExpression(Atomic):
    def __init__(self, line_str: str, expression: typing.List[Token]):
        super().__init__(line_str, expression)

    def eval(self, program, scope_variables):
        return Bool(self.expression[0].is_type(TOKEN_TYPE_TRUE))

class VariableExpression(Atomic):
    def __init__(self, line_str: str, expression: typing.List[Token]):
        super().__init__(line_str, expression)

    def eval(self, program, scope_variables):
        extracted_expression = self.get_extracted_expression()

        if not extracted_expression in scope_variables:
            error(f"variable {extracted_expression} not declared")

        return scope_variables[extracted_expression]

class FunctionCallExpression(Expression):
    def __init__(self, line_str: str, expression: typing.List[Token]):
        super().__init__(line_str)
        self.expression = expression

        from .parser import Parser

        self.name, unparsed_parameters = ExpressionPatternRecognizer.extract_function_call(self.expression)
        self.parameters = [Parser.parse_expression(parameter, self.line_str) for parameter in unparsed_parameters]

    def eval(self, program, scope_variables):
        return program.call_object_by_name(self.name,
                                     [parameter(program, scope_variables) for parameter in self.parameters], scope_variables)


class NativeFunctionCallExpression(FunctionCallExpression):
    def __init__(self, line_str: str, expression: typing.List[Token]):
        super().__init__(line_str, expression)

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

class StringExpression(Atomic):
    def __init__(self, line_str: str, expression: typing.List[Token]):
        super().__init__(line_str, expression)

    def eval(self, program, scope_variables):
        return String(self.get_extracted_expression()[1:-1])

class NumberExpression(Atomic):
    def __init__(self, line_str: str, expression: typing.List[Token]):
        super().__init__(line_str, expression)

    def eval(self, program, scope_variables):
        value = self.get_extracted_expression()

        if type(value) is int:
            return Int(value)

        return Float(value)

class OperatorExpression(Expression):
    def __init__(self, line_str: str, op: str, already_evaluated: bool = False):
        super().__init__(line_str)
        self.op = Operator(op)
        self.already_evaluated = already_evaluated


class UnaryExpression(OperatorExpression):
    def __init__(self, line_str: str, operand: typing.Union[typing.List[Token], Expression, Object], op: str):
        super().__init__(line_str, op)


        from .parser import Parser
        self.operand = Parser.parse_expression(operand, self.line_str) if type(operand) is list else operand


    def eval(self, program, scope_variables):

        evaluated_operand = self.operand

        if issubclass(type(self.operand), Expression):
            evaluated_operand = self.operand.eval(program, scope_variables)

        return self.op(evaluated_operand)

class BinaryExpression(OperatorExpression):
    def __init__(self, line_str: str, left: typing.Union[typing.List[Token], Expression, Object], right: typing.Union[typing.List[Token], Expression, Primitive, NoPrimitive], op: str):
        super().__init__(line_str, op)

        from .parser import Parser

        self.left = Parser.parse_expression(left, self.line_str) if type(left) is list else left
        self.right = Parser.parse_expression(right, self.line_str) if type(right) is list else right

    def eval(self, program, scope_variables):

        left_evaluated = self.left
        right_evaluated = self.right

        if issubclass(type(self.left), Expression):
            left_evaluated = self.left.eval(program, scope_variables)
        if issubclass(type(self.right), Expression):
            right_evaluated = self.right.eval(program, scope_variables)


        return self.op(left_evaluated, right_evaluated)


class ListExpression(Expression):

    def __init__(self, line_str: str, list_expression: typing.List[typing.List[Token]]):
        super().__init__(line_str)

        from .parser import Parser
        self.list_expression = [Parser.parse_expression(list_element, line_str) for list_element in list_expression]

    def eval(self, program, scope_variables):
        return ArrayList([expr(program, scope_variables) for expr in self.list_expression])


class LambdaExpression(Expression):
    def __init__(self, line_str: str, parameters: typing.List[str], expression: typing.Union[typing.List[Token], Expression]):
        super().__init__(line_str)

        from .parser import Parser

        self.parameters = parameters
        self.expression = Parser.parse_expression(expression, line_str) if type(expression) is list else expression

    def eval(self, program, scope_variables):
        from .function import LambdaFunction
        return LambdaFunction(self.parameters, self.expression)


class ReadBufferExpression(Expression):
    def __init__(self, line_str: str, file_expression: typing.List[Token]):
        super().__init__(line_str)

        from .parser import Parser
        self.file_expression = Parser.parse_expression(file_expression, line_str)

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
    def __init__(self, line_str, parameters: typing.List[typing.List[Token]]):
        super().__init__(line_str)

        from .parser import Parser
        self.numerical_expressions = [Parser.parse_expression(parameter, line_str) for parameter in parameters]

    def eval(self, program, scope_variables):
        num_params = len(self.numerical_expressions)

        if num_params != 2:
            error(f"Complex call expression requires real and imag part but {num_params} were given")

        values = list(map(lambda param: param(program, scope_variables), self.numerical_expressions))

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