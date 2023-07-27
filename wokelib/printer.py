import functools


### Add this dectorator to print each flow in a sequence
def print_steps(do_print=False, *args, **kwargs):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapped(*args, **kwargs):
            if do_print:
                print(
                    "seq:",
                    args[0]._sequence_num,
                    "flow:",
                    args[0]._flow_num,
                    "flow name:",
                    fn.__name__,
                    "flow parameters:",
                    kwargs,
                )
            return fn(*args, **kwargs)

        return wrapped

    return decorator
