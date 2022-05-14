import logging
import typing

import pandas as pd
from fastapi import FastAPI

import config
import schemas
from pools.contract_data import get_etf_portfolio
from pools.datasources import SpicyaDataSource
from pools.known_pools import find_pools
from portfolios.portfolio import RebalancedPortfolioModel, MarkovitzOptimization

logger = logging.getLogger(__name__)
app = FastAPI(title="Tezos ETF")

KNOWN_POOLS: typing.List[schemas.PoolSpec]
SPICY_SOURCE: SpicyaDataSource


@app.on_event("startup")
async def on_startup():
    global KNOWN_POOLS, SPICY_SOURCE
    # KNOWN_POOLS = [schemas.PoolSpec(**e) for e in find_pools(config.TZKT_ENDPOINT)]

    try:
        logging.info(f'trying to load cached data')
        pools_data = pd.read_pickle('cached-pools.pkl.gz').to_dict(orient='records')
    except:
        logger.warning(f"can't load cached pool data")

        pools_data = find_pools(config.TZKT_ENDPOINT)
        pd.DataFrame(pools_data).to_pickle('cached-pools.pkl.gz')

    KNOWN_POOLS = [schemas.PoolSpec(**e) for e in pools_data]
    SPICY_SOURCE = SpicyaDataSource()
    logger.info("App started")


@app.on_event("shutdown")
async def on_shutdown():
    logger.info("Shutdown")


@app.get("/pools", response_model=typing.List[schemas.PoolSpec])
async def get_pools() -> typing.List[schemas.PoolSpec]:
    return KNOWN_POOLS


@app.post("/emulate", response_model=schemas.EmulationResult)
async def emulate(portfolio: schemas.Portfolio) -> schemas.EmulationResult:
    symbols = [asset.symbol for asset in portfolio.assets]
    history = SPICY_SOURCE.get_history(symbols)
    tokens = [SPICY_SOURCE.get_hash(symbol) for symbol in symbols]

    token_weights = {token: asset.weight for token, asset in zip(tokens, portfolio.assets)}
    emulation_result = RebalancedPortfolioModel(history).emulate(token_weights)

    total = emulation_result['portfolio-totals']
    return schemas.EmulationResult(result=[
        schemas.DailyResult(day=day_data['day'], evaluation=day_data['price'])
        for day_data in total
    ])


@app.post("/markovitz-optimize", response_model=schemas.OptimizationResult)
async def emulate(portfolio: schemas.Portfolio) -> schemas.OptimizationResult:
    symbols = [asset.symbol for asset in portfolio.assets]
    history = SPICY_SOURCE.get_history(symbols)

    optimization_result = MarkovitzOptimization(history).do_optimize()
    optimization_result = optimization_result[['profit_percent', 'volatility', 'weights']]

    return schemas.OptimizationResult(
        result=[
            schemas.OptimizationMetrics(**metrics) for metrics in optimization_result.to_dict(orient='records')
        ]
    )


def map_v_type(dct, target_type):
    return {k: target_type(v) for k, v in dct.items()}


@app.get("/portfolio", response_model=schemas.PortfolioSpec)
async def get_portfolio(owner: str) -> schemas.PortfolioSpec:
    portfolio = get_etf_portfolio(owner)
    assets = map_v_type(portfolio['assets'], int)
    weights = map_v_type(portfolio['weights'], int)
    tokens = portfolio['tokens']
    tokens = {k: v.get('fa12') or v.get('fa2', {}).get('address') for k, v in tokens.items()}

    return schemas.PortfolioSpec(assets=assets, weights=weights, tokens=tokens)
