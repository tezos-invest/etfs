import logging

from fastapi import FastAPI
import typing

import config
import schemas
from pools.known_pools import find_pools
import itertools as it

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
