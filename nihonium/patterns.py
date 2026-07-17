from typing import List

from .defs import *
from .lexer import *
from .operators import *


def extract_token_sequence(expression: List[Token], separator: str, opening_tokens: List[str], closing_tokens: List[str]):

    sequence = []
    current_token_subsequence = []
    depth = 0

    for token in expression:

        if token.get_type() in opening_tokens:
            depth += 1
        elif token.get_type() in closing_tokens:
            depth -= 1

        if token.is_type(separator):
            if depth == 0:
                sequence.append(current_token_subsequence)
                current_token_subsequence = []
            else:
                current_token_subsequence.append(token)
        else:
            current_token_subsequence.append(token)

    if len(current_token_subsequence) != 0:
        sequence.append(current_token_subsequence)

    return sequence

def merge_lists(l: List[List[Any]]):

    merged_list = []

    for el in l:
        for element in el:
            merged_list.append(element)

    return merged_list


class StatementPatternRecognizer:

    @staticmethod
    def is_function_definition(line: List[Token]):
        if len(line) < 5:
            return False

        if line[0].is_type(TOKEN_TYPE_FUNCTION) and line[1].is_type(TOKEN_TYPE_IDENT) and line[2].is_type(TOKEN_TYPE_LPAREN) and line[-2].is_type(TOKEN_TYPE_RPAREN) and line[-1].is_type(TOKEN_TYPE_LBRACE):
            return True

        return False

    @staticmethod
    def extract_function(function_declaration: List[Token], lines: List[List[Token]]):
        prototype = StatementPatternRecognizer.extract_function_prototype(function_declaration)
        name = StatementPatternRecognizer.extract_function_name_from_prototype_or_call(prototype)
        parameters = StatementPatternRecognizer.extract_function_parameters_from_prototype(prototype)
        ending = StatementPatternRecognizer.extract_function_ending(function_declaration, lines)

        return name, parameters, ending

    @staticmethod
    def extract_function_prototype(line: List[Token]):
        function_prototype = line.copy()

        function_prototype = [
            token for token in function_prototype
            if not token.get_type() in [TOKEN_TYPE_LBRACE, TOKEN_TYPE_FUNCTION]
        ]

        return function_prototype

    @staticmethod
    def extract_function_name_from_prototype_or_call(function_prototype: List[Token]):
        return function_prototype[0].get_value()

    @staticmethod
    def extract_function_parameters_from_prototype(function_prototype: List[Token]):
        parameters = function_prototype.copy()

        # name + LPAREN
        parameters.pop(0)

        parameters = [token for token in parameters if not token.get_type() in [TOKEN_TYPE_LPAREN, TOKEN_TYPE_RPAREN]]

        parameters_cleaned = []

        for parameter in parameters:
            if not parameter.is_type(TOKEN_TYPE_COMMA) and (parameter.get_type() in [TOKEN_TYPE_IDENT, TOKEN_TYPE_NUMBER, TOKEN_TYPE_STRING]):
                parameters_cleaned.append(parameter.get_value())

        return parameters_cleaned

    @staticmethod
    def extract_function_parameters_from_call(function_prototype: List[Token]):
        parameters = function_prototype.copy()
        parameters.pop(0)
        parameters.pop(0)
        parameters.pop(-1)

        return extract_token_sequence(parameters, TOKEN_TYPE_COMMA, [TOKEN_TYPE_LPAREN, TOKEN_TYPE_LSBRACE, TOKEN_TYPE_LBRACE], [TOKEN_TYPE_RPAREN, TOKEN_TYPE_RSBRACE, TOKEN_TYPE_RBRACE])

    @staticmethod
    def extract_function_ending(function_declaration: List[Token], lines: List[List[Token]]):
        n = 0
        n_open_scopes = 0
        is_in_function = False

        for line in lines:

            if line is function_declaration:
                is_in_function = True
                n_open_scopes += 1

            if is_in_function:
                if len(line) > 0:
                    if line[-1].is_type(TOKEN_TYPE_LBRACE) and line != function_declaration:
                        n_open_scopes += 1
                    elif line[-1].is_type(TOKEN_TYPE_RBRACE):
                        n_open_scopes -= 1

                if n_open_scopes == 0:
                    return n

            n += 1

        return -1

    @staticmethod
    def extract_function_special_markers(function_prototype: List[Token]):
        pass

    @staticmethod
    def is_variable_declaration(line: List[Token]):

        if len(line) < 4:
            return False

        if line[0].is_type(TOKEN_TYPE_VAR):
            if line[2].is_type(TOKEN_TYPE_EQUAL):
                return True

        return False

    @staticmethod
    def is_const_declaration(line: List[Token]):
        if len(line) < 4:
            return False

        if line[0].is_type(TOKEN_TYPE_CONST):
            if line[2].is_type(TOKEN_TYPE_EQUAL):
                return True

        return False

    @staticmethod
    def is_variable_affectation(line: List[Token]):
        if len(line) < 3:
            return False

        if line[0].is_type(TOKEN_TYPE_IDENT):
            if line[1].is_type(TOKEN_TYPE_EQUAL):
                return True

        return False

    @staticmethod
    def extract_const(line: List[Token]):
        return StatementPatternRecognizer.extract_variable(line)

    @staticmethod
    def extract_variable(line: List[Token]):
        name = StatementPatternRecognizer.extract_variable_name(line)
        return name, StatementPatternRecognizer.extract_variable_expression(line, name)

    @staticmethod
    def extract_variable_name(line: List[Token]):
        var_decl = line.copy()

        var_decl = [token for token in var_decl if token.get_type() not in [TOKEN_TYPE_CONST, TOKEN_TYPE_VAR, TOKEN_TYPE_EQUAL]]

        return var_decl[0].get_value()

    @staticmethod
    def extract_variable_expression(line: List[Token], variable_name: str):
        var_decl = line.copy()

        expression = []
        n_varname_occ = 0

        for token in var_decl:
            if token.is_type(TOKEN_TYPE_IDENT) and token.get_value() == variable_name:
                if n_varname_occ != 0:
                    expression.append(token)

                n_varname_occ += 1


            elif not token.is_type(TOKEN_TYPE_VAR) and not token.is_type(TOKEN_TYPE_CONST) and not token.is_type(TOKEN_TYPE_EQUAL):
                expression.append(token)

        return expression

    @staticmethod
    def is_return_statement(line: List[Token]):
        if len(line) >= 1:
            if line[0].is_type(TOKEN_TYPE_RETURN):
                return True

        return False

    @staticmethod
    def extract_return_statement(line: List[Token]):
        if len(line) == 0:
            return None

        return line[1:]

    @staticmethod
    def is_function_call(line: List[Token]):
        if len(line) < 3:
            return False

        if line[0].is_type(TOKEN_TYPE_IDENT):
            if line[1].is_type(TOKEN_TYPE_LPAREN):
                if line[-1].is_type(TOKEN_TYPE_RPAREN):
                    depth = 0

                    for n_token, token in enumerate(line, 1):
                        if token.is_type(TOKEN_TYPE_LPAREN):
                            depth += 1
                        elif token.is_type(TOKEN_TYPE_RPAREN):
                            depth -= 1

                        if depth == 0 and n_token > 1 and not token.is_type(TOKEN_TYPE_RPAREN):
                            return False

                    return True

        return False


    @staticmethod
    def extract_function_call(line: List[Token]):
        name = StatementPatternRecognizer.extract_function_name_from_prototype_or_call(line)
        parameters = StatementPatternRecognizer.extract_function_parameters_from_call(line)
        return name, parameters

    @staticmethod
    def is_if_statement(line: List[Token]):
        if len(line) >= 3:
            return line[0].is_type(TOKEN_TYPE_IF) and line[-1].is_type(TOKEN_TYPE_LBRACE)

        return False

    @staticmethod
    def is_while_statement(line: List[Token]):
        if len(line) >= 3:
            return line[0].is_type(TOKEN_TYPE_WHILE) and line[-1].is_type(TOKEN_TYPE_LBRACE)

        return False

    @staticmethod
    def is_for_statement(line: List[Token]):
        if len(line) >= 10:
            return line[0].is_type(TOKEN_TYPE_FOR) and line[-1].is_type(TOKEN_TYPE_LBRACE)

        return False

    @staticmethod
    def extract_for_statement(line: List[Token]):

        semicolons = []

        for n_token, token in enumerate(line):
            if token.is_type(TOKEN_TYPE_SEMICOLON):
                semicolons.append(n_token)

        initialization = line[1:semicolons[0]]
        condition = line[semicolons[0] + 1:semicolons[1]]
        change = line[semicolons[1] + 1:-1]

        return initialization, condition, change

    @staticmethod
    def extract_scope(lines: List[List[Token]], n_line: int):

        end = -1
        depth = 0

        for i in range(n_line, len(lines)):

            line = lines[i]

            if len(line) > 0:
                if line[-1].is_type(TOKEN_TYPE_LBRACE):
                    depth += 1
                elif line[-1].is_type(TOKEN_TYPE_RBRACE):
                    depth -= 1

                if depth == 0 and i != n_line:
                    end = i
                    break

        return end

    @staticmethod
    def extract_block(lines: List[List[Token]], n_line: int):
        return lines[n_line][1:-1], StatementPatternRecognizer.extract_scope(lines, n_line)

    @staticmethod
    def is_del_statement(line: List[Token]):
        if len(line) >= 2:
            if line[0].is_type(TOKEN_TYPE_DEL):
                return True

        return False

    @staticmethod
    def extract_del_statement(line: List[Token]):
        return line[1]

    @staticmethod
    def is_import_statement(line: List[Token]):
        if len(line) == 2:
            return line[0].is_type(TOKEN_TYPE_IMPORT)
        return False

    @staticmethod
    def extract_import_statement(line: List[Token]):
        return line[1]

    @staticmethod
    def is_unsafe_statement(line: List[Token]):
        if len(line) > 1:
            return line[0].is_type(TOKEN_TYPE_UNSAFE) and line[1].is_type(TOKEN_TYPE_LBRACE)

    @staticmethod
    def is_io_write_statement(line: List[Token]):
        if len(line) >= 2:
            return line[0].is_type(TOKEN_TYPE_WRITEBUF)

    @staticmethod
    def extract_io_write_statement(line: List[Token]):
        comma = -1

        for n_token, token in enumerate(line):
            if token.is_type(TOKEN_TYPE_COMMA):
                comma = n_token
                break

        if comma == -1:
            return line[1:], []

        return line[1:][:comma - 1], line[1:][comma:]

    @staticmethod
    def is_io_read_statement(line: List[Token]):
        if len(line) >= 2:
            return line[0].is_type(TOKEN_TYPE_READBUF)

    @staticmethod
    def extract_io_read_statement(line: List[Token]):
        return line[1:]

    @staticmethod
    def is_io_flush_statement(line: List[Token]):
        if len(line) >= 2:
            return line[0].is_type(TOKEN_TYPE_FLUSH)

    @staticmethod
    def extract_io_flush_statement(line: List[Token]):
        return line[1:]

    @staticmethod
    def is_native_function_call(expression: List[Token]):
        return ExpressionPatternRecognizer.is_native_function_call(expression)

    @staticmethod
    def extract_native_function_call(expression: List[Token]):
        return ExpressionPatternRecognizer.extract_native_function_call(expression)

    @staticmethod
    def is_class_declaration(line: List[Token]):
        if len(line) >= 3:
            if line[0].is_type(TOKEN_TYPE_CLASS):
                if line[-1].is_type(TOKEN_TYPE_LBRACE):
                    if line[1].is_type(TOKEN_TYPE_IDENT):
                        return True

        return False

    @staticmethod
    def extract_class(line: List[Token], lines: List[List[Token]], n_line: int):
        t = StatementPatternRecognizer.extract_block(lines, n_line)
        return line[1].get_value(), t[0], t[1]


