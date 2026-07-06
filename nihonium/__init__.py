__doc__ = """

Official API of the Nihonium Programming Language
Special version of the API of the Nihonium Programming Language, only used by the official Nihonium interpreter

Description
-----------
This module defines the stable public interface of the Nihonium runtime
when embedded in a Python environment.

It provides access to:

- Core base types
- The Python <-> Nihonium interoperability layer
- Native exported functions and classes

Stability
-------
Only symbols imported into this module are considered part of the
official public API and are guaranteed to follow semantic versioning.

Any module, attribute, or symbol not exposed here is considered
internal implementation detail and may change without notice.

Version
-------
See __version__ for the current runtime version.

"""

from .base_types import *
from .inline import *
from .config import *
from .error import *
from .module import *
from .lexer import *
from .program_cleaner import *
from .export_native import *


__author__ = "Younes Bendimerad (aka ixodev)"
__version__ = "0.1.0"

__all__ = [
    "export_symbol",
    "Object",
    "Primitive",
    "NoPrimitive",
    "Null",
    "RealNumber",
    "Float",
    "Int",
    "Complex",
    "Bool",
    "String",
    "ArrayList",
    "Dictionary",
    "IOStream",
    "OutputStream",
    "InputStream",
    "SingleLineExecutor",
    "InlineExecutor",
    "NihoniumException"
]
