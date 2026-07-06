from .error import *
from .program_cleaner import *
from .lexer import *


class ProgramReader:
    def __init__(self, program_filename: str):
        self.program_filename = program_filename
        self.original_program = None

        self.read_program()

        self.program_cleaner = ProgramCleaner(self.original_program)
        self.minified_program = self.program_cleaner.get_minified_program()
        self.lines_str = self.program_cleaner.get_lines()

        self.lexer = Lexer(self.minified_program)
        self.tokens = self.lexer.tokenize()

    def get_minified_program(self):
        return self.minified_program

    def get_lines_as_tokens(self):
        return self.tokens

    def get_lines(self):
        return self.lines_str

    def read_program(self):
        try:
            file = open(self.program_filename, "r")
            self.original_program = file.read()
            file.close()
        except IOError as ex:
            raise NihoniumException(ex)