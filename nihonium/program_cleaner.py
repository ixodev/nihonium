from .lexer import *



class ProgramCleaner:
    def __init__(self, program: str):
        self.program = program
        self.minified_program = None
        self.lines_str = self.program.split("\n")
        self.clean()

    def clean(self):
        self.lines_str = [line.strip(" ") for line in self.lines_str if not line.strip(" ").startswith(COMMENT) and line.strip(" ") != " " and len(line) != 0]
        self.build_minified_program()

    def build_minified_program(self):
        self.minified_program = ""
        for line in self.lines_str:
            self.minified_program += (line + "\n")

    def get_lines(self):
        return self.lines_str

    def get_minified_program(self):
        return self.minified_program

