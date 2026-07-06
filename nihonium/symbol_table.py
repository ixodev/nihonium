from typing import *
from .error import error

class SymbolTable:

    def __init__(self, values: Optional[Dict[str, Any]] = None, symbols_properties: Optional[Dict[str, Dict[str, bool]]] = None, flags_format: Optional[List[str]] = None):
        self._values = values if values is not None else {}
        self.flags_format = flags_format if flags_format is not None else ["immutable", "external"]

        self._symbols_properties = symbols_properties if symbols_properties is not None else {
            key: {flag: False for flag in self.flags_format}
            for key in self._values
        }

        self.gen_test_functions()

    def gen_test_functions(self):
        for flag in self.flags_format:
            self.__dict__[f"is_name_{flag}"] = (
                lambda name: self._symbols_properties[name][flag]
            )

            def test_function(value: Any):
                has_found = False
                key = None

                for k in self._values:
                    if self._values[k].reference_equals(value):
                        has_found = True
                        key = k
                        break

                if not has_found:
                    error(f"no value {value} in symbol table")

                return self._symbols_properties[key][flag]

            self.__dict__[f"is_value_{flag}"] = test_function


    def check_flag_format_compatibility(self, flags: Dict[str, bool]):
        for flag in flags:
            if flag not in self.flags_format:
                error(f"flag {flag} does not follow the given flag format")

    def as_dict(self):
        return self._values, self._symbols_properties

    def add_symbol(self, name: str, value: Any, flags: Dict[str, bool]):

        self.check_flag_format_compatibility(flags)

        if name in self:
            error(f"symbol {name} already declared")

        self._values[name] = value
        self._symbols_properties[name] = flags

    def delete_symbol(self, name: str):
        if name not in self:
            error(f"trying to delete symbol {name} but {name} is not declared")

        self._values.pop(name)
        self._symbols_properties.pop(name)

    def clear(self):
        self._values.clear()
        self._symbols_properties.clear()

    def has_name(self, name: str):
        return name in self._values and name in self._symbols_properties

    def has_value(self, value: Any):
        for key in self._values.keys():
            if self._values[key] is value:
                return True
        return False

    def is_format_same_as(self, other: "SymbolTable"):
        return set(other.flags_format) == set(self.flags_format)

    def __repr__(self):
        return f"Symbol Table\n{str(self._values).replace('{', '').replace('}', '')}"

    def __getitem__(self, item):
        if not self.has_name(item):
            error(f"__getitem__: name {item} does not exist")

        return self._values[item]

    def safe_getitem(self, item, retval: Any = None):
        return self._values.get(item, retval)

    def __setitem__(self, key, value):
        if key not in self._values:
            error(f"__setitem__ can only be used on symbols that already exist: {key}")

        if self._symbols_properties[key]["immutable"]:
            error(f"{key} is immutable")

        self._values[key] = value

    def __contains__(self, item):
        return self.has_name(item)

    def __or__(self, other):
        if type(other) is not SymbolTable:
            return NotImplemented

        return SymbolTable.fusion(self, other)

    def __ror__(self, other):
        if type(other) is not SymbolTable:
            return NotImplemented

        return SymbolTable.fusion(other, self)

    @staticmethod
    def fusion(one: "SymbolTable", other: "SymbolTable"):
        one_values, one_properties = one.as_dict()
        other_values, other_properties = other.as_dict()

        if not one.is_format_same_as(other):
            error("cannot fusion symbol tables with different flags format")

        return SymbolTable(values=(one_values | other_values), symbols_properties=(one_properties | other_properties), flags_format=one.flags_format)

    @staticmethod
    def transform_flag(symbol_table: "SymbolTable", flag: str, flag_value: Any):
        values, properties = symbol_table.as_dict()

        new_properties = properties

        for k in properties:
            new_properties[k][flag] = flag_value

        return SymbolTable(values=values, symbols_properties=new_properties, flags_format=symbol_table.flags_format)