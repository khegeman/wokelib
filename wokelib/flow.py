from __future__ import annotations
import functools
from .config import settings


from typing import Callable, Optional
from woke.testing.fuzzing import FuzzTest


### Add this dectorator to print each flow in a sequence
def flow(
    *,
    precondition: Optional[Callable[[FuzzTest], bool]] = None,
):
    def decorator(fn):
        fn.flow = True
        fn.weight = settings.get(f"flows.{fn.__name__}.weight", 0)
        max_times = settings.get(f"flows.{fn.__name__}.max_times", None)
        if max_times is not None:
            fn.max_times = max_times
        if precondition is not None:
            fn.precondition = precondition
        return fn

    return decorator
