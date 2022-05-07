import itertools as it
import logging
import typing

from fastapi import FastAPI

import config
import schemas
from pools.contract_data import get_etf_portfolio
from pools.known_pools import find_pools

logger = logging.getLogger(__name__)
app = FastAPI(title="Tezos ETF")

KNOWN_POOLS: typing.List[schemas.PoolSpec]


@app.on_event("startup")
async def on_startup():
    global KNOWN_POOLS
    # KNOWN_POOLS = [schemas.PoolSpec(**e) for e in find_pools(config.TZKT_ENDPOINT)]
    KNOWN_POOLS = [schemas.PoolSpec(**e) for e in it.islice(find_pools(config.TZKT_ENDPOINT), 2)]
    logger.info("App started")


@app.on_event("shutdown")
async def on_shutdown():
    logger.info("Shutdown")


@app.get("/pools", response_model=typing.List[schemas.PoolSpec])
async def get_pools() -> typing.List[schemas.PoolSpec]:
    return KNOWN_POOLS


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
