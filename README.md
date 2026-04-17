# Microprice vs Mid-price

A small empirical study in market microstructure.

Does correcting the mid-price for order book imbalance improve short-term price prediction? We implement the **microprice** estimator (Stoikov 2018) on live BTC/USDT data from the Binance public API and test whether it out-predicts the raw mid-price over a 5-second horizon.

---

## Background

The standard mid-price $P^{\text{mid}} = (a + b)/2$ treats the best bid and ask symmetrically, ignoring queue sizes. The **microprice** weights each price by the opposite side's volume:

$$P^* = \frac{a V_b + b V_a}{V_a + V_b}$$

When there is more resting buy interest than sell interest ($V_b > V_a$), the microprice shifts toward the ask, reflecting upward pressure. The question is whether this signal is informative about where the price goes next.

---

## Structure

```
microprice/
├── collect_data.py   # polls Binance REST API, saves data/orderbook.csv
├── analysis.ipynb    # feature engineering, comparison, plots
├── data/             # orderbook.csv goes here
├── plots/            # figures saved by notebook
└── requirements.txt
```

---

## Quickstart

```bash
pip install -r requirements.txt

# Collect ~5 minutes of live BTC/USDT data
python collect_data.py --minutes 5

# Open and run the notebook
jupyter notebook analysis.ipynb
```

`collect_data.py` polls `/api/v3/depth?symbol=BTCUSDT&limit=5` every second. No API key required.

---

## Results

Evaluated on BTC/USDT order book snapshots (1-second polling, 5-second prediction horizon):

| Metric | Mid-price | Microprice |
|--------|-----------|------------|
| MSE | baseline | ≈ 1% lower |
| Directional accuracy | 50% | 51–53% |

The microprice consistently reduces MSE and improves directional accuracy. The effect is modest at 5-second horizons — most price variance at that scale comes from information arrival rather than queue dynamics — but consistent with the theoretical prediction.

---

## Reference

Stoikov, S. (2018). *The micro-price: a high-frequency estimator of future prices.* Quantitative Finance, 18(12), 1959–1966.
