// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import '@openzeppelin/contracts/access/Ownable.sol';
import '@openzeppelin/contracts/token/ERC20/IERC20.sol';
import '@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol';

contract TokenFarm is Ownable {

    mapping(address => address) public tokenToPrice;
    // mapping token_address -> person_address -> staked amount
    mapping(address => mapping(address => uint256)) stakingBalance;
    mapping(address => uint256) uniqueTokensStaked;
    address[] public stakers;
    address[] public allowedTokens;

    function setPriceFeedContract (address _tokenAddress, address _priceFeed) public onlyOwner{
        tokenToPrice[_tokenAddress] = _priceFeed;
    }

    function stakeTokens (uint256 _amount, address _token) public{
        require(_amount > 0, "Amount must be greater than 0");
        require(tokenIsAllowed(_token), "Token is currently not allowed");
        IERC20(_token).transferFrom(msg.sender, address(this), _amount);
        updateUniqueTokensStaked(msg.sender, _token);
        stakingBalance[_token][msg.sender] = stakingBalance[_token][msg.sender] + _amount;
        if (uniqueTokensStaked[msg.sender] == 1){
            stakers.push(msg.sender);
        }
    }

    function unstakeTokens (address _token) public{
        uint256 balance = stakingBalance[_token][msg.sender];
        require(balance > 0, "You haven't staked anything. Unstaking isn't possible");
        IERC20(_token).transfer(msg.sender, balance);
        stakingBalance[_token][msg.sender] = 0;
        uniqueTokensStaked[msg.sender] = uniqueTokensStaked[msg.sender] - 1;
    }

    function updateUniqueTokensStaked (address _user, address _token) public{
        if (stakingBalance[_token][_user] == 0){
            uniqueTokensStaked[_user] = uniqueTokensStaked[_user] + 1;
        }
    }

    function tokenIsAllowed (address _token) public view returns (bool){
        for ( uint256 index = 0; index < allowedTokens.length; index++){
            if (allowedTokens[index] == _token){
                return true;
            }
        }
        return false;
    }

    function addAllowedTokens (address _token) public onlyOwner{
        allowedTokens.push(_token);
    }

    function getTokenValue (address _token) public view returns (uint, uint){
        address priceFeedAddress = tokenToPrice[_token];
        AggregatorV3Interface priceFeed = AggregatorV3Interface(priceFeedAddress);
        ( , int256 price, , , ) = priceFeed.latestRoundData();
        uint256 decimals = uint256(priceFeed.decimals());
        return (uint256(price), decimals);
    }
}


