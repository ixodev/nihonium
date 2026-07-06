import typing
import os
import itertools
import math
from typing import Optional

from .error import error


class _PrimitiveTypesMappingRegistry:

    def __init__(self) -> None:
        self._data = {}

    def register(self, target: object, mapped: typing.Optional[type]):
        if target in self._data:
            raise RuntimeError(f"{target!r} is already mapped.")
        self._data[target] = mapped

    def get(self, target: object):
        return self._data.get(target)

    def contains(self, target: object) -> bool:
        return target in self._data

    def contains_value(self, target):
        return target in self._data.values()

    def get_key(self, value):
        try:
            return [k for k, v in self._data.items() if v is value][0]
        except IndexError:
            return None


__registry = _PrimitiveTypesMappingRegistry()


def is_mapped(object: typing.Optional[type]):
    return __registry.contains(object)

def get_mapped_type(object: typing.Optional[type]):
    return __registry.get(object)


def map_primitive_type_to(other_type: typing.Optional[type]):

    def decorator(type_to_map: type):
        __registry.register(other_type, type_to_map)
        return type_to_map

    return decorator


class Object:

    _id_counter = itertools.count()

    def __init__(self):
        self._id = next(self._id_counter)

    def reference_equals(self, other):
        return Bool(other.get_id() == self._id)

    def get_id(self):
        return self._id

    def __repr__(self):
        return f"<{self.__class__.__name__} ({self.get_id()})>"

    def convert_python(self):
        pass
    
    def is_primitive(self):
        return issubclass(self.__class__, (Primitive,))

    def is_callable(self):
        return issubclass(self.__class__, (CallableObject,))

    def is_function(self):
        return type(self).__name__ == "Function"

    def is_native_function(self):
        return type(self).__name__ == "NativeFunction"

    def is_lambda_function(self):
        return type(self).__name__ == "LambdaFunction"


class Primitive(Object):
    def __init__(self):
        super().__init__()


class CallableObject(Object):
    def __init__(self):
        super().__init__()

    def __call__(self, program, scope_variables):
        return self.call(program, scope_variables)

    def call(self, program, scope_variables):
        pass

    def get_parameters(self):
        return getattr(self, "parameters", [])

    def get_num_parameters(self):
        return len(self.get_parameters())

class NoPrimitive(Object):
    def __init__(self):
        super().__init__()

    def convert_nihonium(self):
        pass

class Null(Object):
    def __init__(self):
        super().__init__()

    def convert_python(self):
        return None

    def __repr__(self):
        return "null"

    def __str__(self):
        return "null"

    def __eq__(self, other):
        return Bool(isinstance(other, Null))

    def __ne__(self, other):
        return self.__eq__(other).lognot()

class RealNumber(Primitive):
    def __init__(self, value: typing.Union[int, float]):
        super().__init__()
        self.value = value

    def convert_python(self):
        return self.value


