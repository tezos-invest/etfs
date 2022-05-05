import json
import logging

from tzktpy import contract, bigmap

# https://madfish.crunch.help/quipu-swap/quipu-swap-for-developers

QUIPI_DATA = {
    'mainnet': {
        'endpoint': 'https://api.tzkt.io',
        'factory': {
            'FA1.2': 'KT1FWHLMk5tHbwuSsp31S4Jum4dTVmkXpfJw',
            'FA2': 'KT1PvEyN1xCFCgorN92QCfYjw3axS6jawCiJ',
        }
    },
    'hangzhou': {
        'factory': {
            'FA1.2': 'KT1HrQWkSFe7ugihjoMWwQ7p8ja9e18LdUFn',
            'FA2': 'KT1Dx3SZ6r4h2BZNQM8xri1CtsdNcAoXLGZB',
        },
        'endpoint': 'http://api.hangzhou2net.tzkt.io',
    }
}


def find_contracts_by_address(endpoint, factory):
    domain = QUIPI_DATA[endpoint]['endpoint']
    result_contracts = contract.Contract.get(creator=factory, domain=domain, includeStorage=True)

    return result_contracts


# https://github.com/madfish-solutions/quipuswap-sdk/blob/4c38ce4a44d7c15da197ecb28e6521f3ac8ff527/src/defaults.ts#L1
FEE_FACTOR = 997


def estimateTokenToTez(token_value, tez_pool, token_pool):
    if not token_value:
        return 0
    tokenInWithFee = token_value * FEE_FACTOR
    numerator = tokenInWithFee * tez_pool
    denominator = token_pool * 1000 + tokenInWithFee

    return numerator / denominator


def estimateTezToToken(tez_value, tez_pool, token_pool):
    if not tez_value:
        return 0
    tezInWithFee = tez_value * FEE_FACTOR
    numerator = tezInWithFee * token_pool
    denominator = tez_pool * 1000 + tezInWithFee

    return numerator / denominator


def find_available_pools_for_factory(endpoint, factory):
    '''
        export function estimateTokenToTez(
          dexStorage: any,
          tokenValue: BigNumber.Value
        ) {
          const tokenValueBN = new BigNumber(tokenValue);
          assertNat(tokenValueBN);
          if (tokenValueBN.isZero()) return new BigNumber(0);

          const tokenInWithFee = new BigNumber(tokenValue).times(FEE_FACTOR);
          const numerator = tokenInWithFee.times(dexStorage.storage.tez_pool);
          const denominator = new BigNumber(dexStorage.storage.token_pool)
            .times(1000)
            .plus(tokenInWithFee);
          return numerator.idiv(denominator);
        }

        обменный курс тезос на другой токен считается как tez_value * FEE_FACTOR * tez_pool/(token_pool * 1000 + tez_value * FEE_FACTOR)
    '''

    # https://github.com/madfish-solutions/quipuswap-sdk/blob/4c38ce4a44d7c15da197ecb28e6521f3ac8ff527/src/estimates.ts#L21

    cntrs = find_contracts_by_address(endpoint, factory)
    for cntr in cntrs:
        cntr_storage = cntr.storage_data

        if cntr_storage:
            cntr_storage = cntr_storage.get('storage')
        if cntr_storage:
            token_address = cntr_storage.get('token_address')
            token_id = cntr_storage.get('token_id')
            pool_address = cntr.address

            token_info = get_token_info(endpoint, token_address)
            tez_pool = int(cntr_storage['tez_pool'])
            token_pool = int(cntr_storage['token_pool'])
            if token_info:
                token_name = token_info.get('name')
                token_symbol = token_info.get('symbol')
                decimals = token_info.get('decimals')
                if token_name and token_symbol and decimals:
                    yield {
                        'endpoint': endpoint,
                        'factory': factory,
                        'token_address': token_address,
                        'token_id': token_id,
                        'pool_address': pool_address,
                        'lastActivityTime': cntr.last_activity_time,
                        'tzips': cntr.full_data['tzips'][0],
                        # 'token_info': token_info,
                        'token_name': token_name,
                        'token_symbol': token_symbol,
                        'decimals': decimals,
                        'tez_pool': tez_pool,
                        'token_pool': token_pool,
                        'fee_factor': FEE_FACTOR,

                        'tez_to_token_dbg': estimateTokenToTez(1, tez_pool, token_pool),
                        'token_to_tez_dbg': estimateTezToToken(1, tez_pool, token_pool),
                    }


def find_pools(endpoint):
    endpoint_data = QUIPI_DATA[endpoint]
    for f_type, f_addr in endpoint_data['factory'].items():
        yield from find_available_pools_for_factory(endpoint, f_addr)


def get_token_info(endpoint, addr):
    domain = QUIPI_DATA[endpoint]['endpoint']
    contract_storage = json.loads(contract.Contract.storage(addr, domain=domain))

    bigmap_id = (
        None
        # or contract_storage.get('assets', {}).get('token_metadata')
        or contract_storage.get('token_metadata')
    )
    if not bigmap_id:
        return

    try:
        bigmap_data = bigmap.BigMapKey.by_bigmap(bigmap_id, domain=domain)
        token_info = bigmap_data[0].value.get('token_info')
        if token_info:
            return {k: bytes.fromhex(v).decode() for k, v in token_info.items()}
    except:
        logging.exception(f"can't get token info for {endpoint}, {addr}")


if __name__ == '__main__':
    # print(find_contracts_by_address('hangzhou', 'KT1Dx3SZ6r4h2BZNQM8xri1CtsdNcAoXLGZB'))
    for cntr in find_pools('hangzhou'):
        print(cntr)
    # print(list(find_available_pools('hangzhou', 'KT1Dx3SZ6r4h2BZNQM8xri1CtsdNcAoXLGZB')))
    # print(get_pool_view('hangzhou','KT1AwaUc4igCq5yWhYYj8RatGAKkGYMoJzN9'))
    # print(get_token_info('hangzhou', 'KT1AwaUc4igCq5yWhYYj8RatGAKkGYMoJzN9'))
    # print(bigmap.BigMapKey.by_bigmap(8614, domain = 'http://api.hangzhou2net.tzkt.io'))

    # print(bytes.fromhex('7465737420746f6b656e').decode())
