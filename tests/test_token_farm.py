from scripts.deploy import deploy_farm_token_and_dapp_token, KEPT_BALANCE
from scripts.helpful_scripts import LOCAL_BLOCKCHAIN_ENV, get_account, get_contract
from brownie import network, exceptions
import pytest

def quick():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENV:
        pytest.skip()

def test_add_allowed_tokens():
    quick()
    account = get_account()
    non_owner = get_account(index=1)
    token_farm , dapp_token = deploy_farm_token_and_dapp_token()
    token_farm.addAllowedTokens(dapp_token.address, {"from": account})
    assert token_farm.allowedTokens(0) == dapp_token.address
    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.addAllowedTokens(dapp_token.address, {"from": non_owner})
