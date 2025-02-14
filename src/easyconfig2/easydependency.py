class EasyDependency:
    GREATER = 1
    SMALLER = 2
    NOT_EQUAL = 4
    NOT_EMPTY = 8

    def __init__(self, master, kind, value=None):
        self.master = master
        self.kind = kind
        self.value = value


class EasyPairDependency(EasyDependency):

    def __init__(self, master, slave, kind, value=None):
        super().__init__(master, kind, value)
        self.slave = [slave] if not isinstance(slave, (list, tuple, set)) else slave
