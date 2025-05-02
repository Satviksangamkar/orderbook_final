
from typing import Dict
from cryptofeed import FeedHandler
from cryptofeed.defines import L2_BOOK
from cryptofeed.exchanges import BinanceFutures

orderbook_data: Dict[str, Dict] = {}

async def orderbook_callback(book, receipt_timestamp):
    symbol = book.symbol.upper()
    orderbook_data[symbol] = {
        "timestamp": receipt_timestamp,
        "bids": [{"price": price, "amount": book.book.bids[price]}
                 for price in sorted(book.book.bids.keys(), reverse=True)],
        "asks": [{"price": price, "amount": book.book.asks[price]}
                 for price in sorted(book.book.asks.keys())]
    }

def get_orderbook_data(symbol: str):
    return orderbook_data.get(symbol.upper())

async def run_feed():
    f = FeedHandler()
    f.add_feed(BinanceFutures(
        symbols=['BTC-USDT-PERP', 'ETH-USDT-PERP'],
        channels=[L2_BOOK],
        max_depth=1000,
        callbacks={L2_BOOK: orderbook_callback}
    ))
    f.run(start_loop=False)
