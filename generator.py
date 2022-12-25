from abc import abstractmethod
from base import FactoryBase


class GeneratorBase:

    @abstractmethod
    def get(self):
        pass

    def update(self):
        pass

    def __str__(self):
        return str(self.get())


class Const(GeneratorBase):

    def __init__(self, args) -> None:
        if type(args) == dict:
            self.value = args["value"]
        else:
            self.value = args

    def get(self):
        return self.value


class Expr(GeneratorBase):

    def __init__(self, expr, args={}) -> None:
        self._expr = expr
        self._args = args

    def get(self):
        return self._expr(**(self._args))


class Formatter(GeneratorBase):

    def __init__(self, format, value):
        self._format = format
        self._value = value

    def get(self):
        v = self._value.get()
        f = self._format.get()
        return f.format(v)

    def update(self):
        self._value.update()
        self._format.update()


class GeneratorFactory(FactoryBase):

    def __init__(self, prefix: str) -> None:
        super().__init__(prefix)
        self._expr_map = {}
        self._generators = []
        self.register("formatter", Formatter)

    def register(self, key: str, plugin_type):
        if isinstance(plugin_type, Expr):
            new_key = self._prefix + key
            self._expr_map[new_key] = plugin_type
        else:
            super().register(key, plugin_type)

    def create(self, key: str, args):
        args = {} if args is None else args
        plugin_type = self._map.get(key)
        if plugin_type is None:
            plugin = self._expr_map[key]
        else:
            plugin = plugin_type(**args)
        self._generators.append(plugin)
        return plugin

    def update(self):
        for generator in self._generators:
            generator.update()

    def is_call_plugin(self, string: str) -> bool:
        result = super().is_call_plugin(string)
        if not result:
            for key in self._expr_map.keys():
                if string.startswith(key):
                    return True
        return result
