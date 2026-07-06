import argparse

import colorama
import nihonium

from converter import argparse_namespace_to_nh_run_config

class Interpreter:

    def __init__(self, program_filename: str, args: argparse.Namespace):
        self.program_filename = program_filename
        self.args = argparse_namespace_to_nh_run_config(args)
        self.module = None

    def run(self):
        if self.args.shell:
            self.open_shell()
            return

        self.module = nihonium.module.Module(self.program_filename, self.args)

        if self.args.pretty_print_ast:
            self.pretty_printed_ast()
            return 0
        else:
            return self.run_program()

    def run_program(self):
        self.module.run()

        if not self.module.has_function(nihonium.MAIN_FUNCTION):
            return 0

        return self.module.call_function(nihonium.MAIN_FUNCTION, [[]], nihonium.SymbolTable({})).convert_python()

    def pretty_printed_ast(self):
        print(self.module.ast_repr())

    def open_shell(self):
        executor = nihonium.inline.SingleLineExecutor(self.args)

        print(f"{colorama.Fore.BLUE}Nihonium interactive shell v0.1.0\nCopyright (c) Younes Bendimerad, 2026\n* Nihonium interpreter is running *\n")

        while True:
            line = nihonium.program_cleaner.ProgramCleaner(input(f"{colorama.Fore.GREEN}nihonium shell $ {colorama.Style.RESET_ALL}")).minified_program

            if line.strip(" ") in ["\n", ""]:
                continue

            if line == "/exit\n":
                break

            try:
                executor.exec_line(line)
            except Exception as ex:
                print(f"{colorama.Fore.RED}exception: ", ex, colorama.Style.RESET_ALL)
