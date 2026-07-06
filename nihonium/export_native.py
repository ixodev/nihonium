import sys
from typing import *
import types

from .error import *


def export_symbol(*args, **kwargs):

    def decorator(symbol: Union[types.FunctionType, type]):

        module = sys.modules[symbol.__module__]

        if not getattr(module, "exported_symbols", False):
            module.exported_symbols = {}

        wrapped = _wrap(symbol)

        wrapped._exported = True

        if "export_for_all" in kwargs:
            wrapped._export_for_all = kwargs["export_for_all"]

        if "allowed_modules" in kwargs:
            wrapped._allowed_modules = kwargs["allowed_modules"]

        if "nihonium_name" in kwargs:
            wrapped._nihonium_name = kwargs["nihonium_name"]

        if "marks" in kwargs:
            marks = kwargs["marks"]
            if isinstance(marks, str):
                wrapped._marks = [marks]
            elif isinstance(marks, list):
                wrapped._marks = marks
            else:
                raise Exception(f"native function marks \"{symbol.__name__}\" in module {module.__name__}.py have to be declared as a single string or a list")

        module.exported_symbols[getattr(wrapped, "_nihonium_name", symbol.__name__)] = wrapped

        return wrapped

    if len(args) == 1 and callable(args[0]) and not kwargs:
        return decorator(args[0])

    return decorator

def _wrap(symbol: Union[type, types.FunctionType]):
    if isinstance(symbol, types.FunctionType):
        return _wrap_function(symbol)
    elif isinstance(symbol, type):
        return _wrap_class(symbol)

    return symbol


def _wrap_function(symbol: types.FunctionType):
    def wrapper(*args, **kwargs):
        return symbol(*args, **kwargs)

    wrapper.__name__ = symbol.__name__
    wrapper.__repr__ = lambda self: "<Nihonium Native Function, " + wrapper.__name__ + ">"
    wrapper.__str__ = symbol.__str__
    wrapper.__doc__ = symbol.__doc__

    return wrapper


def _wrap_class(symbol: type):
    return type(symbol.__name__, (symbol,), {
        "__repr__": lambda self: "<Nihonium Native Class, " + symbol.__name__ + ">",
        "__str__": symbol.__str__,
        "__doc__": symbol.__doc__,
        "__module__": symbol.__module__
    })