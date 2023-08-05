# various helper decorators developed for fuzzing with woke

import functools
from collections import defaultdict
from collections import namedtuple
from . import getAddress
from .config import settings

FlowMetaData = namedtuple("FlowMetaData", "name params")


def convert_accounts(values):
    d = values
    for k, v in d.items():
        for k2, v2 in v.items():
            for k3, v3 in v2.params.items():
                values[k][k2].params[k3] = str(getAddress(v3))
    return values


class DictCollector:
    def __init__(
        self,
    ):
        self._values = defaultdict(lambda: defaultdict(FlowMetaData))
        import json

        with open("result.json", "w") as fp:
            j = json.dumps(settings.as_dict())
            print(j, file=fp)

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

        with open("result.json", "a") as fp:
            j = json.dumps(convert_accounts(save_row))
            print(j, file=fp)
            # json.dump(self._collector.values, fp)


def collector(*args, **kwargs):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapped(*args, **kwargs):
            args[0]._collector = DictCollector()
            return fn(*args, **kwargs)

        return wrapped

    return decorator
