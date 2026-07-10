import sys
from typing import List, Optional

from .element import *
from .error import *
from .expressions import Expression, ParsedExpression
from .lexer import Token
from .base_types import IOStream


class Statement(Element):

    def __init__(self, line_str: str, parent=None):
        super().__init__(line_str, parent)

    def __repr__(self):
        return "Nihonium Statement " + super().__repr__()

    def exec(self, program, scope_variables):
        pass

    def __call__(self, program, scope_variables):
        super().__call__(program, scope_variables)
        return self.exec(program, scope_variables)

    def is_unknown(self):
        return isinstance(self, UnknownStatement)


class Scope(Statement):
    def __init__(self, line_str: str, body: List[Statement], parent=None):
        super().__init__(line_str, parent)
        self.body = body

    def exec(self, program, scope_variables):
        for statement in self.body:
            result, function_finished = statement(program, scope_variables)

            if function_finished:
                return result, True

        return None, False

    def __repr__(self):
        return "Nihonium Scope " + Element.__repr__(self)

class FunctionDeclaration(Statement):
    def __init__(self, function, line_str: str, function_name: str, parameters: List[str], start: int, end: int):
        super().__init__(line_str)
        self.function = function
        self.function_name = function_name
        self.function_parameters = parameters
        self.function_start = start
        self.function_end = end
        self.decl = None

    def gen_decl(self):
        self.decl = VarDeclaration("", self.function_name, ParsedExpression("", self.function))

    def exec(self, program, scope_variables):
        self.decl(program, scope_variables)
        return None, False


class ClassDeclaration(Statement):
    def __init__(self, line_str: str, class_name: str, start: int, end: int):
        super().__init__(line_str)

        self.class_name = class_name
        self.start = start
        self.end = end

    def exec(self, program, scope_variables):
        for attr in self.attrs:
            attr.exec(program, scope_variables)


class VarDeclaration(Statement):
    def __init__(self, line_str: str, name: str, expression: Expression, parent=None):
        super().__init__(line_str, parent)
        self.name = name
        self.expression = expression

    def exec(self, program, scope_variables):
        if self.name in scope_variables:
            error(f"{self.name} was already declared")

        scope_variables.add_symbol(self.name, self.expression(program, scope_variables), {"immutable": False, "external": False})
        return None, False

class ConstDeclaration(Statement):
    def __init__(self, line_str: str, name: str, expression: Expression, parent=None):
        super().__init__(line_str, parent)
        self.name = name
        self.expression = expression

    def exec(self, program, scope_variables):
        if self.name in scope_variables:
            error(f"{self.name} was already declared")

        scope_variables.add_symbol(self.name, self.expression(program, scope_variables), {"immutable": True, "external": False})
        return None, False

class VarAffectation(Statement):
    def __init__(self, line_str: str, name: str, expression: Expression, parent=None):
        super().__init__(line_str, parent)
        self.name = name
        self.expression = expression

    def exec(self, program, scope_variables):
        if not self.name in scope_variables:
            error(f"{self.name} was not declared")

        scope_variables[self.name] = self.expression(program, scope_variables)
        return None, False


class Return(Statement):
    def __init__(self, line_str: str, expression: Expression, parent=None):
        super().__init__(line_str, parent)
        self.expression = expression

    def exec(self, program, scope_variables):
        return self.expression(program, scope_variables), True


class FunctionCallStatement(Statement):
    def __init__(self, line_str: str, function: str, parameters: List[Expression], parent=None):
        super().__init__(line_str, parent)
        self.function = function
        self.parameters = parameters

    def exec(self, program, scope_variables):
        return program.call_object_by_name(self.function,
                                     [parameter(program, scope_variables) for parameter in self.parameters], scope_variables), False


class NativeFunctionCallStatement(FunctionCallStatement):
    def __init__(self, line_str: str, function: str, parameters: List[Expression], parent=None):
        super().__init__(line_str, function, parameters, parent)

    def exec(self, program, scope_variables):
        return program.call_native_function(self.function, [parameter(program, scope_variables) for parameter in self.parameters]), False


