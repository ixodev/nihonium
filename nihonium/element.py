class Element:

    def __init__(self, line_str: str, *args, parent = None):
        self.line_str = line_str
        self.parent = parent

    def set_parent(self, parent):
        self.parent = parent

    def _repr(self, indent: int = 0, prefix: str = ""):
        s = f"{prefix}{self.__class__.__name__}:\n"

        n_attrs = len(self.__dict__)
        for i, (attr, value) in enumerate(self.__dict__.items()):
            is_last = i == n_attrs - 1
            attr_prefix = prefix + ("\t" if is_last else "|\t")
            s += f"{prefix}+-- {attr} = "

            if isinstance(value, Element):
                if hasattr(value, 'expression') and isinstance(value.expression, list) and all(not isinstance(v, Element) for v in value.expression):
                    vals = ", ".join(str(v) for v in value.expression)
                    s += f"[{vals}]\n"
                else:
                    s += "\n" + value._repr(indent + 1, attr_prefix)

            elif isinstance(value, list):
                s += "[\n"
                n_items = len(value)
                for j, item in enumerate(value):
                    is_item_last = j == n_items - 1
                    item_prefix = attr_prefix + ("\t" if is_item_last else "|\t")
                    if isinstance(item, Element):
                        s += item._repr(indent + 1, item_prefix)
                    else:
                        s += f"{item_prefix}{item}\n"
                s += f"{attr_prefix}]\n"

            else:
                s += f"{value}\n"

        return s + "\n"

    def ast_repr(self):
        return self._repr(0)

    def __repr__(self):
        return "(<" + self.__class__.__name__ + ">\t\"" + self.line_str.replace("\n", "")[:20] + "...\")"

    def __call__(self, program, scope_variables):
        #print(f"\n\n-- About to execute --")
        #print(self)
        #print("-- Scope Variables --")
        #print(scope_variables, "\n")
        #input("Continue > ")
        pass