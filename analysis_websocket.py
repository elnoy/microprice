"""
analysis_websocket.py
---------------------
Computes directional accuracy of the microprice signal on
sub-second WebSocket data collected via collect_ws.py.

Usage:
    python analysis_websocket.py
"""

import numpy as np
import pandas as pd

df = pd.read_csv("data/orderbook_ws.csv", parse_dates=["timestamp"])
df = df.set_index("timestamp").sort_index()

b, a   = df["bid_price"], df["ask_price"]
Vb, Va = df["bid_vol"],   df["ask_vol"]

df["mid"]        = (a + b) / 2
df["microprice"] = (a * Vb + b * Va) / (Va + Vb)
df["future_mid"] = df["mid"].shift(-1)
df["delta_mid"]  = df["future_mid"] - df["mid"]
df["direction"]  = np.sign(df["delta_mid"])
df = df.dropna()

moving       = df[df["direction"] != 0]
micro_signal = np.sign(df["microprice"] - df["mid"])
da           = (micro_signal[moving.index] == moving["direction"]).mean()

print(f"Observations     : {len(df):,}")
print(f"Non-zero moves   : {len(moving):,}")
print(f"Directional accuracy (microprice) : {da:.1%}")
print(f"Coin-flip baseline                : 50.0%")
