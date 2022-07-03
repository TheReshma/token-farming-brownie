from brownie import (
    network,
    accounts,
    config,
    interface,
    LinkToken,
    MockV3Aggregator,
    MockWETH,
    MockDAI,
    Contract,
)

LOCAL_BLOCKCHAIN_ENV = ["mainnet-fork-dev", "development"]
DECIMALS = 18
INITIAL_VALUE = 2000000000000000000000

contract_to_mock = {
    "eth_usd_price_feed": MockV3Aggregator,
    "dai_usd_price_feed": MockV3Aggregator,
    "fau_token": MockDAI,
    "weth_token": MockWETH,
}

def get_account(index=None, id=None):
    if index:
        return accounts[index]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENV :
        return accounts[0]
    if id:
        return accounts.load(id)
    return accounts.add(config["wallets"]["from_key"])

def get_contract(contract_name):
    contract_type = contract_to_mock[contract_name]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENV:
        if len(contract_type) <= 0:
            deploy_mocks()
        contract = contract_type[-1]
    else:
        try:
            contract_address = config["networks"][network.show_active()][contract_name]
            contract = Contract.from_abi( contract_type._name, contract_address, contract_type.abi)
        except KeyError:
            print(f"Theres some error here in getting contracts on {network.show_active()}")
    return contract

def deploy_mocks( decimals=DECIMALS, initial_value=INITIAL_VALUE):
    print(f"The active network is{network.show_active()}")
    account = get_account()
    link_token = LinkToken.deploy({"from": account})
    mock_price_feed = MockV3Aggregator.deploy(decimals, initial_value, {"from": account})
    mock_dai = MockDAI.deploy({"from": account})
    mock_weth = MockWETH.deploy({"from": account})

def verify_status():
    verify = (
        config["networks"][network.show_active()]["verify"]
        if config["networks"][network.show_active()].get('verify')
        else False
    )
    return verify

def issue_tokens():
    account = get_account()
    token_farm = get_contract("TokenFarm")
    tx = token_farm.issueTokens({"from": account})
    tx.wait(1)

def fund_with_link( contract_address, account=None, link_token=None, amount=1000000000000000000 ):
    account = account if account else get_account()
    link_token = link_token if link_token else get_contract("link_token")
    tx = interface.LinkTokenInterface(link_token).transfer( contract_address, amount, {"from": account})
    return tx