class DeleteVariableStatement(Statement):
    def __init__(self, line_str: str, variable: Token, parent=None):
        super().__init__(line_str, parent)
        self.variable = variable

    def exec(self, program, scope_variables):
        if not self.variable.get_value() in scope_variables:
            error(f"trying to delete {self.variable} but {self.variable} was not declared")

        scope_variables.delete_symbol(self.variable.get_value())
        return None, False


class ConditionalStatement(Scope):
    def __init__(self, line_str: str, body: List[Statement], condition: Expression, parent=None):
        super().__init__(line_str, body, parent)
        self.condition = condition

    def is_true(self, program, scope_variables):
        return bool(self.condition(program, scope_variables))


class IfStatement(ConditionalStatement):
    def __init__(self, line_str: str, body: List[Statement], condition: Expression, parent=None):
        super().__init__(line_str, body, condition, parent)

    def exec(self, program, scope_variables):
        if self.is_true(program, scope_variables):
            return super().exec(program, scope_variables)

        return None, False


class WhileLoopStatement(ConditionalStatement):
    def __init__(self, line_str: str, body: List[Statement], condition: Expression, parent=None):
        super().__init__(line_str, body, condition, parent)

    def exec(self, program, scope_variables):
        while self.is_true(program, scope_variables):
            result, function_finished = super().exec(program, scope_variables)

            if function_finished:
                return result, function_finished

        return None, False


class ForLoopStatement(ConditionalStatement):
    def __init__(self, line_str: str, body: List[Statement], condition: Expression, initialization: Statement, change: Statement, parent=None):
        super().__init__(line_str, body, condition, parent)
        self.initialization = initialization
        self.change = change

    def exec(self, program, scope_variables):
        self.initialization(program, scope_variables)

        while self.is_true(program, scope_variables):

            result, function_finished = super().exec(program, scope_variables)

            if function_finished:
                return result, function_finished

            self.change(program, scope_variables)

        return None, False


class ImportStatement(Statement):
    def __init__(self, line_str: str, module_name_token: Token, parent=None):
        super().__init__(line_str, parent)
        self.module_name = module_name_token.get_value()

    def exec(self, program, scope_variables):
        program.register_module(self.module_name.replace(".", "/"))
        return None, False


class IOStatement(Statement):
    def __init__(self, line_str: str, file_expression: Expression, parent=None):
        super().__init__(line_str, parent)
        self.file_expression = file_expression

    def check_file(self, program, scope_variables):
        file = self.file_expression(program, scope_variables)

        if not issubclass(type(file), IOStream):
            error(f"\"{self.line_str}\"\nFatal: {self.__class__.__name__} only accepts i/o files as first operand")

        return file

class WriteBufferStatement(IOStatement):
    def __init__(self, line_str: str, file_expression: Expression, expression: Expression, parent=None):
        super().__init__(line_str, file_expression, parent)
        self.expression = expression

    def exec(self, program, scope_variables):
        file = self.check_file(program, scope_variables)
        file.write_buffer(str(self.expression(program, scope_variables)))

        if file.write() == -1:
            error("IO Error")

        return None, False

class ReadBufferStatement(IOStatement):
    def __init__(self, line_str: str, file_expression: Expression, parent=None):
        super().__init__(line_str, file_expression, parent)

    def exec(self, program, scope_variables):
        file = self.check_file(program, scope_variables)
        file.read()

        return file.read_buffer().decode(), False

class FlushBufferStatement(IOStatement):
    def __init__(self, line_str: str, file_expression: Expression, parent=None):
        super().__init__(line_str, file_expression, parent)

    def exec(self, program, scope_variables):
        file = self.check_file(program, scope_variables)
        file.flush()

        return None, False


class UnsafeStatement(Scope):
    def __init__(self, line_str: str, body: List[Statement], parent=None):
        super().__init__(line_str, body, parent)

    def exec(self, program, scope_variables):
        print("ENTERING UNSAFE SECTION")
        super().exec(program, scope_variables)
        print("EXITING UNSAFE SECTION")
        return None, False

class VoidStatement(Statement):
    def __init__(self, line_str: str, parent=None):
        super().__init__(line_str, parent)

    def exec(self, program, scope_variables):
        return None, False

class UnknownStatement(Statement):
    def __init__(self, line_str: str, parent=None):
        super().__init__(line_str, parent)

    def exec(self, program, scope_variables):
        error(f"unknown statement => {self.line_str}")