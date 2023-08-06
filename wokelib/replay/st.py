# Strategies for generating random data for flows

from typing import List, Any

import random
from woke.development.primitive_types import uint
from woke.development.core import Address, Account
from woke.testing.fuzzing import generators
from ..config import settings, config
from . import MAX_UINT

import jsons
import copy


class Data:
    values = []

    def set(self, v):
        self.values = v

    def get(self):
        return self.values


sequences = {}


def get_param(param: str, sequence_num: int, flow_num: int):
    params = sequences.get(str(sequence_num), {}).get(str(flow_num), {})
    data = params.get("params", {})
    return data[param]


def load(filename: str):
    # load json lines recorded file to a dict for now
    with open(filename, "r") as f:
        for line in f.readlines():
            flow = jsons.loads(line)
            seqnum = list(flow)[0]
            print("flow", flow, seqnum)
            s = sequences.get(seqnum, {})
            s.update(flow[seqnum])
            sequences[seqnum] = s
            print("sequences", sequences)


def random_ints():
    def f(class_: str, fn: str, param: str, sequence_num: int, flow_num: int):
        # find it
        return get_param(param, sequence_num, flow_num)

    return f


def random_addresses():
    def f(class_: str, fn: str, param: str, sequence_num: int, flow_num: int):
        return [Address(a) for a in get_param(param, sequence_num, flow_num)]

    return f


def random_int():
    def f(class_: str, fn: str, param: str, sequence_num: int, flow_num: int):
        return get_param(param, sequence_num, flow_num)

    return f


def random_float(min: float, max: float):
    def f(class_: str, fn: str, param: str, sequence_num: int, flow_num: int):
        return get_param(param, sequence_num, flow_num)

    return f


def random_percentage():
    def f(class_: str, fn: str, param: str, sequence_num: int, flow_num: int):
        return get_param(param, sequence_num, flow_num)

    return f


def choose(values: Data):
    def f(class_: str, fn: str, param: str, sequence_num: int, flow_num: int):
        return get_param(param, sequence_num, flow_num)

    return f


def random_bool():
    def f(class_: str, fn: str, param: str, sequence_num: int, flow_num: int):
        return get_param(param, sequence_num, flow_num)

    return f


def choose_n(values):
    def f(class_: str, fn: str, param: str, sequence_num: int, flow_num: int):
        return get_param(param, sequence_num, flow_num)

    return f


def random_bytes():
    def f(class_: str, fn: str, param: str, sequence_num: int, flow_num: int):
        return get_param(param, sequence_num, flow_num)

    return f
