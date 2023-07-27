# various helper decorators developed for fuzzing with woke

import functools


def given(*args, **akwargs):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapped(*args, **kwargs):
            params = {k: v() if callable(v) else v for k, v in akwargs.items()}

            collector = getattr(args[0], "_collector", None)
            if collector is not None:
                collector.collect(args[0], fn, **params)
            return fn(args[0], **params)

        return wrapped

    return decorator
