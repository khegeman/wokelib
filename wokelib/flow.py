from __future__ import annotations
import functools
from .config import settings, config


from typing import Callable, Optional
from woke.testing.fuzzing import FuzzTest


### Add this dectorator to print each flow in a sequence
def flow(
    *,
    precondition: Optional[Callable[[FuzzTest], bool]] = None,
):
    def decorator(fn):
        cname = fn.__qualname__.split(".")[0]
        print(settings)
        fn.flow = True
        fn.weight = config(f"{cname}.flows.{fn.__name__}.weight", 0)
        max_times = settings.get(f"{cname}.flows.{fn.__name__}.max_times", None)
        if max_times is not None:
            fn.max_times = max_times
        if precondition is not None:
            fn.precondition = precondition
        return fn

    return decorator
