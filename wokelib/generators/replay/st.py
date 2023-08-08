"""

This is the basic implementation for corpus replay.  

We replace all the strategies for random data generation with 
equivalent functions that load data from a json file.

"""
from typing import List, Any


from woke.development.core import Address

import jsons
import copy


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


def random_ints(**kwargs):
    def f(class_: str, fn: str, param: str, sequence_num: int, flow_num: int):
        # find it
        return get_param(param, sequence_num, flow_num)

    return f


def random_addresses(**kwargs):
    def f(class_: str, fn: str, param: str, sequence_num: int, flow_num: int):
        return [Address(a) for a in get_param(param, sequence_num, flow_num)]

    return f


def random_int(**kwargs):
    def f(class_: str, fn: str, param: str, sequence_num: int, flow_num: int):
        return get_param(param, sequence_num, flow_num)

    return f


def random_float(**kwargs):
    def f(class_: str, fn: str, param: str, sequence_num: int, flow_num: int):
        return get_param(param, sequence_num, flow_num)

    return f


def random_percentage(**kwargs):
    def f(class_: str, fn: str, param: str, sequence_num: int, flow_num: int):
        return get_param(param, sequence_num, flow_num)

    return f


def choose(values: List, **kwargs):
    def f(class_: str, fn: str, param: str, sequence_num: int, flow_num: int):
        return get_param(param, sequence_num, flow_num)

    return f


def random_bool(**kwargs):
    def f(class_: str, fn: str, param: str, sequence_num: int, flow_num: int):
        return get_param(param, sequence_num, flow_num)

    return f


def choose_n(values: List, **kwargs):
    def f(class_: str, fn: str, param: str, sequence_num: int, flow_num: int):
        return get_param(param, sequence_num, flow_num)

    return f


def random_bytes(**kwargs):
    def f(class_: str, fn: str, param: str, sequence_num: int, flow_num: int):
        return get_param(param, sequence_num, flow_num)

    return f
