# Strategies for generating random data for flows

from typing import List, Any

import random
from woke.development.primitive_types import uint
from woke.testing.fuzzing import generators
from ..config import settings
from . import MAX_UINT


class Data:
    values = []

    def set(self, v):
        self.values = v

    def get(self):
        return self.values


def get_args(param: str, fn: str):
    return settings.get(f"flows.{fn}.{param}")


def random_ints():
    def f(param: str, fn: str):
        args = get_args(param, fn).to_dict().copy()
        # we have to delete len before we call random int
        len = args["len"]
        del args["len"]

        if "min" not in args:
            args["min"] = 0
        if "max" not in args:
            args["max"] = MAX_UINT

        return [generators.random_int(**args) for i in range(0, len)]

    return f


def random_addresses():
    def f(param: str, fn: str):
        args = get_args(param, fn)
        return [generators.random_address() for i in range(0, args.len)]

    return f


def random_int():
    def f(param: str, fn: str):
        args = get_args(param, fn)
        print(args)
        if "min" not in args:
            args["min"] = 0
        if "max" not in args:
            args["max"] = MAX_UINT
        return generators.random_int(**args)

    return f


def random_float(min: float, max: float):
    def f(param: str, fn: str):
        return random.uniform(min, max)

    return f


def random_percentage():
    def f(param: str, fn: str):
        args = get_args(param, fn)
        edge_values_prob = None
        if "edge_values_prob" in args:
            edge_values_prob = args.edge_values_prob
        return random_float_with_probability(0, 1, edge_values_prob)

    return f


def choose(values: Data):
    def f(param: str, fn: str):
        return random.choice(values.get())

    return f


def random_bool():
    def f(param: str, fn: str):
        return generators.random_bool(true_prob=get_args(param, fn).true_prob)

    return f


def choose_n(values):
    def f(param: str, fn: str):
        args = get_args(param, fn)
        return random.choices(
            values.get(), k=generators.random_int(args.min_k, args.max_k)
        )

    return f


def random_bytes():
    def f(param: str, fn: str):
        args = get_args(param, fn)
        return generators.random_bytes(args.min, args.max)

    return f


def random_float_with_probability(start, end, edge_values_prob=None):
    if edge_values_prob is not None:
        if edge_values_prob < 0 or edge_values_prob > 1:
            raise ValueError("Probability should be between 0 and 1 (inclusive).")

    if edge_values_prob == 0:
        return random.uniform(
            start, end
        )  # Probability of choosing end is 0, always choose a random float within the range.
    elif edge_values_prob == 1:
        return start if random.uniform(0, 1) < 0.5 else end
    else:
        rand_val = random.uniform(0, 1)  # Generate a random float between 0 and 1.
        if edge_values_prob is None or rand_val >= edge_values_prob:
            return random.uniform(start, end)  # Choose a random float within the range.
        else:
            return start if random.uniform(0, 1) < 0.5 else end
