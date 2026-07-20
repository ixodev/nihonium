from typing import Any
from .defs import *
from .error import *

class Token:
    def __init__(self, type: str, value: Any = None):
        self.type = type
        self.value = value

    def __repr__(self):
        if self.value is not None:
            return self.type + ":" + str(self.value).replace('\n', '\\n').replace('\t', '\\t')
        return self.type

    def is_type(self, token_type: str):
        return self.get_type() == token_type

    def get_type(self):
        return self.type

    def get_value(self):
        return self.value

    def has_value(self):
        return not self.value is None



class Lexer:
    def __init__(self, text: str, inline: bool=False):
        self.text = text
        self.pos = None
        self.inline = inline
        self.current_char = None
        self.reset()

    def reset(self):
        self.pos = 0
        self.current_char = self.text[self.pos] if self.text else None

    def forward(self):
        self.pos += 1

        if self.pos < len(self.text):
            self.current_char = self.text[self.pos]
            return

        self.current_char = None

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char in " \t":
            self.forward()

    def number(self):
        result = ""

        while self.current_char is not None and (self.current_char.isdigit() or self.current_char == "."):
            result += self.current_char
            self.forward()

        if "." in result:
            return Token(TOKEN_TYPE_FLOAT, float(result))

        return Token(TOKEN_TYPE_INT, int(result))

    def string(self):
        self.forward()

        result = "\""

        while self.current_char is not None and (self.current_char != "\""):
            if self.current_char == "\n":
                error("string was never closed")

            if self.current_char == "\\":
                if self.text[self.pos + 1] is not None and self.text[self.pos + 1] == "\"":
                    result += "\""
                elif self.text[self.pos + 1] is not None and self.text[self.pos + 1] == "n":
                    result += "\n"
                elif self.text[self.pos + 1] is not None  and self.text[self.pos + 1] == "t":
                    result += "\t"

                self.forward()
                self.forward()
            else:
                result += self.current_char
                self.forward()

        self.forward()

        return Token(TOKEN_TYPE_STRING, result + "\"")


    def identifier(self):
        result = ""

        while self.current_char is not None and (self.current_char.isalnum() or self.current_char in [".", "_"]):
            result += self.current_char
            self.forward()

        if result in KEYWORDS:
            return Token(KEYWORDS[result])

        return Token(TOKEN_TYPE_IDENT, result)

    def single_char(self):
        result = ""

        if self.current_char is not None:
            result = self.current_char
            self.forward()

        return Token(SINGLE_CHAR_TOKENS[result])

    def restructure_braces(self, tokens):
        i = 0
        while i < len(tokens):
            token_set = tokens[i]

            if len(token_set) == 1 and token_set[0].is_type(TOKEN_TYPE_LBRACE)and i != 0:
                token = tokens.pop(i)[0]
                tokens[i - 1].append(token)
            else:
                i += 1

    def tokenize(self):
        tokens = []
        current_line = []

        while self.current_char is not None:

            if self.current_char == "\n":
                tokens.append(current_line)
                current_line = []
                self.forward()
                continue

            if self.current_char in " \t":
                self.skip_whitespace()
                continue

            if self.current_char.isdigit():
                current_line.append(self.number())
                continue

            if self.current_char == "\"":
                current_line.append(self.string())
                continue

            if self.current_char.isalpha() or self.current_char == "_":
                current_line.append(self.identifier())
                continue

            # WARNING POSSIBILITY OF UNEXPECTED SIDE EFFECTS /!\
            # if self.text[self.pos + 1] is not None:
            if len(self.text) > self.pos + 1:
                combined = self.current_char + self.text[self.pos + 1]
                if combined in MULTIPLE_CHAR_OPERATORS:
                    current_line.append(Token(MULTIPLE_CHAR_OPERATORS[combined]))
                    self.forward()
                    self.forward()
                    continue

            if self.current_char in DOUBLE_CHAR_OPERATORS and self.pos + 1 < len(self.text):
                if self.current_char == self.text[self.pos + 1]:
                    current_line.append(Token(DOUBLE_CHAR_OPERATORS[self.current_char]))
                    self.forward()
                    self.forward()
                    continue

            if self.current_char in SINGLE_CHAR_TOKENS:
                current_line.append(self.single_char())
                continue

        self.reset()

        if self.inline:
            if len(tokens) == 0:
                tokens.append(current_line)

            return tokens[0]

        tokens = [token for token in tokens if len(token) > 0]
        self.restructure_braces(tokens)
        return tokens