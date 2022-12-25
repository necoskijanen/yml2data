from main import execute
from typing import List
import json


TEST_PLUGIN_YML_PATH = "./tests/test_plugin.yml"


def load_file(path) -> List[str]:
    with open(path, "r") as f:
        strings = f.readlines()
        return strings


def is_between(min, max, val) -> bool:
    if min <= val and val <= max:
        return True
    else:
        return False


def test_sequence():
    pattern = "case_seq"
    _, outlist, _ = execute(TEST_PLUGIN_YML_PATH, [pattern])
    file = outlist.outputs[pattern].config.get_target_value()
    actual = [json.loads(line) for line in load_file(file)]
    expect = [
        {"seq1": 0, "seq2": 1},
        {"seq1": 1, "seq2": 3},
        {"seq1": 2, "seq2": 1},
    ]
    assert actual == expect


def test_random():
    pattern = "case_rnd"
    _, outlist, _ = execute(TEST_PLUGIN_YML_PATH, [pattern])
    file = outlist.outputs[pattern].config.get_target_value()
    actuals = json.loads(load_file(file)[0])

    actual = actuals["rndint"]
    assert type(actual) == int
    assert is_between(1, 10, actual)

    actual = actuals["rndfloat"]
    assert type(actual) == float
    assert is_between(0.0, 5.0, actual)
