from woke.testing.core import default_chain


# flow test for beedle protocol
from woke.testing.fuzzing import generators
from woke.development.core import Address, Account
from eth_utils.currency import to_wei
from woke.testing.core import default_chain
from woke.development.utils import keccak256
from woke.testing.fuzzing import fuzz_test
from woke.development.primitive_types import uint
from typing import cast
from dataclasses import dataclass

from woke.development.transactions import may_revert, must_revert
from wokelib import flow
from wokelib import given, collector, print_steps, getAddress
from wokelib import dyna
from wokelib import settings
import random
import math

# random.seed(44)


class FuzzTest(fuzz_test.FuzzTest):
    # collector decorator on the pre_sequence turns on the recording right now
    @collector()
    def pre_sequence(self) -> None:
        pass

    def post_sequence(self) -> None:
        import json

        d = self._collector.values
        for k, v in d.items():
            for k2, v2 in v.items():
                for k3, v3 in v2.params.items():
                    self._collector.values[k][k2].params[k3] = str(getAddress(v3))

        # with open('result.json', 'w') as fp:
        # j = json.dumps(self._collector.values, indent=4)
        # print(j, file=fp)
        # json.dump(self._collector.values, fp)

    def pre_flow(self, flow) -> None:
        print("pre_flow", self._flow_num)

    @flow()
    @given(
        amount=dyna.random_int(),
    )
    def flow1(self, amount) -> None:
        print("amount", amount)

    @flow()
    @given(amount=dyna.random_int(), addresses=dyna.random_addresses())
    def flow2(self, amount, addresses) -> None:
        print("amount", amount)
        print(addresses)

    @flow()
    @given(
        amounts=dyna.random_ints(),
    )
    def flow3(self, amounts) -> None:
        print("amount", amounts)

    @flow()
    @given(
        prob=dyna.random_percentage(),
    )
    def flow4(self, prob) -> None:
        print("prob", prob)

    @flow()
    @given(
        doit=dyna.random_bool(),
    )
    def flow5(self, doit) -> None:
        print("prob", doit)


@default_chain.connect()
def test_default():
    default_chain.set_default_accounts(default_chain.accounts[0])
    FuzzTest().run(sequences_count=1, flows_count=20)
