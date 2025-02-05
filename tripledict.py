class TripleDict:
    def __init__(self):
        self.dict1 = {}
        self.dict2 = {}

    def add(self, node, widget, item):
        self.dict1[node] = (widget, item)
        self.dict2[widget] = (node, item)

    def get(self, key):
        return self.dict1.get(key, self.dict2.get(key, None))

    def clear(self):
        self.dict1.clear()
        self.dict2.clear()

    def __getitem__(self, item):
        return self.get(item)

    def items1(self):
        return self.dict1.items()

    def items2(self):
        return self.dict2.items()

    def keys1(self):
        return self.dict1.keys()

    def keys2(self):
        return self.dict2.keys()
