# WokeLib

An collection of decorators and functions I use for fuzz testing smart contracts with [Woke](https://github.com/Ackee-Blockchain/woke)

## Features

* Corpus Replay
* Hypothesis style data generation for stateful fuzz tests

## Generating data

I modelled this setup after hypothesis such that the generation of all random values is done outside of the flows and sequences in the woke fuzz class.  The reason I prefer this style relates to reproducability.  With this style, all inputs parameters to the flows can be recorded. 

## Strategies

The strategies defined in this library are thin wrappers around the woke functions

```python
def random_int(min: uint = 0, max: uint = MAX_UINT, **kwargs):
    def f():
        return generators.random_int(min=min, max=max, **kwargs)

    return f
```

To use a generator, a static member on the Fuzz class is declared. Then the parameter name to the flow must match the name of the member.

```python
    st_random_amount = st.random_int(min=50, max=200)
    @flow()
    def deposit(self, st_random_amount : uint) -> None:
        pass
```

### Custom Strategies

These methods can be composed to construct dataclasses for custom types.  For example if we have a simple dataclass `Balance` we can define a generator for this type.

```python
@dataclass
class Balance:
    account : Account
    balance : uint

def random_balance(min: uint = 0, max: uint = st.MAX_UINT, **kwargs):

    def f():
        return Balance(
            account=generators.random_address(),
            balance=generators.random_int(min=min, max=max, **kwargs),
        )

    return f
```

Using the custom strategy follows the same pattern with a static member on the FuzzTest and a parameter name that matches the name of the member.

```python
    st_balance = random_balance(min=500, max=4000)

    @flow()
    def balance_flow(self, st_balance: Balance) -> None:
        print("balance", st_balance)
```

```
balance Balance(account=0x1ca586c6eb22351841e246473bcecfed8957159e, balance=3351)
```

This abstraction of generating all random data outside of the flow is what makes corpus replay possible.  

## Collecting data

The json lines format is used for recording flows.  All data is currently saved to the `.replay` folder.  

To enable recording, use the `record` parameter on the run method for the `FuzzTest`

```python
BankTest().run(sequences_count=3, flows_count=10, record=True)
```

Example recorded sequence of 3 flows in json lines format. 

```json
{
  "0": {
    "0": {
      "name": "deposit",
      "params": {
        "account": "0x70997970c51812dc3a010c7d01b50e0d17dc79c8",
        "amount": 33
      }
    }
  }
}
{
  "0": {
    "1": {
      "name": "withdraw",
      "params": {
        "account": "0x70997970c51812dc3a010c7d01b50e0d17dc79c8",
        "amount": 43
      }
    }
  }
}
{
  "0": {
    "2": {
      "name": "deposit",
      "params": {
        "account": "0x90f79bf6eb2c4f870365e785982e1f101e93b906",
        "amount": 12
      }
    }
  }
}
```

## Replay

Currently replay has to be enabled in the source of the test file, there is no command line yet for controlling these features.  to do so, 2 changes are necessary. 

Change the library used for strategies from the random generation. 

```python
from wokelib.generators.random import st
```

to the replay counterpart 

```python
from wokelib.generators.replay import st
```

Import `fuzz_test` from replay.  This overrides woke's run method with a version that does the replay 

```
    from wokelib.generators.replay import fuzz_test
```

then call load on the json file containing the replay data

```python
BankTest.load("replay.json")
```

## Objectives

- Record all sequences, flows and inputs
- Record all transaction data
- Replay any sequence
- Example simplification

## Dependencies

- Pyright
- jsons

## Full Example

### Contracts

```solidity
//SPDX-License-Identifier: ISC

pragma solidity 0.8.20;


contract Bank {
   event Deposit(address indexed account, uint256 amount);
   event Withdraw(address indexed account, uint256 amount);


   mapping (
    address => uint256) public accounts;

  function deposit(uint256 amount) public {
  	accounts[msg.sender]+=amount;
   emit Deposit(msg.sender,amount);

  }
  	
  function withdraw(uint256 amount) public {
  	accounts[msg.sender] -= amount;
   emit Withdraw(msg.sender,amount);

  }

}
```

### Python Fuzz Test

```python
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
        Deposit flow.

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
        Withdraw flow.

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



```




