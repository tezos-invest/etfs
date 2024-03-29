import config
from pools.known_pools import QUIPI_DATA
from tzktpy import bigmap


def get_etf_portfolio(owner, contract_address):
    domain = QUIPI_DATA[config.TZKT_ENDPOINT]['endpoint']
    # contract_storage = json.loads(contract.Contract.storage())
    result = bigmap.BigMap.by_contract(contract_address, domain=domain)
    portfolio_ptr = None
    for bm in result:
        if bm.path == 'portfolios':
            portfolio_ptr = bm.ptr

    if portfolio_ptr is None:
        raise ValueError(f"can't find portfolios path in {contract_address}")

    bigmap_data = bigmap.BigMapKey.by_bigmap(portfolio_ptr, domain=domain, key=owner)
    if len(bigmap_data) == 0:
        return None

    if len(bigmap_data) > 1:
        raise ValueError(f"multiple bigmap entries for owner = {owner}")

    return bigmap_data[0].value


if __name__ == '__main__':
    print(get_etf_portfolio('tz1LQjdKgiAsHkYMzBH2HFDcynf7QSd5Z4Eg'))
