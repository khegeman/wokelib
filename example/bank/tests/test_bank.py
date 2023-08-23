from woke.testing.core import default_chain
from woke.development.core import Account
from woke.development.transactions import may_revert
from woke.development.primitive_types import uint
from woke.testing.fuzzing import flow, invariant
from woke.testing import *
from wokelib import get_address, MAX_UINT
from wokelib import Mirror
from wokelib.generators.random import st
from pytypes.example.bank.contracts.bank import Bank
import os

# Determine if we are replaying a test
try:
    Replay = False if int(os.getenv("WOKE_REPLAY", 0)) > 0 else False
except:
    Replay = False

# Load appropriate modules based on replay status
if Replay:
    from wokelib.generators.replay import fuzz_test
else:
    from wokelib.generators.random import fuzz_test

# Create a mirror to track account balances
bankMirror = Mirror[Account]()
accounts = list()

class BankTest(fuzz_test.FuzzTest):
    """
    A fuzz test for the Bank contract.

    Attributes:
        account: A randomly chosen account.
        amount: A random integer amount.
    """
    
    account = st.choose(accounts)
   # amount = st.random_int(max=50)

    def pre_sequence(self) -> None:
        """
        Set up the pre-sequence for the fuzz test.
        """
        self._bank = Bank.deploy(from_=default_chain.accounts[0])
        bankMirror.bind(self._bank.accounts)
        accounts.clear()
        accounts.extend(default_chain.accounts[1:5])
        for account in accounts:
            bankMirror[account] = 0

    @flow()
    def deposit(self, account: Account, amount: uint) -> None:
        """
        Simulate a deposit flow.

        Args:
            account: The account to deposit to.
            amount: The amount to deposit.
        """
        balance = self._bank.accounts(account)
        overflow = balance + amount > MAX_UINT
        try:
            tx = self._bank.deposit(amount, from_=account)
            assert balance + amount == self._bank.accounts(account)
            assert tx.events[0] == Bank.Deposit(get_address(account), amount)
            assert not overflow
            bankMirror[account] += amount
        except TransactionRevertedError as e:            
            assert e ==  Panic(PanicCodeEnum.UNDERFLOW_OVERFLOW)
            assert overflow

    @flow()
    def withdraw(self, account: Account, amount: uint) -> None:
        """
        Simulate a withdraw flow.

        Args:
            account: The account to withdraw from.
            amount: The amount to withdraw.
        """
        balance = self._bank.accounts(account)
        underflow = balance < amount
        with may_revert() as e:
            tx = self._bank.withdraw(amount, from_=account)
            assert not underflow
            assert balance - amount == self._bank.accounts(account)
            assert tx.events[0] == Bank.Withdraw(get_address(account), amount)
            bankMirror[account] -= amount
        if e.value is not None:
            assert underflow

    @invariant()
    def balances_match(self) -> None:
        """
        Check if balances in the mirror match the bank contract.
        """
        bankMirror.assert_equals_remote()

@default_chain.connect()
def test_default():
    """
    Run the BankTest under the default connection.
    """
    if Replay:
        BankTest.load("replay.json")
    BankTest().run(sequences_count=3, flows_count=10, record=True)
