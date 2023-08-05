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


def random_ints(len: int, min_val: uint = 0, max_val: uint = MAX_UINT):
    def f(param: str, fn: str):
        return [generators.random_int(min_val, max_val) for i in range(0, len)]

    return f


def random_addresses(len: int):
    def f(param: str, fn: str):
        return [generators.random_address() for i in range(0, len)]

    return f


def random_int(min: uint = 0, max: uint = MAX_UINT, **kwargs):
    def f(param: str, fn: str):
        return generators.random_int(min=min, max=max, **kwargs)

    return f


def random_float(min: float, max: float):
    def f(param: str, fn: str):
        return random.uniform(min, max)

    return f


def random_percentage(edge_values_prob=None):
    def f(param: str, fn: str):
        return random_float_with_probability(0, 1, edge_values_prob)

    return f


def choose(values: Data):
    def f(param: str, fn: str):
        return random.choice(values.get())

    return f


def random_bool(true_prob):
    def f(param: str, fn: str):
        return generators.random_bool(true_prob=true_prob)

    return f


def choose_n(values, min_k, max_k):
    def f(param: str, fn: str):
        return random.choices(values.get(), k=generators.random_int(min_k, max_k))

    return f


def random_bytes(min, max):
    def f(param: str, fn: str):
        return generators.random_bytes(min, max)

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
