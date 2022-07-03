from web3 import Web3
from scripts.deploy import deploy_farm_token_and_dapp_token
from scripts.helpful_scripts import LOCAL_BLOCKCHAIN_ENV, get_account, get_contract
from brownie import network
import pytest

def quick():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENV:
        pytest.skip()

def amount_staked():
    return Web3.toWei(1, "ether")

def test_stake_and_issue_correct_amounts():
    quick()
    account = get_account()
    token_farm, dapp_token = deploy_farm_token_and_dapp_token()
    amount = amount_staked()
    dapp_token.approve(token_farm.address, amount, {"from": account})
    tx = token_farm.stakeTokens(amount, dapp_token.address, {"from": account})
    tx.wait(1)
    starting_balance = dapp_token.balanceOf(account.address)
    price_feed_contract = get_contract("dai_usd_price_feed")
    (_, price, _, _, _) = price_feed_contract.latestRoundData()
    amount_token_to_issue = (price/ 10 ** price_feed_contract.decimals()) * amount
    issue_tx = token_farm.issueTokens({"from": account})
    issue_tx.wait(1)
    assert (dapp_token.balanceOf(account.address) == amount_token_to_issue + starting_balance)

