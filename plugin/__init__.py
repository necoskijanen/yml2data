from generator import GeneratorFactory
from plugin.sequence import Sequence
from plugin.random import Random


def register_generator(factory: GeneratorFactory):
    factory.register("seq", Sequence)
    factory.register("rnd", Random)
