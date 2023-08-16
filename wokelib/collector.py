"""

Fuzz test data collection classes and decorators
"""
import functools
from collections import defaultdict
from collections import namedtuple
from woke.development.core import Address, Account

from pathlib import Path
from typing import Dict
import time
import jsons
from dataclasses import dataclass,asdict,fields
from . import get_address


def address_serializer(obj: Address | Account, **kwargs) -> str:
    return str(get_address(obj))


jsons.set_serializer(address_serializer, Address)
jsons.set_serializer(address_serializer, Account)


def set_serializer(t: type) -> None:
    jsons.set_serializer(address_serializer, t)


@dataclass
class FlowMetaData:
    name: str
    params: Dict

class DictCollector:
    def __init__(self, testName: str):
        self._values = defaultdict(lambda: defaultdict(FlowMetaData))
        datapath = Path.cwd().resolve() / ".replay"
        datapath.mkdir(parents=True, exist_ok=True)

        self._filename = datapath / f"{testName}-{time.strftime('%Y%m%d-%H%M%S')}.json"

    def __repr__(self):
        return self._values.__repr__()

    @property
    def values(self):
        return self._values

    def collect(self, fuzz, fn, **kwargs):
        self._values[fuzz._sequence_num][fuzz._flow_num] = FlowMetaData(
            fn.__name__, kwargs
        )
        save_row = defaultdict(lambda: defaultdict(FlowMetaData))        
        save_row[fuzz._sequence_num][fuzz._flow_num] = FlowMetaData(fn.__name__, kwargs)       

        with open(self._filename, "a") as fp:
            j = jsons.dumps(save_row, strip_privates=True, strip_nulls=True)
            print(j, file=fp)


def collector(*args, **kwargs):
    """add this decorator to pre_sequence on your fuzz test
    This adds parameter collection and saving for all flows
    """

    def decorator(fn):
        names = fn.__qualname__.split(".")

        @functools.wraps(fn)
        def wrapped(*args, **kwargs):
            args[0]._collector = DictCollector(names[0])
            return fn(*args, **kwargs)

        return wrapped

    return decorator
