import datetime as dt
from typing import Optional, Dict, List

from pydantic import BaseModel, Extra, StrictStr, Field, validator


class Portfolio(BaseModel):
    class Asset(BaseModel):
        symbol: str = Field(..., min_length=1)
        weight: int = Field(..., gt=0, lte=100)

        class Config:
            extra = Extra.forbid
            allow_mutation = False

    assets: List[Asset]

    @validator("assets")
    def check_total_weight(cls, assets: List[Asset]) -> List[Asset]:
        if sum(asset.weight for asset in assets) != 100:
            raise ValueError("Invalid portfolio")
        return assets


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


class PortfolioSpec(BaseModel):
    assets: Dict[str, int]
    weights: Dict[str, int]
    tokens: Optional[Dict[str, str]]


class DailyResult(BaseModel):
    day: dt.datetime
    evaluation: float


class EmulationResult(BaseModel):
    result: List[DailyResult]

class OptimizationMetrics(BaseModel):
    profit_percent: float
    volatility: float
    weights: Dict[str, int]

class OptimizationResult(BaseModel):
    result: List[OptimizationMetrics]
