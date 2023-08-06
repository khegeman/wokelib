# various helper decorators developed for fuzzing with woke

import functools


def given(*args, **akwargs):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapped(*args, **kwargs):
            names = fn.__qualname__.split(".")
            assert len(names) == 2
            params = {
                k: v(
                    class_=names[0],
                    param=k,
                    fn=names[1],
                    sequence_num=args[0]._sequence_num,
                    flow_num=args[0]._flow_num,
                )
                if callable(v)
                else v
                for k, v in akwargs.items()
            }

            collector = getattr(args[0], "_collector", None)
            if collector is not None:
                collector.collect(args[0], fn, **params)
            return fn(args[0], **params)

        return wrapped

    return decorator
