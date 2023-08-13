# WokeLib

An collection of decorators and functions I use for fuzz testing smart contracts with [Woke](https://github.com/Ackee-Blockchain/woke)

## Features

* Corpus Replay

 

## Generating data

I modelled this setup after hypothesis such that the generation of all random values is done outside of the flows and sequences in the woke fuzz class.  The reason I prefer this style relates to reproducability.  With this style, all inputs parameters to the flows can be recorded. 



### The given decorator



The given decorator accepts named parameters which are strategies for generating random data for the corresponding parameter in the decorated method.  In this example below the `random_int` strategy will be used to generate random data for the amount parameter on deposit.

```python
    @flow()
    @given(
        amount=st.random_int(max=50),
    )
    def deposit(self, amount) -> None:
        pass
```



This abstraction of generating all random data outside of the flow is what makes corpus replay possible.  



## Collecting data

The json lines format is used for recording flows.  All data is currently saved to the `.replay` folder.  

To enable recording, add the `collector` decorator to the pre_sequence method.

```python
    @collector()
    def pre_sequence(self) -> None:
        pass
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
    st.load("replay.json")
```



## Objectives

- Record all sequences, flows and inputs
- Record all transaction data
- Replay any sequence
- Example simplification

## Dependencies

- Pyright

## Full Example

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

```python
from woke.testing.core import default_chain

from woke.testing.core import default_chain

from woke.development.transactions import may_revert

from wokelib import given, collector
from woke.testing.fuzzing import flow
from wokelib import get_address, MAX_UINT

from pytypes.contracts.bank import Bank

#we load different depending on if we are doing random generation or a replay 
Replay = False 
if Replay:
    from wokelib.generators.replay import st
    from wokelib.generators.replay import fuzz_test
    #no cli yet
    import os
   # replay_file = os.environ['WOKE_REPLAY']
    st.load("replay.json")
else:
    from wokelib.generators.random import st
    from woke.testing.fuzzing import fuzz_test

import random

# random.seed(44)


class BankTest(fuzz_test.FuzzTest):


    accounts = list()

    # collector decorator on the pre_sequence turns on the recording right now
    @collector()
    def pre_sequence(self) -> None:
        self._bank = Bank.deploy()
        BankTest.accounts.clear()
        for a in default_chain.accounts[1:5]:
            BankTest.accounts.append(a)


    @flow()
    @given(
        account=st.choose(accounts),
        amount=st.random_int(max=50),
    )
    def deposit(self, account, amount) -> None:
        balance = self._bank.accounts(account)
        overflow = balance + amount > MAX_UINT
        with may_revert() as e:
            tx=self._bank.deposit(amount,from_=account)
            assert balance + amount == self._bank.accounts(account)
            assert tx.events[0]==Bank.Deposit(get_address(account), amount)
            assert overflow == False 
        if e.value is not None:
            assert overflow



    @flow()
    @given(
        account=st.choose(accounts),
        amount=st.random_int(max=50))
    def withdraw(self,account, amount) -> None:
        balance = self._bank.accounts(account)
        underflow = balance < amount
        with may_revert() as e:
            tx=self._bank.withdraw(amount, from_=account)
            assert underflow==False
            assert balance-amount == self._bank.accounts(account)
            assert tx.events[0]==Bank.Withdraw(get_address(account), amount)
        if e.value is not None:
            assert underflow





@default_chain.connect()
def test_default():
    default_chain.set_default_accounts(default_chain.accounts[0])
    BankTest().run(sequences_count=1, flows_count=20)
```


