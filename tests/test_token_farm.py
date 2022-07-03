from web3 import Web3
from scripts.deploy import deploy_farm_token_and_dapp_token
from scripts.helpful_scripts import DECIMALS, LOCAL_BLOCKCHAIN_ENV, get_account, get_contract, INITIAL_VALUE
from brownie import network, exceptions, MockERC20
import pytest

def quick():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENV:
        pytest.skip()

def amount_staked():
    return Web3.toWei(1, "ether")

def randomERC20():
    account = get_account()
    erc20 = MockERC20.deploy({"from": account})
    return erc20

def test_add_allowed_tokens():
    quick()
    account = get_account()
    non_owner = get_account(index=1)
    token_farm , dapp_token = deploy_farm_token_and_dapp_token()
    token_farm.addAllowedTokens(dapp_token.address, {"from": account})
    assert token_farm.allowedTokens(0) == dapp_token.address
    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.addAllowedTokens(dapp_token.address, {"from": non_owner})

def test_token_is_allowed():
    quick()
    account = get_account()
    token_farm , dapp_token = deploy_farm_token_and_dapp_token()
    token_farm.addAllowedTokens(dapp_token.address, {"from": account})
    assert token_farm.tokenIsAllowed(dapp_token.address, {"from": account}) == True

def test_set_price_feed_contract():
    quick()
    account = get_account()
    non_owner = get_account(index=1)
    token_farm , dapp_token = deploy_farm_token_and_dapp_token()
    token_farm.setPriceFeedContract( dapp_token.address, get_contract("eth_usd_price_feed"), {"from": account})
    assert token_farm.tokenToPrice(dapp_token.address) == get_contract("eth_usd_price_feed")
    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.setPriceFeedContract( dapp_token.address, get_contract("eth_usd_price_feed"), {"from": non_owner})

def test_stake_tokens(amount_staked = amount_staked()):
    quick()
    account = get_account()
    token_farm, dapp_token = deploy_farm_token_and_dapp_token()
    dapp_token.approve(token_farm.address, amount_staked, {"from": account})
    tx = token_farm.stakeTokens(amount_staked, dapp_token.address, {"from": account})
    tx.wait(1)
    assert (token_farm.stakingBalance(dapp_token.address, account.address) == amount_staked)
    assert token_farm.uniqueTokensStaked(account.address) == 1
    assert token_farm.stakers(0) == account.address
    return token_farm, dapp_token

def test_stake_unapproved_tokens():
    quick()
    account = get_account()
    token_farm, dapp_token = deploy_farm_token_and_dapp_token()
    amount = amount_staked()
    random_erc20 = randomERC20()
    random_erc20.approve(token_farm.address, amount, {"from": account})
    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.stakeTokens(amount, random_erc20.address, {"from": account})

def test_get_user_total_balance():
    quick()
    account = get_account()
    token_farm, dapp_token = deploy_farm_token_and_dapp_token()
    amount = amount_staked()
    random_erc20 = randomERC20()
    token_farm.addAllowedTokens(random_erc20.address, {"from": account})
    token_farm.setPriceFeedContract( random_erc20.address, get_contract("eth_usd_price_feed"), {"from": account})
    random_erc20.approve(token_farm.address, amount, {"from": account})
    token_farm.stakeTokens(amount, random_erc20.address, {"from": account})
    random_erc20_stake_amount = amount * 2
    random_erc20.approve(token_farm.address, random_erc20_stake_amount, {"from": account})
    tx = token_farm.stakeTokens(random_erc20_stake_amount, random_erc20.address, {"from": account})
    tx.wait(1)
    total_eth_balance = token_farm.getUserTotalValue(account.address)
    assert total_eth_balance == INITIAL_VALUE * 3

def test_get_token_eth_price():
    quick()
    account = get_account()
    token_farm, dapp_token = deploy_farm_token_and_dapp_token()
    assert (token_farm.getTokenValue(dapp_token.address) == ( INITIAL_VALUE, DECIMALS))

def test_get_staked_eth_value():
    quick()
    account = get_account()
    amount = amount_staked()
    token_farm, dapp_token = deploy_farm_token_and_dapp_token()
    token_farm.addAllowedTokens(dapp_token.address, {"from": account})
    dapp_token.approve(token_farm.address, amount, {"from": account})
    tx = token_farm.stakeTokens(amount, dapp_token.address, {"from": account})
    tx.wait(1)
    eth_balance_token = token_farm.getUserSingleTokenValue( account.address, dapp_token.address)
    assert eth_balance_token == Web3.toWei(2000, "ether")

def test_issue_tokens():
    quick()
    account = get_account()
    token_farm, dapp_token = test_stake_tokens()
    starting_balance = dapp_token.balanceOf(account.address)
    token_farm.issueTokens({"from": account})
    assert ( dapp_token.balanceOf(account.address) == starting_balance + INITIAL_VALUE )