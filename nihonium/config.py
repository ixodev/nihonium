class RunConfig:
    def __init__(self, file: str = "", shell: bool = False, pretty_print_ast: bool = False,
                 debug: bool = False, vm: bool = False, disable_default_natives: bool = False, natives: list = []):

        self.program = file
        self.shell = shell
        self.pretty_print_ast = pretty_print_ast
        self.debug = debug
        self.vm = vm
        self.disable_default_natives = disable_default_natives
        self.natives = natives
