"""
collect_data.py
---------------
Polls the Binance public REST API for BTC/USDT order book snapshots
and saves the result to data/orderbook.csv.

Usage:
    python collect_data.py --minutes 10

No API key required.
"""

import time
import argparse
import requests
import pandas as pd
from pathlib import Path
from datetime import datetime, timezone

BINANCE_URL = "https://api.binance.com/api/v3/depth"
SYMBOL      = "BTCUSDT"
POLL_INTERVAL_S = 1.0     # seconds between requests
DEPTH_LIMIT     = 5       # only need best bid/ask, 5 is the minimum valid value


def fetch_best_bid_ask() -> dict | None:

    try:
        r = requests.get(BINANCE_URL, params={"symbol": SYMBOL, "limit": DEPTH_LIMIT}, timeout=5)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print(f"  [warn] request failed: {e}")
        return None

    best_bid_price, best_bid_vol = float(data["bids"][0][0]), float(data["bids"][0][1])
    best_ask_price, best_ask_vol = float(data["asks"][0][0]), float(data["asks"][0][1])

    return {
        "timestamp":  datetime.now(timezone.utc).isoformat(),
        "bid_price":  best_bid_price,
        "bid_vol":    best_bid_vol,
        "ask_price":  best_ask_price,
        "ask_vol":    best_ask_vol,
    }


def collect(duration_minutes: float, out_path: str) -> None:
    Path(out_path).parent.mkdir(exist_ok=True)

    n_target = int(duration_minutes * 60 / POLL_INTERVAL_S)
    print(f"Collecting ~{n_target} snapshots over {duration_minutes} min → {out_path}")

    rows = []
    for i in range(n_target):
        row = fetch_best_bid_ask()
        if row:
            rows.append(row)
            if i % 30 == 0:
                mid = 0.5 * (row["bid_price"] + row["ask_price"])
                print(f"  t={i:>4}  mid={mid:.2f}")
        time.sleep(POLL_INTERVAL_S)

    df = pd.DataFrame(rows)
    df.to_csv(out_path, index=False)
    print(f"\nSaved {len(df)} rows to {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--minutes", type=float, default=5.0)
    parser.add_argument("--out",     type=str,   default="data/orderbook.csv")
    args = parser.parse_args()
    collect(args.minutes, args.out)