@map_primitive_type_to(float)
# ---------------- Float ----------------
class Float(RealNumber):
    def __init__(self, value: typing.Union[int, float]):
        super().__init__(value)
        self.value = value

    def __repr__(self):
        return f"{self.__class__.__name__}({self.value})"

    def __str__(self):
        return str(self.value)

    def __bool__(self):
        return bool(self.value)

    # ---------- Coercion ----------
    def _coerce(self, other):
        if isinstance(other, Float):
            return other.value
        return NotImplemented

    # ---------- Arithmetic ----------
    def __add__(self, other):
        val = self._coerce(other)
        if val is NotImplemented:
            return NotImplemented
        return Float(self.value + val)

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        val = self._coerce(other)
        if val is NotImplemented:
            return NotImplemented
        return Float(self.value - val)

    def __rsub__(self, other):
        if isinstance(other, Float):
            return Float(other.value - self.value)
        return NotImplemented

    def __mul__(self, other):
        val = self._coerce(other)
        if val is NotImplemented:
            return NotImplemented
        return Float(self.value * val)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        val = self._coerce(other)
        if val is NotImplemented:
            return NotImplemented
        if val == 0:
            raise ZeroDivisionError
        return Float(self.value / val)

    def __rtruediv__(self, other):
        if isinstance(other, Float):
            if self.value == 0:
                raise ZeroDivisionError
            return Float(other.value / self.value)
        return NotImplemented

    def __floordiv__(self, other):
        val = self._coerce(other)
        if val is NotImplemented:
            return NotImplemented
        if val == 0:
            raise ZeroDivisionError
        return Float(self.value // val)

    def __rfloordiv__(self, other):
        if isinstance(other, Float):
            if self.value == 0:
                raise ZeroDivisionError
            return Float(other.value // self.value)
        return NotImplemented

    def __mod__(self, other):
        val = self._coerce(other)
        if val is NotImplemented:
            return NotImplemented
        if val == 0:
            raise ZeroDivisionError
        return Float(self.value % val)

    def __rmod__(self, other):
        if isinstance(other, Float):
            if self.value == 0:
                raise ZeroDivisionError
            return Float(other.value % self.value)
        return NotImplemented

    def __pow__(self, other):
        val = self._coerce(other)
        if val is NotImplemented:
            return NotImplemented
        return Float(self.value ** val)

    def __rpow__(self, other):
        if isinstance(other, Float):
            return Float(other.value ** self.value)
        return NotImplemented

    # ---------- Unary ----------
    def __neg__(self):
        return Float(-self.value)

    def __pos__(self):
        return Float(+self.value)

    def __abs__(self):
        return Float(abs(self.value))

    # ---------- Comparison ----------
    def __eq__(self, other):
        if isinstance(other, Float) or isinstance(other, Int):
            return Bool(self.value == other.value)
        return False

    def __ne__(self, other):
        return Bool(not self.__eq__(other))

    def __lt__(self, other):
        if isinstance(other, Float) or isinstance(other, Int):
            return Bool(self.value < other.value)
        return NotImplemented

    def __le__(self, other):
        if isinstance(other, Float) or isinstance(other, Int):
            return Bool(self.value <= other.value)
        return NotImplemented

    def __gt__(self, other):
        if isinstance(other, Float) or isinstance(other, Int):
            return Bool(self.value > other.value)
        return NotImplemented

    def __ge__(self, other):
        if isinstance(other, Float) or isinstance(other, Int):
            return Bool(self.value >= other.value)
        return NotImplemented

    # ---------- Hash ----------
    def __hash__(self):
        return hash(self.value)



@map_primitive_type_to(int)
class Int(Float):
    def __init__(self, value: int):
        super().__init__(int(value))

    def __repr__(self):
        return f"Int({int(self.value)})"

    def __hash__(self):
        return hash(int(self.value))

    # ---------- Arithmetic Overrides ----------
    def __add__(self, other):
        if isinstance(other, Int):
            return Int(int(self.value + other.value))
        return super().__add__(other)

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if isinstance(other, Int):
            return Int(int(self.value - other.value))
        return super().__sub__(other)

    def __rsub__(self, other):
        if isinstance(other, Int):
            return Int(int(other.value - self.value))
        return super().__rsub__(other)

    def __mul__(self, other):
        if isinstance(other, Int):
            return Int(int(self.value * other.value))
        return super().__mul__(other)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        if isinstance(other, Int):
            if other.value == 0:
                raise ZeroDivisionError
            return Float(self.value / other.value)
        return super().__truediv__(other)

    def __rtruediv__(self, other):
        if isinstance(other, Int):
            if self.value == 0:
                raise ZeroDivisionError
            return Float(other.value / self.value)
        return super().__rtruediv__(other)

    def __floordiv__(self, other):
        if isinstance(other, Int):
            if other.value == 0:
                raise ZeroDivisionError
            return Int(int(self.value // other.value))
        return super().__floordiv__(other)

    def __rfloordiv__(self, other):
        if isinstance(other, Int):
            if self.value == 0:
                raise ZeroDivisionError
            return Int(int(other.value // self.value))
        return super().__rfloordiv__(other)

    def __mod__(self, other):
        if isinstance(other, Int):
            if other.value == 0:
                raise ZeroDivisionError
            return Int(int(self.value % other.value))
        return super().__mod__(other)

    def __rmod__(self, other):
        if isinstance(other, Int):
            if self.value == 0:
                raise ZeroDivisionError
            return Int(int(other.value % self.value))
        return super().__rmod__(other)

    def __pow__(self, other):
        if isinstance(other, Int):
            return Int(int(self.value ** other.value))
        return super().__pow__(other)

    def __rpow__(self, other):
        if isinstance(other, Int):
            return Int(int(other.value ** self.value))
        return super().__rpow__(other)

    def __abs__(self):
        return Float(abs(self.value))

    # ---------- Comparison ----------
    def __eq__(self, other):
        if isinstance(other, Int) or isinstance(other, Float):
            return Bool(self.value == other.value)
        return False

    def __ne__(self, other):
        return Bool(not self.__eq__(other))

    def __lt__(self, other):
        if isinstance(other, Int) or isinstance(other, Float):
            return Bool(self.value < other.value)
        return NotImplemented

    def __le__(self, other):
        if isinstance(other, Int) or isinstance(other, Float):
            return Bool(self.value <= other.value)
        return NotImplemented

    def __gt__(self, other):
        if isinstance(other, Int) or isinstance(other, Float):
            return Bool(self.value > other.value)
        return NotImplemented

    def __ge__(self, other):
        if isinstance(other, Int) or isinstance(other, Float):
            return Bool(self.value >= other.value)
        return NotImplemented

    # ---------- Bitwise ----------
    def __and__(self, other):
        if isinstance(other, Int):
            return Int(self.value & other.value)
        return NotImplemented

    def __rand__(self, other):
        return self.__and__(other)

    def __or__(self, other):
        if isinstance(other, Int):
            return Int(self.value | other.value)
        return NotImplemented

    def __ror__(self, other):
        return self.__or__(other)

    def __xor__(self, other):
        if isinstance(other, Int):
            return Int(self.value ^ other.value)
        return NotImplemented

    def __rxor__(self, other):
        return self.__xor__(other)

    def __lshift__(self, other):
        if isinstance(other, Int):
            return Int(self.value << other.value)
        return NotImplemented

    def __rlshift__(self, other):
        if isinstance(other, Int):
            return Int(other.value << self.value)
        return NotImplemented

    def __rshift__(self, other):
        if isinstance(other, Int):
            return Int(self.value >> other.value)
        return NotImplemented

    def __rrshift__(self, other):
        if isinstance(other, Int):
            return Int(other.value >> self.value)
        return NotImplemented

    def __invert__(self):
        return Int(~self.value)

    # ---------- Unary ----------
    def __neg__(self):
        return Int(-self.value)

    def __pos__(self):
        return Int(+self.value)


@map_primitive_type_to(complex)
class Complex(Primitive):
    def __init__(self, from_number: typing.Optional[complex] = None, real: typing.Optional[RealNumber] = None, imag: typing.Optional[RealNumber] = None):
        super().__init__()

        if from_number is not None:
            self.real = convert_nihonium(from_number.real)
            self.imag = convert_nihonium(from_number.imag)
        else:
            self.real = real if real is not None else Int(0)
            self.imag = imag if imag is not None else Int(0)

    def __repr__(self):
        return f"Complex({self.real}, {self.imag})"

    def __str__(self):
        return f"{self.real} + {self.imag}i"

    def convert_python(self):
        return complex(self.real.convert_python(), self.imag.convert_python())

    def is_null(self):
        return self.real.value == 0 and self.imag.value == 0

    def __add__(self, other):
        if isinstance(other, Complex):
            return Complex(None, self.real + other.real, self.imag + other.imag)
        elif issubclass(other.__class__, RealNumber):
            return Complex(None, self.real + other, self.imag)

        return NotImplemented

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if isinstance(other, Complex):
            return Complex(None, self.real - other.real, self.imag - other.imag)
        elif issubclass(other.__class__, RealNumber):
            return Complex(None, self.real - other, self.imag)

        return NotImplemented

    def __rsub__(self, other):
        if isinstance(other, Complex):
            return Complex(None, other.real - self.real, other.imag - self.imag)
        elif issubclass(other.__class__, RealNumber):
            return Complex(None, other - self.real, self.imag)

        return NotImplemented

    def __mul__(self, other):
        if isinstance(other, Complex):
            return Complex(None, self.real * other.real - self.imag * other.imag, self.real * other.imag + self.imag * other.real)
        elif issubclass(other.__class__, RealNumber):
            return Complex(None, self.real * other, self.imag * other)

        return NotImplemented

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):

        if isinstance(other, Complex):

            if other.is_null():
                error("cannot divide by zero complex number")

            denominator = (
                    other.real * other.real +
                    other.imag * other.imag
            )

            real = (
                           self.real * other.real +
                           self.imag * other.imag
                   ) / denominator

            imag = (
                           self.imag * other.real -
                           self.real * other.imag
                   ) / denominator

            return Complex(None, real, imag)

        elif issubclass(other.__class__, RealNumber):

            if other.value == 0:
                error("division by zero")

            return Complex(None,
                self.real / other,
                self.imag / other
            )

        return NotImplemented

    def __rtruediv__(self, other):

        if self.is_null():
            error("division by zero complex number")

        denominator = (
                self.real * self.real +
                self.imag * self.imag
        )

        if isinstance(other, Complex):

            real = (
                           other.real * self.real +
                           other.imag * self.imag
                   ) / denominator

            imag = (
                           other.imag * self.real -
                           other.real * self.imag
                   ) / denominator

            return Complex(None, real, imag)

        elif issubclass(other.__class__, RealNumber):

            real = (
                           other * self.real
                   ) / denominator

            imag = (
                           -other * self.imag
                   ) / denominator

            return Complex(None, real, imag)

        return NotImplemented


@map_primitive_type_to(bool)
class Bool(Primitive):
    def __init__(self, value: typing.Union[int, bool]):
        super().__init__()
        self.value = bool(value)

    def __bool__(self):
        return self.value

    def convert_python(self):
        return self.value

    def logand(self, other):
        if isinstance(other, Bool):
            return Bool(self.value and other.value)

        return other.logand(self)

    def logor(self, other):
        if isinstance(other, Bool):
            return Bool(self.value or other.value)

        return other.logor(self)

    def lognot(self):
        return Bool(not self.value)

    def __or__(self, other):
        if isinstance(other, Bool):
            return Bool(self.value | other.value)
        return NotImplemented

    def __ror__(self, other):
        if isinstance(other, Bool):
            return Bool(self.value | other.value)
        return NotImplemented

    def __and__(self, other):
        if isinstance(other, Bool):
            return Bool(self.value & other.value)
        return NotImplemented

    def __rand__(self, other):
        if isinstance(other, Bool):
            return Bool(self.value & other.value)
        return NotImplemented

    def __xor__(self, other):
        if isinstance(other, Bool):
            return Bool(self.value ^ other.value)
        return NotImplemented

    def __rxor__(self, other):
        if isinstance(other, Bool):
            return Bool(self.value ^ other.value)
        return NotImplemented

    def __eq__(self, other):
        if isinstance(other, Bool):
            return Bool(self.value == other.value)
        return NotImplemented

    def __ne__(self, other):
        return self.__eq__(other).lognot()

    def __repr__(self):
        return f"Bool({self.value})"

    def __str__(self):
        return str(self.value).lower()

    # ---------- Hash ----------
    def __hash__(self):
        return hash(self.value)


@map_primitive_type_to(str)
class String(Object):
    def __init__(self, value: str):
        super().__init__()
        self.value = value

    def convert_python(self):
        return self.value

    def __repr__(self):
        return f"String(\"{self.value}\")"

    def __str__(self):
        return self.value

    def __eq__(self, other):
        if isinstance(other, String):
            return Bool(self.value == other.value)
        return NotImplemented

    def __ne__(self, other):
        return self.__eq__(other).lognot()

    def __add__(self, other):
        if isinstance(other, String):
            return String(self.value + other.value)
        return NotImplemented

    def __radd__(self, other):
        if isinstance(other, String):
            return String(other.value + self.value)
        return NotImplemented

    def __getitem__(self, index):
        if isinstance(index, int):
            return String(self.value[index])
        elif isinstance(index, Int):
            return String(self.value[index.convert_python()])

        return NotImplemented

    def __len__(self):
        return Int(len(self.value))

    def __hash__(self):
        return hash(self.value)



class IOStream(NoPrimitive):
    def __init__(self, fd: int):
        super().__init__()
        self._fd = fd
        self._buffer = bytearray()

    def get_real_fd(self):
        return self._fd

    def flush(self):
        self._buffer.clear()

    def close(self):
        os.close(self._fd)

    def __repr__(self):
        return f"<fd: {self._fd}, buffer: {self._buffer}>"

    def convert_python(self):
        return self

    def convert_nihonium(self):
        return self


class OutputStream(IOStream):
    def __init__(self, fd: int):
        super().__init__(fd)

    def write_buffer(self, data):
        if isinstance(data, str):
            data = data.encode()

        self._buffer.extend(bytearray(data))

    def write(self):

        if not self._buffer:
            return 0

        total_written = 0

        while self._buffer:
            written = os.write(self._fd, self._buffer)
            if written == 0:
                return -1

            self._buffer = self._buffer[written:]
            total_written += written

        return total_written

    def __repr__(self):
        return "output " + super().__repr__()


class InputStream(IOStream):
    def __init__(self, fd: int):
        super().__init__(fd)

    def read_buffer(self, n: int = -1):
        to_read = n

        if n == -1 or n > len(self._buffer):
            to_read = len(self._buffer)

        data = self._buffer[:to_read]
        del self._buffer[:to_read]

        return bytearray(data)

    def read(self, size: int = 4096):
        chunk = os.read(self._fd, size)
        self._buffer.extend(chunk)
        return len(chunk)

    def __repr__(self):
        return "input " + super().__repr__()


@map_primitive_type_to(list)
class ArrayList(Primitive):

    def __repr__(self):
        return f"List({self.elements})"

    def __str__(self):
        stringbuilder = "["

        for element in self.elements:
            if type(element) is String:
                stringbuilder += f"\"{str(element)}\""
            else:
                stringbuilder += str(element)

            if not (element is self.elements[-1]):
                stringbuilder += ", "

        return stringbuilder + "]"


    def __init__(self, elements: typing.List[typing.Any]):
        super().__init__()
        self.elements = elements

    def convert_python(self):
        return [element.convert_python() for element in self.elements]


@map_primitive_type_to(dict)
class Dictionary(Primitive):

    def __repr__(self):
        return f"Dictionary({self.elements})"

    def __str__(self):
        return str(self.elements)

    def __init__(self, elements: typing.Dict[typing.Any, typing.Any]):
        super().__init__()

        self.elements = {
            convert_nihonium(key): convert_nihonium(val)
            for key, val in elements.items()
        }

    def convert_python(self):
        return {
            key.convert_python(): val.convert_python()
            for key, val in self.elements.items()
        }



def is_primitive(python_object: typing.Any):
    return is_mapped(type(python_object))

def convert_nihonium(python_object: typing.Any):
    if python_object is None:
        return Null()

    if is_primitive(python_object):
        return get_mapped_type(type(python_object))(python_object)

    if type(python_object) is NoPrimitive or issubclass(type(python_object), NoPrimitive):
        return python_object.convert_nihonium()

    print(f"Warning, raw python object \"{python_object}\" of type \"{type(python_object)}\" is being passed to Nihonium runtime")
    return python_object
