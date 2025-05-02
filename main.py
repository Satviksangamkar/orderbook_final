
import asyncio
import logging
from datetime import datetime
from decimal import Decimal
from fastapi import FastAPI, Query, HTTPException
from pymongo import MongoClient

from feedhandler import get_orderbook_data, run_feed, orderbook_data
from schemas import (
    DepthResponse, DeltaResponse, RatioResponse,
    TotalLiquidityResponse, MidSpreadResponse,
    ImbalanceResponse, WallsResponse, CumulativeDepthResponse
)

MONGO_URI = "mongodb+srv://satvik:Stankarrk@satvik.kimjuo9.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(MONGO_URI)
db = client["cryptofeed_db"]

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(run_feed())

@app.get("/")
def root():
    return {"message": "Order Book API running. Use /api/orderbook/* endpoints."}

@app.get("/api/orderbook/symbols")
def list_symbols():
    return list(orderbook_data.keys())

def _to_decimal(f):
    return Decimal(str(f))

def _store(collection: str, doc: dict):
    db[collection].insert_one(doc)

@app.get("/api/orderbook/depth", response_model=DepthResponse)
def depth(symbol: str = Query(...), percent: float = Query(1.0, ge=0.1, le=10.0)):
    data = get_orderbook_data(symbol)
    if data is None:
        raise HTTPException(status_code=404, detail="No data available for symbol")
    try:
        pct = _to_decimal(percent)
        bids, asks = data["bids"], data["asks"]
        best_bid = _to_decimal(max(b["price"] for b in bids))
        best_ask = _to_decimal(min(a["price"] for a in asks))
        bid_thresh = best_bid * (Decimal("1") - pct/Decimal("100"))
        ask_thresh = best_ask * (Decimal("1") + pct/Decimal("100"))
        fb = [b for b in bids if _to_decimal(b["price"]) >= bid_thresh]
        fa = [a for a in asks if _to_decimal(a["price"]) <= ask_thresh]
        doc = {
            "timestamp": datetime.utcnow(),
            "symbol": symbol.upper(),
            "percent": float(pct),
            "bids": fb,
            "asks": fa
        }
        _store("depth_view", doc)
        return doc
    except Exception as e:
        logging.exception("Depth endpoint failed")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/orderbook/total", response_model=TotalLiquidityResponse)
def liquidity(symbol: str = Query(...), percent: float = Query(1.0, ge=0.1, le=10.0)):
    data = get_orderbook_data(symbol)
    if data is None:
        raise HTTPException(status_code=404, detail="No data available for symbol")
    pct = Decimal(str(percent))
    bids, asks = data["bids"], data["asks"]
    best_bid = max(Decimal(str(b["price"])) for b in bids)
    best_ask = min(Decimal(str(a["price"])) for a in asks)
    bid_thresh = best_bid * (Decimal("1") - pct / Decimal("100"))
    ask_thresh = best_ask * (Decimal("1") + pct / Decimal("100"))
    fb = [b for b in bids if Decimal(str(b["price"])) >= bid_thresh]
    fa = [a for a in asks if Decimal(str(a["price"])) <= ask_thresh]
    total = sum(Decimal(str(b["amount"])) for b in fb) + sum(Decimal(str(a["amount"])) for a in fa)
    return {
        "timestamp": datetime.utcnow(),
        "symbol": symbol.upper(),
        "percent": float(pct),
        "totalLiquidity": float(total)
    }

@app.get("/api/orderbook/delta", response_model=DeltaResponse)
def delta(symbol: str = Query(...), percent: float = Query(1.0, ge=0.1, le=10.0)):
    data = get_orderbook_data(symbol)
    if data is None:
        raise HTTPException(status_code=404, detail="No data available for symbol")
    pct = _to_decimal(percent)
    bids, asks = data["bids"], data["asks"]
    best_bid = _to_decimal(max(b["price"] for b in bids))
    best_ask = _to_decimal(min(a["price"] for a in asks))
    bid_thresh = best_bid * (Decimal("1") - pct / Decimal("100"))
    ask_thresh = best_ask * (Decimal("1") + pct / Decimal("100"))
    fb = [b for b in bids if _to_decimal(b["price"]) >= bid_thresh]
    fa = [a for a in asks if _to_decimal(a["price"]) <= ask_thresh]
    bid_total = sum(_to_decimal(b["amount"]) for b in fb)
    ask_total = sum(_to_decimal(a["amount"]) for a in fa)
    delta_val = bid_total - ask_total
    return {
        "timestamp": datetime.utcnow(),
        "symbol": symbol.upper(),
        "percent": float(pct),
        "delta": float(delta_val)
    }

