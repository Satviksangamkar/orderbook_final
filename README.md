# Order Book Analytics API

This project is a FastAPI-based service that streams live Binance Futures order book data using the Cryptofeed library. It exposes multiple endpoints to analyze market depth, liquidity, order imbalances, and more.

## Features

- Depth view (±X% from mid)
- Bid-Ask Delta
- Liquidity Ratio
- Total Order Book Liquidity
- Mid Price & Spread
- Order Imbalance
- Order Walls (≥ volume threshold)
- Cumulative Depth
- Top N Price Levels by Size
- VWAP (Volume-Weighted Average Price)
- Liquidity Change over Time

## Data Source

- Exchange: Binance Futures
- Channel: L2_BOOK (order book snapshots)
- Feed Handler: Cryptofeed

## Tech Stack

- Python
- FastAPI
- Cryptofeed
- MongoDB (optional for logging endpoint responses)

## Run Locally

```bash
uvicorn main:app --reload

