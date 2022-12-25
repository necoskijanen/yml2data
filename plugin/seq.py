from generator import GeneratorBase, Const
import sys


def get_default(obj, default):
    if obj is not None:
        return obj
    else:
        return Const(default)


class Seq(GeneratorBase):

    def __init__(self, min=Const(0), max=Const(sys.maxsize), step=Const(1)) -> None:
        self._min = min
        self._max = max
        self._step = step
        self._value = min.get()

    def get(self) -> int:
        return self._value

    def update(self):
        next_value = self._value + self._step.get()
        if next_value > self._max.get():
            next_value = self._min.get()
        self._value = next_value
