
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