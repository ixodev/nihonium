from typing import List, Optional

from .base_types import Object, CallableObject
from .function import Function
from .symbol_table import SymbolTable


class Class(CallableObject):
    def __init__(self, name: str, attrs: SymbolTable, ctor_params: Optional[List[Object]] = None):
        super().__init__()

        self.name = name
        self.attrs = attrs
        self.ctor_params = ctor_params

        self.ctor = self.search_ctor()

    def has_ctor(self):
        return self.ctor is not None

    def search_ctor(self):
        attr = self.attrs.safe_getitem(self.name)

        if attr is not None:
            if attr.is_function():
                return attr

    def call(self, program, scope_variables):
        if self.has_ctor():
            program.call_object(self.ctor, self.ctor_params, scope_variables)