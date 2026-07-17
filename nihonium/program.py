import argparse
import sys
import types
from typing import Dict, List, Any

from .error import *
from .base_types import Object, Primitive, convert_nihonium
from .function import *
from .import_native import *
from .symbol_table import SymbolTable
from .config import RunConfig


class Program:
    def __init__(self, global_statements: List["Statement"], module_name: str, args: RunConfig):

        self.global_statements = global_statements
        self.module_name = module_name.removesuffix(".nh").replace("/", ".")
        self.args = args

        self.global_variables = SymbolTable()
        self.inner_global_variables = SymbolTable()
        self.module_cache = {}
        self.native_functions = {}

        self.import_native_functions()

    def get_global_variable(self, name: str):
        return self.global_variables[name]

    def get_module_from_cache(self, module_name: str):
        return self.module_cache[module_name]

    def has_module_in_cache(self, module_name: str):
        return self.get_module_from_cache(module_name) is not None

    def register_module(self, name: str):
        from .module import Module

        module_name = name.lower()

        if module_name in self.module_cache.keys():
            return

        self.module_cache[module_name] = None
        loaded_module = Module(f"{module_name}.nh", self.args)
        self.module_cache[module_name] = loaded_module

        loaded_module.run()
        self.global_variables = SymbolTable.transform_flag(loaded_module.get_global_variables(), "external", True) | self.global_variables

    def import_native_functions(self):

        if not self.args.disable_default_natives:
            self.native_functions = import_natives(self.module_name, "natives")

        for native_module_name in self.args.natives:
            self.native_functions = {**self.native_functions, **import_natives(self.module_name, native_module_name)}

    def get_function(self, name: str, safe: bool=False):

        if safe:
            return self.global_variables.safe_getitem(name)

        else:
            obj = self.global_variables[name]

        if not obj.is_callable():
            error(f"trying to access object \"{name}\" as a function but \"{name}\" is not callable")

        return obj

    def has_function(self, name: str, safe: bool=False):
        return self.get_function(name, safe) is not None

    def has_native_function(self, name: str, client_module_name: str):
        if name not in self.native_functions:
            return False

        if not self.native_functions[name].is_module_allowed(client_module_name):
            return False

        return True

    def process_global_statements(self):
        self.global_variables.clear()
        self.inner_global_variables.clear()

        for statement in self.global_statements:
            statement(self, self.global_variables)


        #print("------- MODULE ", self.module_name, " ------")
        #print(self.global_variables)
        #print("-------------------------------------\n\n")

    def call_object_by_name(self, obj_name: str, given_parameters: List[Any], actual_scope: SymbolTable):

        scope_to_search = self.global_variables | actual_scope

        if not obj_name in scope_to_search:
            error(f"No callable object named \"{obj_name}\" in module \"{self.module_name}\"")

        obj = scope_to_search[obj_name]

        if not obj.is_callable():
            error(f"Object \"{obj_name}\" in module \"{self.module_name}\" is not callable")

        n_given_parameters = len(given_parameters)
        n_parameters = obj.get_num_parameters()

        if n_given_parameters != n_parameters:
            error(f"callable object \"{obj_name}\" function expected {n_parameters} parameters but {n_given_parameters} were given")

        if self.is_obj_external(obj_name, actual_scope):
            module = self.find_obj_in_parallel_module(obj_name)

            if module is not None:
                return module.program.call_object(obj, given_parameters, SymbolTable())

        scope_variables = self.global_variables | SymbolTable(values=dict(zip(obj.get_parameters(), given_parameters)))
        return obj(self, scope_variables)

    def call_object(self, obj: CallableObject, given_parameters, actual_scope: SymbolTable):

        if not obj.is_callable():
            error(f"Object \"{obj}\" in module \"{self.module_name}\" is not callable")

        n_given_parameters = len(given_parameters)
        n_parameters = obj.get_num_parameters()

        if n_given_parameters != n_parameters:
            error(f"callable object \"{obj}\” function expected {n_parameters} parameters but {n_given_parameters} were given")

        if self.is_obj_external(obj, actual_scope, as_name=False):
            module = self.find_obj_in_parallel_module(obj)

            if module is not None:
                return module.program.call_object(obj, given_parameters, {})

        scope_variables = self.global_variables | SymbolTable(values=dict(zip(obj.get_parameters(), given_parameters)))
        return obj(self, scope_variables)

    def call_native_function(self, function_name: str, given_parameters: List[Any]):

        function = self.native_functions.get(function_name)

        if function is not None:
            return convert_nihonium(self.native_functions[function_name](*[parameter.convert_python() for parameter in given_parameters]))

        for module in self.module_cache:
            module_obj = self.module_cache[module]
            if module_obj.has_native_function(function_name, self.module_name):
                return module_obj.program.call_native_function(function_name, given_parameters)

        error(f"No native function \"{function_name}\" in module \"{self.module_name}\"")

    def call_function(self, function_name: str, given_parameters: List[Any], actual_scope: SymbolTable):
        return self.call_object_by_name(function_name, given_parameters, actual_scope)

    def is_obj_external(self, obj: Union[Object, str], actual_scope: SymbolTable, as_name: bool=True):
        #print(actual_scope if self.module_name == "examples.lambdas" else "")
        #print("is_external, \"", obj, "\":", end=" ")
        #print(self.global_variables | actual_scope)
        if as_name:
            return (self.global_variables | actual_scope).is_name_external(obj)
        #print(f"I AM SEARCHING THE OBJECT {obj} with ID {obj.get_id()}")
        return (self.global_variables | actual_scope).is_value_external(obj)

    def find_obj_in_parallel_module(self, obj: Union[Object, str], as_name: bool=True):
        for module in self.module_cache:

            module_obj = self.module_cache[module]

            if as_name:
                if obj in module_obj.program.global_variables:
                    return module_obj
            else:
                if module_obj.program.global_variables.has_value(obj):
                    return module_obj

        return None

    def ast_repr(self):
        string = "\n\nProgram AST\n\n\tGlobal statements:\n\n\t"

        for global_statement in self.global_statements:
            string += global_statement.ast_repr().replace("\n", "\n\t")

        return string