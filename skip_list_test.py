#!/usr/bin/env python3

import types
import skip_list
from skip_list import Pair, SkipList, SkipNode

import pytest
parameterize = pytest.mark.parametrize


def make_example_list():
  _24 = SkipNode(Pair(24, "24!"), [None, None, None])
  _19 = SkipNode(Pair(19, "19!"), [_24])
  _15 = SkipNode(Pair(15, "15!"), [_19, _24])
  _12 = SkipNode(Pair(12, "12!"), [_15])
  _7 = SkipNode(Pair(7, "7!"), [_12])
  _5 = SkipNode(Pair(5, "5!"), [_7, _15, _24])
  _1 = SkipNode(Pair(1, "1!"), [_5])
  _head = SkipNode(Pair(None, None), [_1, _5, _5])
  return SkipList(_head, 2, 7)

def make_example_list():
  _24 = SkipNode(Pair(24, "24!"), {})
  _19 = SkipNode(Pair(19, "19!"), {0: _24})
  _15 = SkipNode(Pair(15, "15!"), {0: _19, 1: _24})
  _12 = SkipNode(Pair(12, "12!"), {0: _15})
  _7 = SkipNode(Pair(7, "7!"), {0: _12})
  _5 = SkipNode(Pair(5, "5!"), {0: _7, 1: _15, 2: _24})
  _1 = SkipNode(Pair(1, "1!"), {0: _5})
  _head = SkipNode(Pair(None, None), {0: _1, 1: _5, 2: _24})
  return SkipList(_head, 2, 7)

example_list = pytest.fixture(make_example_list)


def test_find_missing_key(example_list):
  with pytest.raises(KeyError):
    example_list[100]


@parameterize("level", (0, 1, 2, 6))
def test_insert(example_list, level):
  key = 14
  value = "my value"
  example_list.get_level = types.MethodType(lambda self: level, example_list)
  example_list = example_list.insert(key, value)
  assert example_list[key] == value


@parameterize("to_delete", (1, 5, 15, 12, 24, 100))
def test_delete(example_list, to_delete):
  example_list = example_list.delete(to_delete)
  with pytest.raises(KeyError):
    example_list[to_delete]


@parameterize("to_find", (1, 5, 15, 12, 24))
def test_find(example_list, to_find):
  assert example_list[to_find] == f"{to_find}!"
