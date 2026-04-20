"""
collect_ws.py
-------------
Collects BTC/USDT top-of-book data via the Binance WebSocket stream.
Saves to data/orderbook_ws.csv.

The bookTicker stream fires a message every time the best bid or ask
changes — typically many times per second for BTC/USDT. This gives
sub-second resolution without polling.

Usage:
    python collect_ws.py              # runs for 15 minutes (default)
    python collect_ws.py --minutes 10
    python collect_ws.py --minutes 5 --out data/test_ws.csv

No API key required.
"""

import asyncio
import json
import argparse
import signal
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import websockets

URL = "wss://stream.binance.com:9443/ws/btcusdt@bookTicker"


async def collect(duration_minutes: float, out_path: str) -> None:
    Path(out_path).parent.mkdir(exist_ok=True)

    duration_s = duration_minutes * 60
    rows = []
    start = asyncio.get_event_loop().time()
    last_print = start

    print(f"Connecting to Binance WebSocket stream...")
    print(f"Collecting for {duration_minutes} min → {out_path}\n")

    async with websockets.connect(URL) as ws:
        while True:
            elapsed = asyncio.get_event_loop().time() - start
            if elapsed >= duration_s:
                break

            try:
                msg = json.loads(await asyncio.wait_for(ws.recv(), timeout=5.0))
            except asyncio.TimeoutError:
                print("  [warn] no message for 5s, reconnecting...")
                break

            rows.append({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "bid_price": float(msg["b"]),
                "bid_vol":   float(msg["B"]),
                "ask_price": float(msg["a"]),
                "ask_vol":   float(msg["A"]),
            })

            # Print progress every 30 seconds
            now = asyncio.get_event_loop().time()
            if now - last_print >= 30:
                mid = (rows[-1]["bid_price"] + rows[-1]["ask_price"]) / 2
                print(f"  t={int(elapsed):>4}s  msgs={len(rows):>6}  mid={mid:.2f}")
                last_print = now

    df = pd.DataFrame(rows)
    df.to_csv(out_path, index=False)
    print(f"\nSaved {len(df)} rows to {out_path}")
    print(f"Average update frequency: {len(df) / (duration_s):.1f} msgs/sec")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--minutes", type=float, default=15.0)
    parser.add_argument("--out",     type=str,   default="data/orderbook_ws.csv")
    args = parser.parse_args()

    asyncio.run(collect(args.minutes, args.out))
