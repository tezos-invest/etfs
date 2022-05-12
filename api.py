import itertools as it
import logging
import typing

from fastapi import FastAPI

import config
import schemas
from pools.contract_data import get_etf_portfolio
from pools.known_pools import find_pools
from pools.datasources import SpicyaDataSource
from pools.portfolio import RebalancedPortfolioModel

logger = logging.getLogger(__name__)
app = FastAPI(title="Tezos ETF")

KNOWN_POOLS: typing.List[schemas.PoolSpec]
SPICY_SOURCE: SpicyaDataSource


@app.on_event("startup")
async def on_startup():
    global KNOWN_POOLS, SPICY_SOURCE
    # KNOWN_POOLS = [schemas.PoolSpec(**e) for e in find_pools(config.TZKT_ENDPOINT)]
    KNOWN_POOLS = [schemas.PoolSpec(**e) for e in find_pools(config.TZKT_ENDPOINT)]
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
