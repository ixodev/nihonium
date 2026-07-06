import sys
import os
import math
import cmath
import time
from typing import *
from .error import *
from .export_native import *
from .base_types import *


@export_symbol(allowed_modules=["stdlib.stdio"])
def createOutputStream(fd: int):
    return OutputStream(fd)

@export_symbol(allowed_modules=["stdlib.stdio"])
def createInputStream(fd: int):
    return InputStream(fd)

@export_symbol(allowed_modules=["stdlib.stdio"])
def standardOutputFileno():
    return sys.stdout.fileno()

@export_symbol(allowed_modules=["stdlib.stdio"])
def standardInputFileno():
    return sys.stdin.fileno()

@export_symbol(allowed_modules=["stdlib.stdio"])
def standardErrorFileno():
    return sys.stderr.fileno()


@export_symbol(allowed_modules=["stdlib.math"], nihonium_name="abs")
def _abs(x: Union[float, int, complex]):
    return abs(x)

@export_symbol(allowed_modules=["stdlib.math"], nihonium_name="pow")
def _pow(b: Union[float, int, complex], e: Union[float, int, complex]):

    if isinstance(e, (int, float)):
        return pow(b, e)

    elif isinstance(e, complex):
        if b == 0:
            return 0

        if b > 0:
            return exp(ln(b) * e)

        elif b < 0:
            r = abs(e)
            base = abs(b)
            lnb = ln(base)
            arg = phase(e)
            c = math.cos(arg)
            s = math.sin(arg)

            return exp(complex(r * (lnb * c - math.pi * s), r * (math.pi * c + lnb * s)))

@export_symbol(allowed_modules=["stdlib.math"])
def phase(z: Union[float, int, complex]):
    if isinstance(z, (float, int)):
        if z == 0:
            error("Cannot take phase of null real number")
        if z < 0:
            return math.pi
        return 0

    elif isinstance(z, complex):
        if z.imag == 0 and z.real == 0:
            error("Cannot take phase of null complex number")
        if z.imag == 0:
            if z.real < 0:
                return math.pi
            return 0
        if z.real == 0:
            if z.imag < 0:
                return -math.pi / 2
            return math.pi / 2

        return cmath.phase(z)

    error(f"phase function expected pure real / complex number but {z} was given")

@export_symbol(allowed_modules=["stdlib.math"])
def sqrt(x: Union[float, int]):
    return math.sqrt(x)

@export_symbol(allowed_modules=["stdlib.math"])
def exp(x: Union[float, int, complex]):
    if isinstance(x, (float, int)):
        return math.exp(x)

    real = math.exp(x.real) * math.cos(x.imag)
    imag = math.exp(x.real) * math.sin(x.imag)

    eps = 1e-12

    if abs(real) < eps:
        real = 0.0

    if abs(imag) < eps:
        imag = 0.0

    return complex(real, imag)

@export_symbol(allowed_modules=["stdlib.math"])
def ln(x: Union[float, int]):
    return math.log(x)

@export_symbol(allowed_modules=["stdlib.math"])
def cos(x: Union[float, int]):
    return math.cos(x)

@export_symbol(allowed_modules=["stdlib.math"])
def sin(x: Union[float, int]):
    return math.sin(x)

@export_symbol(allowed_modules=["stdlib.math"])
def tan(x: Union[float, int]):
    return math.tan(x)

@export_symbol(allowed_modules=["stdlib.math"])
def acos(x: Union[float, int]):
    return math.acos(x)

@export_symbol(allowed_modules=["stdlib.math"])
def asin(x: Union[float, int]):
    return math.asin(x)

@export_symbol(allowed_modules=["stdlib.math"])
def atan(x: Union[float, int]):
    return math.atan(x)

@export_symbol(allowed_modules=["stdlib.math"])
def piApproximation():
    return math.pi

@export_symbol(allowed_modules=["stdlib.math"])
def eApproximation():
    return math.e

@export_symbol(export_for_all=True)
def roundFloat(x: Union[float, int, bool]):
    return round(x)

@export_symbol(export_for_all=True)
def roundInt(x: Union[float, int, bool]):
    return int(round(x))

@export_symbol(export_for_all=True)
def floatToInt(x: float):
    return int(x)

@export_symbol(export_for_all=True)
def intToFloat(x: Union[int, float]):
    return float(x)

@export_symbol(allowed_modules=["stdlib.time"])
def getTime():
    return time.time()

@export_symbol(allowed_modules=["stdlib.time"])
def getDateTime():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

@export_symbol(allowed_modules=["stdlib.time"])
def getCurrentYear():
    return time.localtime().tm_year

@export_symbol(allowed_modules=["stdlib.time"])
def getCurrentMonth():
    return time.localtime().tm_mon

@export_symbol(allowed_modules=["stdlib.time"])
def getCurrentMonthDay():
    return time.localtime().tm_mday

@export_symbol(allowed_modules=["stdlib.time"])
def getCurrentWeekDay():
    return time.localtime().tm_wday

@export_symbol(allowed_modules=["stdlib.time"])
def getCurrentYearDay():
    return time.localtime().tm_yday

@export_symbol(allowed_modules=["stdlib.time"])
def getCurrentWeekDayString():
    return ["monday", "tuesday", "wednesday", "thursday", "saturday", "sunday"][getCurrentWeekDay()]

@export_symbol(allowed_modules=["stdlib.time"])
def getCurrentMinutes():
    return time.localtime().tm_min

@export_symbol(allowed_modules=["stdlib.time"])
def getCurrentSeconds():
    return time.localtime().tm_sec

@export_symbol()
def system(cmd: str):
    return os.system(cmd)




