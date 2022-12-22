import importlib
import yaml
from pydantic import BaseModel, Extra
from typing import Dict, List
from base import Common, OutputConfig
from writer import EncoderFactory, StreamFactory, Writer
from generator import GeneratorFactory, Const, GeneratorBase


def load_yml(path: str):
    with open(path, "r") as f:
        data = yaml.safe_load(f)
    return data


def get_module_name(base: str) -> str:
    end = base.rfind(".")
    base = base[:end] if end > 0 else base
    base = base.replace("/", ".")
    return base


def safe_push(mapper, key, value) -> bool:
    if mapper.get(key) is not None:
        return False
    mapper[key] = value
    return True


class PluginManager:

    def __init__(self, common: Common):
        self._generator_factory = GeneratorFactory(common.generator_prefix)
        self._encoder_factory = EncoderFactory(common.encoder_prefix)
        self._stream_factory = StreamFactory(common.stream_prefix)

        def load_plugin(module, factory, func_name):
            func = module.__dict__.get(func_name)
            if func is not None:
                func(factory)

        for path in common.paths:
            name = get_module_name(str(path))
            module = importlib.import_module(name)
            load_plugin(module, self._generator_factory, "register_generator")
            load_plugin(module, self._encoder_factory, "register_encoder")
            load_plugin(module, self._stream_factory, "register_stream")

    def is_generator(self, string: str):
        return string.startswith(self._generator_factory._prefix)

    def get_generator(self, string: str, args):
        plugin = self._generator_factory.create(string, args)
        return plugin

    def update_generator(self):
        self._generator_factory.update()

    def get_writer(self, config: OutputConfig) -> Writer:
        stream = self._stream_factory.create(config.get_target_type())
        encoder = self._encoder_factory.create(config.type)
        writer = Writer(stream, encoder)
        return writer


class OutputUnit(BaseModel):
    config: OutputConfig = OutputConfig()
    mapping: object

    class Config:
        extra = Extra.forbid
        allow_mutation = False

    def _setup(self, mapping, plugins: PluginManager):
        t = type(mapping)
        if t == dict:
            for key, value in mapping.items():
                new_value = self._setup(value, plugins)
                mapping[key] = new_value
                if plugins.is_generator(key):
                    return plugins.get_generator(key, new_value)
            return mapping
        elif t == list:
            for i, item in enumerate(mapping):
                new_value = self._setup(item, plugins)
                mapping[i] = new_value
            return mapping
        elif t == str:
            if plugins.is_generator(mapping):
                new_value = plugins.get_generator(mapping, {})
            else:
                new_value = Const({"value": mapping})
            return new_value
        else:
            return Const({"value": mapping})

    def setup(self, plugins: PluginManager):
        self._setup(self.config.target, plugins)
        self._setup(self.mapping, plugins)

    def _apply(self, mapping):
        if isinstance(mapping, GeneratorBase):
            return mapping.get()
        t = type(mapping)
        if t == dict:
            for key, value in mapping.items():
                new_value = self._apply(value)
                mapping[key] = new_value
            return mapping
        elif t == list:
            for i, item in enumerate(mapping):
                new_value = self._apply(item)
                mapping[i] = new_value
            return mapping
        else:
            return mapping.get()

    def apply(self, mapping):
        new_mapping = dict(**mapping)
        return self._apply(new_mapping)

    def write(self, plugins: PluginManager):
        config = self.config
        writer = plugins.get_writer(config)
        try:
            writer.open(config)
            for _ in range(config.count):
                mapping = self.mapping
                if writer.need_apply():
                    mapping = self.apply(mapping)
                writer.write(mapping)
                plugins.update_generator()
        finally:
            writer.close()


class OutputList(BaseModel):
    common: Common = Common()
    outputs: Dict[str, OutputUnit] = {}

    class Config:
        extra = Extra.forbid
        allow_mutation = False

    def setup(self, plugins: PluginManager):
        for _, unit in self.outputs.items():
            unit.setup(plugins)

    def write(self, plugins: PluginManager):
        for _, unit in self.outputs.items():
            unit.write(plugins)


def pickup_pattern(data, pattern: List[str]):
    if pattern is None:
        return data

    new_outputs = {}
    outputs = data["outputs"]
    for name in outputs.keys():
        if name in pattern:
            new_outputs[name] = outputs[name]

    new_data = {
        "common": data["common"],
        "outputs": new_outputs
    }
    return new_data


def execute(path: str, pattern: List[str]):
    data = load_yml(path)
    data = pickup_pattern(data, pattern)
    outlist = OutputList(**data)
    plugins = PluginManager(outlist.common)
    outlist.setup(plugins)
    outlist.write(plugins)
