from generator import GeneratorFactory, Expr
from tests.plugin.sample.sample_plugin import SamplePlugin


class Counter:
    def __init__(self, initial) -> None:
        self.count = initial

    def increment(self) -> int:
        value = self.count
        self.count = value + 1
        return value


counter = Counter(0)


def register_generator(factory: GeneratorFactory):
    factory.register("sample", SamplePlugin)
    factory.register("counter", Expr(lambda: counter.increment()))

    def add(x, y):
        return x + y

    factory.register("expr_sample", Expr(lambda x, y: add(x, y), {"x": 1, "y": 2}))
