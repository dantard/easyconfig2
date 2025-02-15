class EasyDependency:
    def __init__(self, master, func, **kwargs):
        self.master = master
        self.func = func

    def call(self, value):
        if value == "" or value is None:
            return False
        return self.func(value)


class EasyMandatoryDependency(EasyDependency):
    pass


class EasyPairDependency(EasyDependency):

    def __init__(self, master, slave, func, **kwargs):
        super().__init__(master, func, **kwargs)
        self.slave = [slave] if not isinstance(slave, (list, tuple, set)) else slave

    def get_slave(self):
        return self.slave