@app.get("/api/orderbook/ratio", response_model=RatioResponse)
def ratio(symbol: str = Query(...), percent: float = Query(1.0, ge=0.1, le=10.0)):
    data = get_orderbook_data(symbol)
    if data is None:
        raise HTTPException(status_code=404, detail="No data available for symbol")
    pct = _to_decimal(percent)
    bids, asks = data["bids"], data["asks"]
    best_bid = _to_decimal(max(b["price"] for b in bids))
    best_ask = _to_decimal(min(a["price"] for a in asks))
    bid_thresh = best_bid * (Decimal("1") - pct / Decimal("100"))
    ask_thresh = best_ask * (Decimal("1") + pct / Decimal("100"))
    fb = [b for b in bids if _to_decimal(b["price"]) >= bid_thresh]
    fa = [a for a in asks if _to_decimal(a["price"]) <= ask_thresh]
    bid_total = sum(_to_decimal(b["amount"]) for b in fb)
    ask_total = sum(_to_decimal(a["amount"]) for a in fa)
    total = bid_total + ask_total
    ratio_val = (bid_total - ask_total) / total if total > 0 else Decimal("0")
    return {
        "timestamp": datetime.utcnow(),
        "symbol": symbol.upper(),
        "percent": float(pct),
        "ratio": float(ratio_val)
    }


@app.get("/api/orderbook/midspread", response_model=MidSpreadResponse)
def midspread(symbol: str = Query(...)):
    data = get_orderbook_data(symbol)
    if data is None:
        raise HTTPException(status_code=404, detail="No data available for symbol")
    bids, asks = data["bids"], data["asks"]
    best_bid = max(b["price"] for b in bids)
    best_ask = min(a["price"] for a in asks)
    mid = (best_bid + best_ask) / 2
    spread = best_ask - best_bid
    return {
        "timestamp": datetime.utcnow(),
        "symbol": symbol.upper(),
        "midPrice": mid,
        "spread": spread
    }

@app.get("/api/orderbook/imbalance", response_model=ImbalanceResponse)
def imbalance(symbol: str = Query(...), percent: float = Query(1.0, ge=0.1, le=10.0)):
    data = get_orderbook_data(symbol)
    if data is None:
        raise HTTPException(status_code=404, detail="No data available for symbol")
    pct = Decimal(str(percent))
    bids, asks = data["bids"], data["asks"]
    best_bid = max(Decimal(str(b["price"])) for b in bids)
    best_ask = min(Decimal(str(a["price"])) for a in asks)
    bid_thresh = best_bid * (Decimal("1") - pct / Decimal("100"))
    ask_thresh = best_ask * (Decimal("1") + pct / Decimal("100"))
    fb = [b for b in bids if Decimal(str(b["price"])) >= bid_thresh]
    fa = [a for a in asks if Decimal(str(a["price"])) <= ask_thresh]
    bid_total = sum(Decimal(str(b["amount"])) for b in fb)
    ask_total = sum(Decimal(str(a["amount"])) for a in fa)
    imb = (bid_total - ask_total) / (bid_total + ask_total) if (bid_total + ask_total) > 0 else Decimal("0")
    return {
        "timestamp": datetime.utcnow(),
        "symbol": symbol.upper(),
        "percent": float(pct),
        "imbalance": float(imb)
    }

@app.get("/api/orderbook/walls", response_model=WallsResponse)
def walls(symbol: str = Query(...), threshold: float = Query(10.0, gt=0)):
    data = get_orderbook_data(symbol)
    if data is None:
        raise HTTPException(status_code=404, detail="No data available for symbol")
    thresh = Decimal(str(threshold))
    bids = [b for b in data["bids"] if Decimal(str(b["amount"])) >= thresh]
    asks = [a for a in data["asks"] if Decimal(str(a["amount"])) >= thresh]
    return {
        "timestamp": datetime.utcnow(),
        "symbol": symbol.upper(),
        "threshold": float(thresh),
        "walls": {"bids": bids, "asks": asks}
    }

@app.get("/api/orderbook/cumulative", response_model=CumulativeDepthResponse)
def cumulative(symbol: str = Query(...), percent: float = Query(1.0, ge=0.1, le=10.0)):
    data = get_orderbook_data(symbol)
    if data is None:
        raise HTTPException(status_code=404, detail="No data available for symbol")
    pct = Decimal(str(percent))
    bids, asks = data["bids"], data["asks"]
    best_bid = max(Decimal(str(b["price"])) for b in bids)
    best_ask = min(Decimal(str(a["price"])) for a in asks)
    bid_thresh = best_bid * (Decimal("1") - pct / Decimal("100"))
    ask_thresh = best_ask * (Decimal("1") + pct / Decimal("100"))
    fb = [(b["price"], Decimal(str(b["amount"]))) for b in bids if Decimal(str(b["price"])) >= bid_thresh]
    fa = [(a["price"], Decimal(str(a["amount"]))) for a in asks if Decimal(str(a["price"])) <= ask_thresh]
    cum_bids, cum_asks = [], []
    running = Decimal("0")
    for price, amt in fb:
        running += amt
        cum_bids.append({"price": price, "cumulative": float(running)})
    running = Decimal("0")
    for price, amt in fa:
        running += amt
        cum_asks.append({"price": price, "cumulative": float(running)})
    return {
        "timestamp": datetime.utcnow(),
        "symbol": symbol.upper(),
        "percent": float(pct),
        "cumulativeBids": cum_bids,
        "cumulativeAsks": cum_asks
    }
