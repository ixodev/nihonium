import typing

from common_runtime.base_types import InputStream, OutputStream
from frame import Locals

import sys
import heapq


# =========================================================
# STREAM REGISTRY (factory)
# =========================================================

STREAM_TYPE_REGISTRY = {}

def register_type(name: str):
    def decorator(cls: type):
        STREAM_TYPE_REGISTRY[name] = cls
        return cls
    return decorator


def create_stream(name: str, *args, **kwargs):
    try:
        cls = STREAM_TYPE_REGISTRY[name]
    except KeyError:
        raise ValueError(f"Unknown stream type: {name}")
    return cls(*args, **kwargs)


@register_type("stdin")
class StdIn(InputStream):

    __is_open = False

    def __init__(self):
        if not StdIn.__is_open:
            super().__init__(sys.stdin.fileno())
            StdIn.__is_open = True


@register_type("stdout")
class StdOut(OutputStream):

    __is_open = False

    def __init__(self):
        if not StdOut.__is_open:
            super().__init__(sys.stdout.fileno())
            StdOut.__is_open = True


@register_type("stderr")
class StdErr(OutputStream):

    __is_open = False

    def __init__(self):
        if not StdErr.__is_open:
            super().__init__(sys.stderr.fileno())
            StdErr.__is_open = True


# =========================================================
# IO / FILE DESCRIPTOR TABLE
# =========================================================

class IO:
    """
    VM-level file descriptor manager (Unix-like behavior).
    """

    # fd -> IOStream
    streams = Locals()

    # next never-used fd
    next_fd: int = 0

    # freed fds (min-heap)
    free_fds: list[int] = []


    # -----------------------------------------------------
    # INIT STANDARD STREAMS
    # -----------------------------------------------------

    @staticmethod
    def open_standard_streams():
        std = [StdIn(), StdOut(), StdErr()]

        for fd, stream in enumerate(std):
            IO.streams.store(fd, stream)

        IO.next_fd = 3  # stdin/out/err are reserved


    # -----------------------------------------------------
    # FD ALLOCATION (Unix-like)
    # -----------------------------------------------------

    @staticmethod
    def allocate_fd() -> int:
        # reuse smallest free fd if available
        if IO.free_fds:
            return heapq.heappop(IO.free_fds)

        fd = IO.next_fd
        IO.next_fd += 1
        return fd


    @staticmethod
    def free_fd(fd: int):
        heapq.heappush(IO.free_fds, fd)


    # -----------------------------------------------------
    # OPEN STREAM
    # -----------------------------------------------------

    @staticmethod
    def open_stream(type_name: str, *args, **kwargs) -> int:
        stream = create_stream(type_name, *args, **kwargs)

        fd = IO.allocate_fd()
        IO.streams.store(fd, stream)

        return fd


    # -----------------------------------------------------
    # CLOSE STREAM
    # -----------------------------------------------------

    @staticmethod
    def close_stream(fd: int):
        stream = IO.streams.free(fd)
        stream.close()

        IO.free_fd(fd)

    @staticmethod
    def write(fd: int, value: typing.Any):
        stream = IO.streams.load(fd)

        stream.write_buffer(str(value))
        stream.write()

    @staticmethod
    def read(fd: int, n: int = -1):
        stream = IO.streams.load(fd)
        stream.read()

        return stream.read_buffer(n).decode()
