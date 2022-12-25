import random
from generator import GeneratorBase, Const


class Random(GeneratorBase):
    def __init__(self, min=Const(0), max=Const(1), type=Const("float")) -> None:
        self._min = min
        self._max = max
        self._type = type

    def get(self):
        min = self._min.get()
        max = self._max.get()

        if self._type.get() == "int":
            return random.randint(min, max)
        else:
            return (max - min) * random.random() + min

    def update(self):
        self._min.update()
        self._max.update()
        self._type.update()
