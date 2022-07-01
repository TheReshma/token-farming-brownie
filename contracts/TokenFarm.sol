// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import '@openzeppelin/contracts/access/Ownable.sol';
import '@openzeppelin/contracts/token/ERC20/IERC20.sol';

contract TokenFarm is Ownable {

    mapping(address => address) public tokenToPrice;
    // mapping token_address -> person_address -> staked amount
    mapping(address => mapping(address => uint256)) stakingBalance;

    function setPriceFeedContract (address _tokenAddress, address _priceFeed) public onlyOwner{
        tokenToPrice[_tokenAddress] = _priceFeed;
    }

    function stakeTokens (uint256 _amount, address _token) public{
        require(_amount > 0, "Amount must be greater than 0");
        require(tokenIsAllowed(_token), "Token is currently not allowed");
        IERC20.transferFrom(msg.sender, address(this) ,_amount);
        stakingBalance[_token][msg.sender] = stakingBalance[_token][msg.sender] + _amount;
    }

    function unstakeTokens (address _token) public{
        uint256 balance = stakingBalance[_token][msg.sender];
        require(balance > 0, "You haven't staked anything. Unstaking isn't possible");
        IERC20(_token).transfer(msg.sender, balance);
        stakingBalance[_token][msg.sender] = 0;
    }
}


