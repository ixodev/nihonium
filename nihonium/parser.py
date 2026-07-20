import argparse
from .patterns import *
from .statements import *
from .expressions import *
from .function import *
from .class_obj import *


class Parser:

    def __init__(self, lines: List[List[Token]], lines_str: str):
        self.lines = lines
        self.lines_str = lines_str

    def parse(self):

        global_statements = self.parse_block(0, len(self.lines) - 1)
        return global_statements

    @staticmethod
    def parse_operator_expression(expression: List[Token], line_str: str):

        if ExpressionPatternRecognizer.has_global_parentheses(expression):
            return Parser.parse_expression(expression[1:-1], line_str)

        elif ExpressionPatternRecognizer.is_binary_expression(expression):
            left, right, op = ExpressionPatternRecognizer.extract_binary_expression(expression)
            operator_type = op.get_type()
            return BinaryExpression(line_str, left, right, operator_type)

        elif ExpressionPatternRecognizer.is_unary_expression(expression):
            op, operand = ExpressionPatternRecognizer.extract_unary_expression(expression)
            operator_type = op.get_type()
            return UnaryExpression(line_str, operand, operator_type)

        return UnknownExpression(line_str)

    @staticmethod
    def parse_expression(expression: List[Token], line_str: str):

        if ExpressionPatternRecognizer.has_global_parentheses(expression):
            return Parser.parse_expression(expression[1:-1], line_str)

        if ExpressionPatternRecognizer.is_native_function_call(expression):

            expr = ExpressionPatternRecognizer.extract_native_function_call(expression)
            name, unparsed_parameters = ExpressionPatternRecognizer.extract_function_call(expr)
            parameters = [Parser.parse_expression(parameter, line_str) for parameter in unparsed_parameters]


            return NativeFunctionCallExpression(
                line_str,
                name, parameters
            )

        elif ExpressionPatternRecognizer.is_complex_call_expression(expression):
            parameters = [Parser.parse_expression(param, line_str) for param in ExpressionPatternRecognizer.extract_complex_call_expression(expression)]
            return ComplexCallExpression(line_str, parameters)

        elif ExpressionPatternRecognizer.is_function_call(expression):
            name, unparsed_parameters = ExpressionPatternRecognizer.extract_function_call(expression)
            parameters = [Parser.parse_expression(parameter, line_str) for parameter in unparsed_parameters]

            return FunctionCallExpression(line_str, name, parameters)

        elif ExpressionPatternRecognizer.is_binary_expression(expression):
            left, right, op = ExpressionPatternRecognizer.extract_binary_expression(expression)
            operator_type = op.get_type()
            return BinaryExpression(line_str, Parser.parse_expression(left, line_str), Parser.parse_expression(right, line_str), operator_type)

        elif ExpressionPatternRecognizer.is_unary_expression(expression):
            op, operand = ExpressionPatternRecognizer.extract_unary_expression(expression)
            operator_type = op.get_type()
            return UnaryExpression(line_str, Parser.parse_expression(operand, line_str), operator_type)

        elif ExpressionPatternRecognizer.is_lambda_expression(expression):
            parameters, function_body = ExpressionPatternRecognizer.extract_lambda_expression(expression)
            return LambdaExpression(line_str, parameters, Parser.parse_expression(function_body, line_str))

        elif ExpressionPatternRecognizer.is_io_read_expression(expression):
            return ReadBufferExpression(line_str, Parser.parse_expression(ExpressionPatternRecognizer.extract_io_read_expression(expression), line_str))

        elif ExpressionPatternRecognizer.is_boolean_atomic_expression(expression):
            return BooleanExpression(line_str,
                                           ExpressionPatternRecognizer.extract_boolean_atomic_expression(expression)[0].get_value())

        elif ExpressionPatternRecognizer.is_null_atomic_expression(expression):
            return NullExpression(line_str)

        elif ExpressionPatternRecognizer.is_imaginary_unit_keyword_expression(expression):
            return ImaginaryUnitExpression(line_str)

        elif ExpressionPatternRecognizer.is_int(expression):
            return IntExpression(line_str, ExpressionPatternRecognizer.extract_int(expression).get_value())

        elif ExpressionPatternRecognizer.is_float(expression):
            return FloatExpression(line_str, ExpressionPatternRecognizer.extract_float(expression).get_value())

        elif ExpressionPatternRecognizer.is_string(expression):
            return StringExpression(line_str, ExpressionPatternRecognizer.extract_string(expression).get_value())

        elif ExpressionPatternRecognizer.is_variable(expression):
            return VariableExpression(line_str, ExpressionPatternRecognizer.extract_variable(expression).get_value())

        elif ExpressionPatternRecognizer.is_list_expression(expression):
            return ListExpression(line_str, [Parser.parse_expression(expr, line_str) for expr in ExpressionPatternRecognizer.extract_list_expression(expression)])

        return UnknownExpression(line_str)


    def parse_statement(self, line: List[Token], line_str: str, n_line: int):

        if StatementPatternRecognizer.is_function_definition(line):
            name, parameters, ending = StatementPatternRecognizer.extract_function(line, self.lines)

            declaration = FunctionDeclaration(Function(name,
                                                       parameters, self.parse_block(n_line + 1, ending - 1)), line_str, name,
                                              parameters, n_line, ending)

            return declaration, ending

        elif StatementPatternRecognizer.is_class_declaration(line):
            name, body, ending = StatementPatternRecognizer.extract_class(line, self.lines, n_line)

            return ClassDeclaration(line_str, name, self.parse_block(n_line + 1, ending - 1), n_line, ending), ending

        elif StatementPatternRecognizer.is_import_statement(line):
            return ImportStatement(line_str, StatementPatternRecognizer.extract_import_statement(line)), n_line

        elif StatementPatternRecognizer.is_variable_declaration(line):
            name, expression = StatementPatternRecognizer.extract_variable(line)
            return VarDeclaration(line_str, name, Parser.parse_expression(expression, line_str)), n_line

        elif StatementPatternRecognizer.is_const_declaration(line):
            name, expression = StatementPatternRecognizer.extract_const(line)
            return ConstDeclaration(line_str, name, Parser.parse_expression(expression, line_str)), n_line

        elif StatementPatternRecognizer.is_variable_affectation(line):
            name, expression = StatementPatternRecognizer.extract_variable(line)
            return VarAffectation(line_str, name, Parser.parse_expression(expression, line_str)), n_line

        elif StatementPatternRecognizer.is_return_statement(line):
            expression = StatementPatternRecognizer.extract_return_statement(line)

            if len(expression) == 0:
                return Return(line_str, NullExpression(line_str)), n_line
            else:
                return Return(line_str, Parser.parse_expression(expression, line_str)), n_line

        elif StatementPatternRecognizer.is_function_call(line):
            name, parameters = StatementPatternRecognizer.extract_function_call(line)
            parsed_parameters = [Parser.parse_expression(parameter, line_str) for parameter in parameters]
            return FunctionCallStatement(line_str, name, parsed_parameters), n_line

        elif StatementPatternRecognizer.is_native_function_call(line):
            name, parameters = StatementPatternRecognizer.extract_function_call(StatementPatternRecognizer.extract_native_function_call(line))
            parsed_parameters = [Parser.parse_expression(parameter, line_str) for parameter in parameters]
            return NativeFunctionCallStatement(line_str, name, parsed_parameters), n_line

        elif StatementPatternRecognizer.is_del_statement(line):
            variable = StatementPatternRecognizer.extract_del_statement(line)
            return DeleteVariableStatement(line_str, variable), n_line

        elif StatementPatternRecognizer.is_io_write_statement(line):
            file_expression, expression = StatementPatternRecognizer.extract_io_write_statement(line)
            return WriteBufferStatement(line_str, Parser.parse_expression(file_expression, line_str), Parser.parse_expression(expression, line_str)), n_line

        elif StatementPatternRecognizer.is_io_read_statement(line):
            file_expression = StatementPatternRecognizer.extract_io_read_statement(line)
            return ReadBufferStatement(line_str, Parser.parse_expression(file_expression, line_str)), n_line

        elif StatementPatternRecognizer.is_io_flush_statement(line):
            file_expression = StatementPatternRecognizer.extract_io_flush_statement(line)
            return FlushBufferStatement(line_str, Parser.parse_expression(file_expression, line_str)), n_line

        elif StatementPatternRecognizer.is_unsafe_statement(line):
            unsafe_statement_end = StatementPatternRecognizer.extract_scope(self.lines, n_line)
            if unsafe_statement_end != -1:
                return UnsafeStatement(line_str, self.parse_block(n_line + 1, unsafe_statement_end - 1)), unsafe_statement_end

        elif StatementPatternRecognizer.is_if_statement(line):
            condition, if_statement_end = StatementPatternRecognizer.extract_block(self.lines, n_line)
            if if_statement_end != -1:
                return IfStatement(line_str, self.parse_block(n_line + 1, if_statement_end - 1), Parser.parse_expression(condition, line_str)), if_statement_end

        elif StatementPatternRecognizer.is_while_statement(line):
            condition, while_statement_end = StatementPatternRecognizer.extract_block(self.lines,
                                                                                                      n_line)
            if while_statement_end != -1:
                return WhileLoopStatement(line_str, self.parse_block(n_line + 1, while_statement_end - 1),
                                                     Parser.parse_expression(condition, line_str)), while_statement_end

        elif StatementPatternRecognizer.is_for_statement(line):
            for_statement_end = StatementPatternRecognizer.extract_block(self.lines, n_line)[1]
            initialization, condition, change = StatementPatternRecognizer.extract_for_statement(line)

            if for_statement_end != - 1:
                return ForLoopStatement(line_str, self.parse_block(n_line + 1, for_statement_end - 1),
                                                   Parser.parse_expression(condition, line_str), self.parse_statement(initialization, '', 0)[0],
                                                    self.parse_statement(change, '', 0)[0]), for_statement_end

        elif StatementPatternRecognizer.is_import_statement(line):
            return ImportStatement(line_str, StatementPatternRecognizer.extract_import_statement(line)), n_line

        return UnknownStatement(line_str), n_line

    @staticmethod
    def parse_generic_line(line: List[Token], line_str: str):
        parsed_node_stmt = Parser([[]], "").parse_statement(line, line_str, -1)[0]

        if parsed_node_stmt.is_unknown():
            return Parser.parse_expression(line, line_str)

        return parsed_node_stmt


    def parse_block(self, start: int, end: int):
        statements = []

        n_line = start

        while n_line < end + 1:

            line = self.lines[n_line]
            line_str = self.lines_str[n_line]

            statement, n_line = self.parse_statement(line, line_str, n_line)

            statements.append(statement)

            n_line += 1

        return statements