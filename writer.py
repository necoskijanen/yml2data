import csv
import json
import sys
from io import StringIO
from base import OutputConfig, EncoderBase, StreamBase, FactoryBase


class JsonEncoder(EncoderBase):

    def init(self, config: OutputConfig):
        params = {
            "indent": config.indent,
            "default": lambda x: x.get()
        }
        self._encoder = lambda obj: json.dumps(obj, **params)
        self._terminator = config.terminator

    def encode(self, obj) -> str:
        string = self._encoder(obj) + self._terminator
        return string


class CsvEncoder(EncoderBase):

    def init(self, config: OutputConfig):
        self._buffer = StringIO()
        params = {
            "delimiter": config.delimiter,
            "quotechar": config.quotechar,
            "quoting": config.quoting,
            "lineterminator": config.terminator,
        }
        self._need_apply = config.quoting is not csv.QUOTE_ALL
        self._encoder = csv.writer(self._buffer, **params)
        if config.header:
            self.encode = self._add_header
        else:
            self.encode = self._value_only

    def encode(self, obj) -> str:
        return ""

    def _encode(self, obj) -> str:
        self._encoder.writerow(obj)
        string = self._buffer.getvalue()
        self._buffer.truncate(0)
        self._buffer.seek(0)
        return string

    def _add_header(self, obj) -> str:
        keys = list(obj.keys())
        string = self._encode(keys)
        string += self._value_only(obj)
        self.encode = self._value_only
        return string

    def _value_only(self, obj) -> str:
        values = list(obj.values())
        string = self._encode(values)
        return string

    def need_apply(self) -> bool:
        return self._need_apply


class EncoderFactory(FactoryBase):

    def __init__(self, prefix: str) -> None:
        super().__init__(prefix)
        super().register("json", JsonEncoder)
        super().register("csv", CsvEncoder)

    def create(self, key: str, _=None):
        encoder = self._map.get(key)
        if encoder is None:
            encoder = JsonEncoder
        return encoder(self._prefix)


class StdOutError(StreamBase):
    def open(self, config: OutputConfig):
        if config.get_target_type() == self._prefix + "stdout":
            self._fp = sys.stdout
        else:
            self._fp = sys.stderr
        return self

    def write(self, string: str):
        self._fp.write(string)

    def close(self):
        self._fp.flush()


class FilePointer(StreamBase):
    def open(self, config: OutputConfig):
        params = {
            "file": config.get_target_value(),
            "mode": "a" if config.append else "w",
            "encoding": config.charset,
            "newline": config.terminator,
        }
        self._fp = open(**params)
        return self

    def write(self, string: str):
        self._fp.write(string)

    def close(self):
        self._fp.flush()
        self._fp.close()


class StringBuffer(StreamBase):
    def open(self, _: OutputConfig):
        self._buffer = []

    def write(self, string: str):
        self._buffer.append(string)

    def close(self):
        self._buffer = None


class StreamFactory(FactoryBase):

    def __init__(self, prefix: str) -> None:
        super().__init__(prefix)
        super().register("stdout", StdOutError)
        super().register("stderr", StdOutError)
        super().register("file", FilePointer)
        super().register("string", StringBuffer)

    def create(self, key: str, _=None):
        stream = self._map.get(key)
        if stream is None:
            stream = FilePointer
        return stream(self._prefix)


class Writer:
    def __init__(self, stream: StreamBase, encoder: EncoderBase) -> None:
        self._encoder = encoder
        self._stream = stream

    def open(self, config: OutputConfig):
        self._encoder.init(config)
        self._stream.open(config)

    def write(self, obj):
        string = self._encoder.encode(obj)
        self._stream.write(string)

    def close(self):
        self._stream.close()

    def need_apply(self) -> bool:
        return self._encoder.need_apply()
