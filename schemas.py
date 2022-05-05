import datetime as dt
from typing import Optional

from pydantic import BaseModel


class PoolSpec(BaseModel):
    endpoint: str
    factory: str
    token_address: str
    token_id: Optional[str]
    pool_address: str
    lastActivityTime: dt.datetime
    tzips: str
    token_name: str
    token_symbol: str
    decimals: str
    tez_pool: int
    token_pool: int
    fee_factor: int
    tez_to_token_dbg: float
    token_to_tez_dbg: float
