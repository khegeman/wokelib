# various helper decorators developed for fuzzing with woke

import functools
from collections import defaultdict
from collections import namedtuple


FlowMetaData = namedtuple("FlowMetaData", "name params")


class DictCollector:
    def __init__(self,):
        self._values = defaultdict(lambda: defaultdict(FlowMetaData))

    def __repr__(self):
        return self._values.__repr__()

    @property
    def values(self):
        return self._values

    def collect(self, fuzz, fn, **kwargs):
        self._values[fuzz._sequence_num][fuzz._flow_num] = FlowMetaData(
            fn.__name__, kwargs
        )


def collector(*args, **kwargs):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapped(*args, **kwargs):
            args[0]._collector = DictCollector()
            return fn(*args, **kwargs)

        return wrapped

    return decorator