class ExpressionPatternRecognizer:
    def __init__(self):
        pass

    @staticmethod
    def is_number(expression: List[Token]):
        if len(expression) == 1 and isinstance(expression[0], Token):
            return expression[0].is_type(TOKEN_TYPE_NUMBER)
        return False

    @staticmethod
    def extract_number(expression: List[Token]):
        return expression[0]

    @staticmethod
    def is_string(expression: List[Token]):
        if len(expression) == 1 and isinstance(expression[0], Token):
            return expression[0].is_type(TOKEN_TYPE_STRING)
        return False

    @staticmethod
    def extract_string(expression: List[Token]):
        return expression[0]

    @staticmethod
    def is_variable(expression: List[Token]):
        if len(expression) == 1:
            if expression[0].is_type(TOKEN_TYPE_IDENT):
                return True

        return False

    @staticmethod
    def extract_variable(expression: List[Token]):
        return expression[0]

    @staticmethod
    def is_function_call(expression: List[Token]):
        return StatementPatternRecognizer.is_function_call(expression)

    @staticmethod
    def extract_function_call(expression: List[Token]):
        return StatementPatternRecognizer.extract_function_call(expression)

    @staticmethod
    def has_global_parentheses(tokens: List[Token]):
        if not tokens or len(tokens) == 0:
            return False
        if not tokens[0].is_type(TOKEN_TYPE_LPAREN):
            return False
        if not tokens[-1].is_type(TOKEN_TYPE_RPAREN):
            return False

        depth = 0
        for i, token in enumerate(tokens):
            if token.is_type(TOKEN_TYPE_LPAREN):
                depth += 1
            elif token.is_type(TOKEN_TYPE_RPAREN):
                depth -= 1

            if depth == 0 and i != len(tokens) - 1:
                return False

        return depth == 0

    @staticmethod
    def is_binary_expression(expression: List[Token]):
        return ExpressionPatternRecognizer.extract_binary_expression(expression) != (None, None, None)

    @staticmethod
    def extract_binary_expression(expression: List[Token]):

        expression_copy = expression.copy()

        precedences = [[TOKEN_TYPE_LOGICAL_AND, TOKEN_TYPE_LOGICAL_OR],
                      [TOKEN_TYPE_OR], [TOKEN_TYPE_XOR], [TOKEN_TYPE_AND],
                      [TOKEN_TYPE_EQUALITY, TOKEN_TYPE_INEQUALITY, TOKEN_TYPE_GREATER, TOKEN_TYPE_SMALLER, TOKEN_TYPE_GREATER_EQ, TOKEN_TYPE_SMALLER_EQ, TOKEN_TYPE_REFERENCE],
                      [TOKEN_TYPE_LEFTSHIFT, TOKEN_TYPE_RIGHTSHIFT],
                      [TOKEN_TYPE_PLUS, TOKEN_TYPE_MINUS], [TOKEN_TYPE_STAR, TOKEN_TYPE_SLASH, TOKEN_TYPE_DOUBLE_SLASH, TOKEN_TYPE_MOD], [TOKEN_TYPE_DOUBLE_STAR]]

        for ops in precedences:
            depth = 0

            for i in range(len(expression_copy)):
                token = expression_copy[i]

                if token.get_type() in [TOKEN_TYPE_LPAREN, TOKEN_TYPE_LSBRACE, TOKEN_TYPE_LBRACE]:
                    depth += 1
                elif token.get_type() in [TOKEN_TYPE_RPAREN, TOKEN_TYPE_RSBRACE, TOKEN_TYPE_RBRACE]:
                    depth -= 1

                if depth == 0 and token.get_type() in ops:
                    if token.get_type() in Operator.unary_operators and i == 0:
                        continue

                    elif token.get_type() in Operator.unary_operators and i != 0:
                        previous_token_type = expression_copy[i - 1].get_type()
                        if previous_token_type in Operator.binary_operators:
                            continue
                    left = expression_copy[:i]
                    right = expression_copy[i + 1:]
                    op = token
                    return left, right, op

        return None, None, None

    @staticmethod
    def is_null_atomic_expression(expression: List[Token]):
        if len(expression) == 1:
            return expression[0].is_type(TOKEN_TYPE_NULL)
        return False

    @staticmethod
    def is_boolean_atomic_expression(expression: List[Token]):
        if len(expression) == 1:
            if expression[0].get_type() in [TOKEN_TYPE_TRUE, TOKEN_TYPE_FALSE]:
                return True

        return False

    @staticmethod
    def extract_boolean_atomic_expression(expression: List[Token]):
        return [expression[0]]

    @staticmethod
    def is_unary_expression(expression: List[Token]):
        if len(expression) >= 2:
            return expression[0].get_type() in Operator.unary_operators
        return False

    @staticmethod
    def extract_unary_expression(expression: List[Token]):
        op = expression[0]
        operand = expression[1:]

        while ExpressionPatternRecognizer.has_global_parentheses(operand):
            operand = operand[1:-1]

        return op, operand

    @staticmethod
    def is_native_function_call(expression: List[Token]):
        if len(expression) > 0:
            return expression[0].is_type(TOKEN_TYPE_NATIVE)
        return False

    @staticmethod
    def extract_native_function_call(expression: List[Token]):
        return expression[1:]

    @staticmethod
    def is_io_read_expression(expression: List[Token]):
        if len(expression) >= 2:
            return expression[0].is_type(TOKEN_TYPE_READBUF)
        return False

    @staticmethod
    def extract_io_read_expression(expression: List[Token]):
        return expression[1:]

    @staticmethod
    def is_list_expression(expression: List[Token]):
        if len(expression) >= 2:
            return expression[0].is_type(TOKEN_TYPE_LSBRACE) and expression[-1].is_type(TOKEN_TYPE_RSBRACE)
        return False

    @staticmethod
    def extract_list_expression(expression: List[Token]):
        return extract_token_sequence(expression[1:-1], TOKEN_TYPE_COMMA, [TOKEN_TYPE_LPAREN, TOKEN_TYPE_LSBRACE, TOKEN_TYPE_LBRACE], [TOKEN_TYPE_RPAREN, TOKEN_TYPE_RSBRACE, TOKEN_TYPE_RBRACE])

    @staticmethod
    def is_lambda_expression(expression: List[Token]):
        expression_copy = expression.copy()

        if ExpressionPatternRecognizer.has_global_parentheses(expression):
            return ExpressionPatternRecognizer.is_lambda_expression(expression_copy[1:-1])

        if len(expression_copy) >= 3:

            depth = 0
            has_lambda = False

            for n_token, token in enumerate(expression_copy):


                if token.get_type() in [TOKEN_TYPE_LPAREN, TOKEN_TYPE_LBRACE, TOKEN_TYPE_LSBRACE]:
                    depth += 1
                elif token.get_type() in [TOKEN_TYPE_RPAREN, TOKEN_TYPE_RBRACE, TOKEN_TYPE_RSBRACE]:
                    depth -= 1


                if n_token == 0 and token.get_type() not in [TOKEN_TYPE_COMMA, TOKEN_TYPE_LPAREN, TOKEN_TYPE_IDENT, TOKEN_TYPE_LAMBDA]:
                    return False

                if token.is_type(TOKEN_TYPE_LAMBDA):
                    has_lambda = True

                if not has_lambda and token.get_type() not in [TOKEN_TYPE_LPAREN, TOKEN_TYPE_RPAREN, TOKEN_TYPE_IDENT, TOKEN_TYPE_LAMBDA, TOKEN_TYPE_COMMA]:
                    return False

            return has_lambda

        return False

    @staticmethod
    def extract_lambda_expression(expression: List[Token]):
        lambda_sep = next((i for i, x in enumerate(expression) if x.is_type(TOKEN_TYPE_LAMBDA)), None)
        function_params = expression[:lambda_sep]
        function_params = list(filter(lambda token: token.is_type(TOKEN_TYPE_IDENT), function_params))
        function_body = expression[lambda_sep + 1:]

        while ExpressionPatternRecognizer.has_global_parentheses(function_params):
            function_params = function_params[1:-1]

        params = merge_lists(extract_token_sequence(function_params, TOKEN_TYPE_COMMA, [], []))
        return list(map(lambda param: param.get_value(), params)), function_body

    @staticmethod
    def is_imaginary_unit_keyword_expression(expression: List[Token]):
        if len(expression) == 1:
            return expression[0].is_type(TOKEN_TYPE_IMAGINARY_UNIT)

        return False

    @staticmethod
    def is_complex_call_expression(expression: List[Token]):
        if len(expression) < 3:
            return False

        if expression[0].is_type(TOKEN_TYPE_COMPLEX_CALL):
            if expression[1].is_type(TOKEN_TYPE_LPAREN):
                if expression[-1].is_type(TOKEN_TYPE_RPAREN):
                    depth = 0

                    for n_token, token in enumerate(expression, 1):
                        if token.is_type(TOKEN_TYPE_LPAREN):
                            depth += 1
                        elif token.is_type(TOKEN_TYPE_RPAREN):
                            depth -= 1

                        if depth == 0 and n_token > 1 and not token.is_type(TOKEN_TYPE_RPAREN):
                            return False

                    return True

        return False


    @staticmethod
    def extract_complex_call_expression(expression: List[Token]):
        return ExpressionPatternRecognizer.extract_function_call(expression)[1]
