from generator import GeneratorFactory
from plugin.seq import Seq
from plugin.rnd import Rnd


def register_generator(factory: GeneratorFactory):
    factory.register("seq", Seq)
    factory.register("rnd", Rnd)
