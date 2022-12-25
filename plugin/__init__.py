from generator import GeneratorFactory
from plugin.rnd import Rnd


def register_generator(factory: GeneratorFactory):
    factory.register("rnd", Rnd)
