from woke.testing.core import default_chain


from woke.testing.fuzzing import generators
from woke.development.core import Address, Account
from eth_utils.currency import to_wei
from woke.testing.core import default_chain
from woke.development.utils import keccak256

from woke.development.primitive_types import uint
from typing import cast
from dataclasses import dataclass

from woke.development.transactions import may_revert, must_revert
from wokelib import flow
from wokelib import given, collector, print_steps, getAddress

# we load different depending on if we are doing random generation or a replay
Replay = False
if Replay:
    from wokelib.replay import st
    from wokelib.replay import fuzz_test

    # no cli yet
    import os

    replay_file = os.environ["WOKE_REPLAY"]
    st.load(replay_file)
else:
    from wokelib.toml import st
    from woke.testing.fuzzing import fuzz_test

from wokelib import config, load
import random
import math

# random.seed(44)


load("settings.toml", "FuzzTest")


class FuzzTest(fuzz_test.FuzzTest):
    # collector decorator on the pre_sequence turns on the recording right now
    @collector()
    def pre_sequence(self) -> None:
        pass

    def pre_flow(self, flow) -> None:
        print("pre_flow", self._flow_num)

    @flow()
    @given(
        amount=st.random_int(),
    )
    def flow1(self, amount) -> None:
        print("amount", amount)

    @flow()
    @given(amount=st.random_int(), addresses=st.random_addresses())
    def flow2(self, amount, addresses) -> None:
        print("amount", amount)
        print(addresses)

    @flow()
    @given(
        amounts=st.random_ints(),
    )
    def flow3(self, amounts) -> None:
        print("amounts", amounts)

    #  assert False

    @flow()
    @given(
        prob=st.random_percentage(),
    )
    def flow4(self, prob) -> None:
        print("prob", prob)

    @flow()
    @given(
        doit=st.random_bool(),
    )
    def flow5(self, doit) -> None:
        print("prob", doit)


@default_chain.connect()
def test_default():
    default_chain.set_default_accounts(default_chain.accounts[0])
    FuzzTest().run(sequences_count=1, flows_count=20)
