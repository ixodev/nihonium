import typing

from nihonium.base_types import InputStream, OutputStream, IOStream
from nexcellence.frame import Locals

from common import FileMode, StreamType

import sys
import heapq


# =========================================================
# STREAM REGISTRY (factory)
# =========================================================

STREAM_TYPE_REGISTRY = {}

def register_stream_type(stream_type: int):
    def decorator(cls: type):
        STREAM_TYPE_REGISTRY[stream_type] = cls
        return cls
    return decorator


def create_stream(stream_type: int, *args, **kwargs):
    try:
        cls = STREAM_TYPE_REGISTRY[stream_type]
    except KeyError:
        raise ValueError(f"Unknown stream type: {stream_type}")
    return cls(*args, **kwargs)


@register_stream_type(StreamType.STDIN)
class StdIn(InputStream):

    __is_open = False

    def __init__(self):
        if not StdIn.__is_open:
            super().__init__(sys.stdin.fileno())
            StdIn.__is_open = True
            return

        print("stdin already open")


@register_stream_type(StreamType.STDOUT)
class StdOut(OutputStream):

    __is_open = False

    def __init__(self):
        if not StdOut.__is_open:
            super().__init__(sys.stdout.fileno())
            StdOut.__is_open = True
            return

        print("stdout already open")


@register_stream_type(StreamType.STDERR)
class StdErr(OutputStream):

    __is_open = False

    def __init__(self):
        if not StdErr.__is_open:
            super().__init__(sys.stderr.fileno())
            StdErr.__is_open = True
            return

        print("stderr already open")


@register_stream_type(StreamType.FILE)
class FileSystemStream(InputStream, OutputStream):

    def __init__(self, file: str, mode: FileMode):
        self.mode = mode
        self.mode_str = ""

        if mode.mode_str == "":

            if mode & FileMode.READ:
                self.mode_str += FileMode.READ.mode_str
            if mode & FileMode.WRITE:
                self.mode_str += FileMode.WRITE.mode_str
            if mode & FileMode.APP:
                self.mode_str += FileMode.APP.mode_str
            if mode & FileMode.BIN:
                self.mode_str += FileMode.BIN.mode_str

        else:
            self.mode_str = self.mode.mode_str

        self.file_handle = open(str(file), str(self.mode_str))
        fd = self.file_handle.fileno()

        IOStream.__init__(self, fd)

    def close(self):
        self.file_handle.close()



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
    def open_stream(stream_type: int, *args, **kwargs) -> int:
        stream = create_stream(stream_type, *args, **kwargs)

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
