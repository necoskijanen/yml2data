from base import Common, OutputConfig
from main import OutputUnit, OutputList
from main import PluginManager
from main import load_yml, get_module_name
from pydantic import ValidationError
from typing import List
import pytest


common01 = {
    "generator_prefix": "use.",
    "encoder_prefix": "enc.",
    "stream_prefix": "dst.",
    "paths": ["./plugin"],
    "seed": 0,
}

output_config01 = {
    "count": 2,
    "type": "json",
    "charset": "utf-8",
    "append": False,
    "terminator": "\n",
    "indent": None,
    "header": False,
    "delimiter": ",",
    "quotechar": '"',
    "quoting": "ALL"
}


def test_module_name():
    sets = {
        "sample_plugin.py": "sample_plugin"
    }
    for test, expect in sets.items():
        assert get_module_name(test) == expect


def test_check_path_cwd():
    data = load_yml("./tests/test_main.yml")
    actual = Common(**data["common_path_pass"]).paths
    assert len(actual) == 2
    assert actual[0].exists
    assert actual[1].exists


def test_check_path_error():
    data = load_yml("./tests/test_main.yml")
    with pytest.raises(ValueError) as e:
        _ = Common(**data["common_path_error"]).paths
    assert "missed" in str(e.value)


def test_seed_int():
    data = load_yml("./tests/test_main.yml")
    actual = Common(**data["common_seed_int"]).seed
    assert actual == 10


def test_seed_time():
    data = load_yml("./tests/test_main.yml")
    actual = Common(**data["common_seed_time"]).seed
    assert actual > 0


def test_seed_error():
    data = load_yml("./tests/test_main.yml")
    with pytest.raises(ValidationError) as e:
        _ = Common(**data["common_seed_error"])
    assert "seed" in str(e.value)


def test_terminator():
    data = load_yml("./tests/test_main.yml")
    actual = OutputConfig(**data["terminator_lf"]).terminator
    assert actual == "\n"

    with pytest.raises(ValidationError) as e:
        _ = OutputUnit(**data["terminator_error"])
    assert "terminator" in str(e.value)


def build_outlist(yml: str, target: str):
    data = load_yml(yml)
    outlist = OutputList(**data[target])
    plugins = PluginManager(outlist.common)
    outlist.setup(plugins)
    return (data, outlist, plugins)


def get_string(writer):
    return writer._stream._buffer


def test_jsonencoder():
    plugins = PluginManager(Common(**common01))
    config = OutputConfig(**dict(output_config01, **{
        "target": "dst.string",
        "type": "enc.json",
        "indent": 2
    }))
    writer = plugins.get_writer(config)
    data = {"a": 100}
    writer.open(config)
    writer.write(data)
    actual = get_string(writer)[0]
    expect = '{\n  "a": 100\n}\n'
    assert actual == expect


def test_csvencoder():
    plugins = PluginManager(Common(**common01))
    config = OutputConfig(**dict(output_config01, **{
        "target": "dst.string",
        "type": "enc.csv",
        "delimiter": ",",
        "terminator": "LF",
        "quotechar": '"',
        "quoting": "NONNUMERIC"
    }))
    writer = plugins.get_writer(config)
    data = {"id": "a", "value": 100}
    writer.open(config)
    writer.write(data)
    actual = get_string(writer)[0]
    expect = '"a",100\n'
    assert actual == expect


def load_strings(path: str) -> List[str]:
    with open(path, "r") as f:
        return f.readlines()


def test_write_jsonfile():
    _, outlist, plugins = build_outlist("./tests/test_main.yml", "jsonfile")
    outlist.write(plugins)
    path = outlist.outputs["case1"].config.target["dst.file"].get()
    actual = load_strings(path)

    expect = [
        '{"id": "xx100xx", "user": {"name": "user01", "mail_address": ["01@sample.com", 100]}}\n',
        '{"id": "xx100xx", "user": {"name": "user01", "mail_address": ["01@sample.com", 100]}}\n'
    ]
    assert actual == expect


def test_write_csvfile():
    _, outlist, plugins = build_outlist("./tests/test_main.yml", "csvfile")
    outlist.write(plugins)
    path = outlist.outputs["case1"].config.target["dst.file"].get()
    actual = load_strings(path)

    expect = [
        '"id","user.name","user.mail_address","integer"\n',
        '"xx0xx","user01","01@sample.com",20\n',
        '"xx1xx","user01","01@sample.com",20\n'
    ]
    assert actual == expect


def test_expr_generator():
    _, outlist, plugins = build_outlist("./tests/test_main.yml", "exprtest")
    outlist.write(plugins)
    path = outlist.outputs["case1"].config.target["dst.file"].get()
    actual = load_strings(path)

    expect = [
        '"ID0003"\n',
    ]
    assert actual == expect


def test_stdout():
    _, outlist, plugins = build_outlist("./tests/test_main.yml", "stdout")
    outlist.write(plugins)
    _ = outlist.outputs["case1"].config.target
    assert True
