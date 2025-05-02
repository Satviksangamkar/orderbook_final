
from pydantic import BaseModel, Field
from typing import List, Dict
from datetime import datetime

class PriceLevel(BaseModel):
    price: float
    amount: float

class DepthResponse(BaseModel):
    timestamp: datetime
    symbol: str
    percent: float
    bids: List[PriceLevel]
    asks: List[PriceLevel]

class DeltaResponse(BaseModel):
    timestamp: datetime
    symbol: str
    percent: float
    delta: float

class RatioResponse(BaseModel):
    timestamp: datetime
    symbol: str
    percent: float
    ratio: float

class TotalLiquidityResponse(BaseModel):
    timestamp: datetime
    symbol: str
    percent: float
    totalLiquidity: float

class MidSpreadResponse(BaseModel):
    timestamp: datetime
    symbol: str
    midPrice: float
    spread: float

class ImbalanceResponse(BaseModel):
    timestamp: datetime
    symbol: str
    percent: float
    imbalance: float

class WallEntry(BaseModel):
    price: float
    amount: float

class WallsResponse(BaseModel):
    timestamp: datetime
    symbol: str
    threshold: float
    walls: Dict[str, List[WallEntry]]

class CumulativeEntry(BaseModel):
    price: float
    cumulative: float

class CumulativeDepthResponse(BaseModel):
    timestamp: datetime
    symbol: str
    percent: float
    cumulativeBids: List[CumulativeEntry]
    cumulativeAsks: List[CumulativeEntry]
