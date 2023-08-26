
from woke.testing.fuzzing import generators
from woke.development.core import Address
from woke.testing.core import default_chain
from woke.development.primitive_types import uint
from dataclasses import dataclass
from woke.testing.fuzzing import flow
from woke.testing.fuzzing.fuzz_test import FuzzTest




@dataclass
class Balance:
    account: Address
    balance: uint


def random_balance(min: uint , max: uint):

    def f():
        return Balance(
            account=generators.random_address(),
            balance=generators.random_int(min=min, max=max),
        )

    return f


class ExampleTest(FuzzTest):


    st_balance = random_balance(min=500, max=4000)

    @flow()
    def flow6(self, st_balance: Balance) -> None:
        print("balance", st_balance)


@default_chain.connect()
def test_default():
    default_chain.set_default_accounts(default_chain.accounts[0])
    ExampleTest().run(sequences_count=1, flows_count=5)