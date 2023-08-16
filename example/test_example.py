from woke.testing.core import default_chain


from woke.testing.fuzzing import generators
from woke.development.core import Address, Account
from eth_utils.currency import to_wei
from woke.testing.core import default_chain
from woke.development.utils import keccak256

from woke.development.primitive_types import uint
from typing import List
from dataclasses import dataclass

from woke.development.transactions import may_revert, must_revert

from wokelib import given, collector, print_steps, get_address
from woke.testing.fuzzing import flow

# we load different depending on if we are doing random generation or a replay
Replay = False
if Replay:
    from wokelib.generators.replay import st
    from wokelib.generators.replay import fuzz_test

    # no cli yet
    import os

    replay_file = os.environ["WOKE_REPLAY"]
    st.load(replay_file)
else:
    from wokelib.generators.random import st
    #from wokelib.generators.random import fuzz_test
    from woke.testing.fuzzing import fuzz_test

from wokelib import config, load
import random
import math

random.seed(44)


@dataclass
class Balance:
    account: Address
    balance: uint


def random_balance(min: uint = 0, max: uint = st.MAX_UINT, **kwargs):
    print("calling random blaance")

    def f():
        return Balance(
            account=generators.random_address(),
            balance=generators.random_int(min=min, max=max, **kwargs),
        )

    return f


class ExampleTest(fuzz_test.FuzzTest):
    # collector decorator on the pre_sequence turns on the recording right now
    @collector()
    def pre_sequence(self) -> None:
        pass

    def pre_flow(self, flow) -> None:
        print("pre_flow", self._flow_num)

    st_deposit_amount = st.random_int(min=1, max=5)
    st_addresses = st.random_addresses(len=3)
    st_amounts = st.random_ints(len=3, min=40, max=54)
    st_percentage = st.random_percentage()
    st_bool = st.random_bool(true_prob=0.5)

    st_balance = random_balance(min=500, max=4000)

    @flow()
    def flow1(self, st_deposit_amount: uint) -> None:
        print("amount", st_deposit_amount)

    @flow()
    def flow2(self, st_deposit_amount: uint, st_addresses: List[Address]) -> None:
        print("amount", st_deposit_amount)
        print(st_addresses)

    @flow()
    def flow3(self, st_amounts: List[uint]) -> None:
        print("amounts", st_amounts)

    @flow()
    def flow4(self, st_percentage: float) -> None:
        print("prob", st_percentage)

    @flow()
    def flow5(self, st_bool: bool) -> None:
        print("prob", st_bool)

    @flow()
    def flow6(self, st_balance: Balance) -> None:
        print("balance", st_balance)


@default_chain.connect()
def test_default():
    default_chain.set_default_accounts(default_chain.accounts[0])
    ExampleTest().run(sequences_count=1, flows_count=20)
