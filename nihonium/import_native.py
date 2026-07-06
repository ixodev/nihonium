import importlib
from .error import error
from .function import NativeFunction
from .defs import STANDARD_NATIVE_MODULE_NAME


def import_natives(module_name: str, native_module_name: str):

    native_functions = {}

    try:
        module = importlib.import_module(__package__ + "." + native_module_name if native_module_name == STANDARD_NATIVE_MODULE_NAME else native_module_name)

    except ImportError:
        error(f"Could not import native module {native_module_name}")


    for name in getattr(module, "exported_symbols", {}):

        symbol = getattr(module, "exported_symbols", {name: None})[name]

        if symbol is None:
            error(f"could not load module {native_module_name}")

        if getattr(symbol, "_export_for_all", False):
            if symbol._export_for_all:
                native_functions.update({name: NativeFunction(symbol, None, export_for_all=True)})
                continue

        if getattr(symbol, "_allowed_modules", False):
            if module_name in symbol._allowed_modules:
                native_functions.update({name: NativeFunction(symbol, symbol._allowed_modules)})


    return native_functions