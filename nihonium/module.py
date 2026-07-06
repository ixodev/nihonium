from .parser import *
from .program_reader import *
from .config import RunConfig


class Module:
    def __init__(self, module_name: str, args: RunConfig):
        self.args = args
        self.module_name = module_name
        self.program_reader = ProgramReader(module_name)
        self.program = Parser(self.program_reader.get_lines_as_tokens(), self.program_reader.get_lines()).parse(self.module_name, self.args)

    def get_program(self):
        return self.program

    def run(self):
        self.program.process_global_statements()

    def get_global_variables(self):
        return self.program.global_variables

    def get_function(self, name: str):
        return self.program.get_function(name)

    def has_function(self, name: str):
        return self.program.has_function(name)

    def has_native_function(self, name: str, client_module_name: str):
        return self.program.has_native_function(name, client_module_name)

    def call_function(self, function_name: str, given_parameters: List[Any], actual_scope: SymbolTable):
        return self.program.call_function(function_name, given_parameters, actual_scope)

    def ast_repr(self):
        return self.program.ast_repr()

    def __repr__(self):
        return f"Module {self.module_name}\n" + str(self.program)