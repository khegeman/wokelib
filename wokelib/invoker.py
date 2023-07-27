# various helper decorators developed for fuzzing with woke

import functools

from collections import defaultdict, namedtuple

TX = namedtuple("TX", "events")


def invoker(s_impl, p_impl):
    def invoke(fname, expected_execptions=[], **kwargs):
        py_revert = False
        sol_revert = False
        import inspect

        def scall(object, name, **kwargs):
            fn = getattr(object, name)
            sig = inspect.signature(fn)
            arglist = {arg: kwargs[arg] for arg in sig.parameters if arg in kwargs}
            return fn(**arglist)

        stx = None
        ptx = None
        try:
            fn = getattr(p_impl, fname)
            sig = inspect.signature(fn)
            arglist = {arg: kwargs[arg] for arg in sig.parameters}

            ptx = fn(**arglist)
        except Exception as e:
            print(e)
            py_revert = True

        try:
            stx = scall(s_impl, fname, **kwargs)
        except Exception as e:
            print(
                fname,
                "error",
                e,
                any([isinstance(e, ex) for ex in expected_execptions]),
            )
            if any([isinstance(e, ex) for ex in expected_execptions]):
                sol_revert = True
            else:
                raise e

        assert py_revert == sol_revert, {
            "invoke of {} failed assertion check".format(fname)
        }

        if isinstance(ptx, TX):
            assert stx is not None
            assert ptx.events == stx.events, {
                "invoke of {} failed event match check".format(fname)
            }
        return stx

    return invoke
