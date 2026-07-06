from enum import Enum

class NihoniumExceptionType(str, Enum):
    UNDEFINED = "undefined"
    NO_MAIN_FUNCTION = "no_main_function"

class NihoniumException(Exception):
    def __init__(self, msg: str, error_type: NihoniumExceptionType = NihoniumExceptionType.UNDEFINED):
        super().__init__(msg)
        self.msg = msg
        self.error_type = error_type

    def get_cause(self):
        return self.error_type

    def is_cause(self, compared_value: NihoniumExceptionType):
        return self.error_type == compared_value


def error(msg, cause: NihoniumExceptionType = NihoniumExceptionType.UNDEFINED):
    raise NihoniumException(msg, cause)