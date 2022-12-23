from pydantic import BaseModel, Extra, ValidationError, validator
from pathlib import Path
from abc import abstractmethod
from typing import List, Optional
import csv
import random
import time
import sys


def resolve_path(value: str) -> Path:
    path = Path(value)
    if not path.exists():
        raise ValueError(f'{path.absolute()} is not exist')
    return path


class Common(BaseModel):
    generator_prefix: str = "use."
    encoder_prefix: str = "enc."
    stream_prefix: str = "dst."
    paths: List[Path] = [Path("./")]
    seed: int = 0
    extra: Optional[object] = None

    class Config:
        extra = Extra.allow
        allow_mutation = False

    @validator("paths", each_item=True)
    def check_paths(cls, v):
        return resolve_path(v)

    @validator("seed", pre=True)
    def check_seed(cls, v):
        t = type(v)
        print(t, v)
        if t == int:
            return v
        elif t == str:
            if v == "time":
                return int(time.time())
            elif v == "random":
                return random.randint(0, sys.maxsize)
        else:
            raise ValidationError('seed => integer or "time"')


class OutputConfig(BaseModel):
    target: object
    type: str = ""
    count: int = 10
    charset: str = "UTF-8"
    append: bool = False
    terminator: str = "\n"
    indent: Optional[int] = None
    header: bool = False
    delimiter: str = ","
    quotechar: str = '"'
    quoting: int = csv.QUOTE_ALL

    class Config:
        extra = Extra.allow
        allow_mutation = False

    @validator("terminator")
    def check_terminator(cls, v):
        types = {
            "LF": "\n",
            "CR": "\r",
            "CRLF": "\r\n"
        }
        type = types.get(v.upper())
        return type if type is not None else v

    @validator("quoting", pre=True)
    def check_quoting(cls, v):
        types = {
            "MINIMAL": csv.QUOTE_MINIMAL,
            "ALL": csv.QUOTE_ALL,
            "NONNUMERIC": csv.QUOTE_NONNUMERIC,
            "NONE": csv.QUOTE_NONE,
        }
        quoting = types.get(v.upper())
        if quoting is None:
            raise ValidationError()
        return quoting

    def get_target_type(self) -> str:
        target = self.target
        t = type(target)
        if t == str:
            return target
        elif t == dict:
            for key in target.keys():
                return key

    def get_target_value(self) -> str:
        target = self.target
        t = type(target)
        if t == str:
            return t
        elif t == dict:
            for value in target.values():
                return value.get()


class EncoderBase:
    def __init__(self, prefix: str) -> None:
        self._prefix = prefix

    @abstractmethod
    def init(self, config: OutputConfig):
        pass

    @abstractmethod
    def encode(self, obj) -> str:
        pass

    def need_apply(self) -> bool:
        return False


class StreamBase:

    def __init__(self, prefix: str) -> None:
        self._prefix = prefix

    @abstractmethod
    def open(self, config: OutputConfig):
        pass

    @abstractmethod
    def write(self, string: str):
        pass

    @abstractmethod
    def close(self):
        pass


class FactoryBase:
    def __init__(self, prefix: str) -> None:
        self._prefix = prefix
        self._map = {}

    def register(self, key: str, plugin_type):
        new_key = self._prefix + key
        self._map[new_key] = plugin_type

    def is_call_plugin(self, string: str) -> bool:
        return string.startswith(self._prefix)

    @abstractmethod
    def create(self, key: str, args):
        pass
