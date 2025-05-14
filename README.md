# VIX Calculator (CBOE White Paper Based)

A Python-based implementation of the official **CBOE VIX Index** calculation method, using historical SPX options data.
The goal is to replicate the VIX index using real SXO option quotes, as a way to understand the mechanics of implied volatility estimation, and to enable further research on volatility modeling.


**Cautions**
The csv Data sampled doesn't have sufficient data to fullfill the condition that the expiration day has to be between 23 to 37 days. That is, only the nearest two expiration dates are extracted. Try to adjust a little bit while using it, Thanks! 

---

## Features
# VIX Index Calculator (Based on CBOE White Paper)

This repository contains a Python implementation of the official CBOE VIX Index methodology, applied to historical option data.

The goal is to replicate the VIX index using real SXO option quotes, as a way to understand the mechanics of implied volatility estimation, and to enable further research on volatility modeling.

---

## How it works

- Computes forward index price using call-put parity
- Determines the ATM strike (K₀), with correction if F < K₀
- Filters OTM options based on bid and volume, using the CBOE "stop rule"
- Calculates squared variance (σ²) using ΔK and Q(K)
- Combines near- and next-term variances to get the 30-day annualized VIX

---

## Example usage

```python
import pandas as pd
from VIX_calculator import VIXCalculator

df = pd.read_csv("arranged SXO data (200603-201012).csv")
vix_calc = VIXCalculator(df)

vix = vix_calc.calculate_vix("2006-03-01")
print(vix)  # Expected: ~11.31

---

## Quick Start

```python
from VIX_calculator import VIXCalculator
import pandas as pd

df = pd.read_csv("yourdata.csv")
vix_calc = VIXCalculator(df)

vix = vix_calc.calculate_vix("{objectdate}")

---

## Sample output

Date: 
Near-term: 
Next-term: 
F = , adjusted K₀ = 
VIX = 

---

## Notes

- Data used in this project was provided by the course instructor and contains historical SXO (TXO) option quotes from 2006–2010.
- This calculator assumes the dataset includes: strike price (K), option type (PC), bid/ask quotes, risk-free rate (rf), and time-to-expiry (T).
- Mid-price is calculated as (bid + ask) / 2.

---

## Author

Harvey Hsu  
Department of Economics, National Taipei University
