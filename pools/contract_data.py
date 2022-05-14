import json
from tzktpy import contract, bigmap
from pools.known_pools import QUIPI_DATA
import config


def get_etf_portfolio(owner):
    domain = QUIPI_DATA[config.TZKT_ENDPOINT]['endpoint']
    contract_address = config.CONTRACT_ADDRESS[config.TZKT_ENDPOINT]
    # contract_storage = json.loads(contract.Contract.storage())
    result = bigmap.BigMap.by_contract(contract_address, domain=domain)
    portfolio_ptr = None
    for bm in result:
        if bm.path == 'portfolios':
            portfolio_ptr = bm.ptr

    if portfolio_ptr is None:
        raise ValueError(f"can't find portfolios path in {contract_address}")

    bigmap_data = bigmap.BigMapKey.by_bigmap(portfolio_ptr, domain=domain, key=owner)
    if len(bigmap_data)==0:
        return None

    if len(bigmap_data) > 1:
        raise ValueError(f"multiple bigmap entries for owner = {owner}")

    return bigmap_data[0].value


if __name__ == '__main__':
    print(get_etf_portfolio('tz1LQjdKgiAsHkYMzBH2HFDcynf7QSd5Z4Eg'))
