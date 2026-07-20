import argparse

from .error import NihoniumException
from .program import Program
from .lexer import Lexer
from .parser import Parser
from .expressions import Expression
from .defs import MAIN_FUNCTION
from .program_cleaner import ProgramCleaner
from .symbol_table import SymbolTable
from .config import RunConfig



class SingleLineExecutor:
    def __init__(self, args: RunConfig):
        self.context = Program([], "", args)

    def exec_line(self, line: str):
        tokens = Lexer(ProgramCleaner(line).minified_program, inline=True).tokenize()
        single_node = Parser.parse_generic_line(tokens, line)

        if issubclass(single_node.__class__, Expression):
            value = single_node.eval(self.context, self.context.global_variables)
            return value.convert_python()

        single_node.exec(self.context, self.context.global_variables)

    @staticmethod
    def create_default_single_line_executor():
        return SingleLineExecutor(RunConfig("", True, False, False, False, False, []))


class InlineExecutor:
    def __init__(self, program: str, args: RunConfig):
        self.program = ProgramCleaner(program).minified_program
        self.args = args
        self.context = Program(Parser(Lexer(self.program).tokenize(), self.program).parse(), "", args)

    def exec_inline(self):
        self.context.process_global_statements()

        if self.context.has_function(MAIN_FUNCTION, safe=True):
            try:
                return self.context.call_function(MAIN_FUNCTION, [[]], SymbolTable({})).convert_python()
            except NihoniumException as ex:
                print(f"nihonium exception: {ex}")
                return 1

        else:
            print("warning: no main function, exiting")
            return 0

    @staticmethod
    def create_default_inline_executor(program: str):
        return InlineExecutor(program, RunConfig("", True, False, False, False, False, []))

