# various helper decorators developed for fuzzing with woke

import functools
from collections import defaultdict
from collections import namedtuple
from woke.development.core import Address, Account
from . import getAddress
from .config import settings

import time
import jsons

FlowMetaData = namedtuple("FlowMetaData", "name params")


class DictCollector:
    def __init__(self, testName: str):
        self._values = defaultdict(lambda: defaultdict(FlowMetaData))
        self._filename = f"{testName}-{time.strftime('%Y%m%d-%H%M%S')}.json"

    def __repr__(self):
        return self._values.__repr__()

    @property
    def values(self):
        return self._values

    def collect(self, fuzz, fn, **kwargs):
        print("collect", fuzz._flow_num)
        self._values[fuzz._sequence_num][fuzz._flow_num] = FlowMetaData(
            fn.__name__, kwargs
        )
        save_row = defaultdict(lambda: defaultdict(FlowMetaData))
        save_row[fuzz._sequence_num][fuzz._flow_num] = FlowMetaData(fn.__name__, kwargs)
        # save as json lines
        import json

        with open(self._filename, "a") as fp:
            j = jsons.dumps(save_row)
            print(j, file=fp)
            # json.dump(self._collector.values, fp)


def collector(*args, **kwargs):
    def decorator(fn):
        names = fn.__qualname__.split(".")

        @functools.wraps(fn)
        def wrapped(*args, **kwargs):
            args[0]._collector = DictCollector(names[0])
            return fn(*args, **kwargs)

        return wrapped

    return decorator
