# VIX Calculator (CBOE White Paper Based)

A Python-based implementation of the official **CBOE VIX Index** calculation method, using historical SPX options data.

**Cautions**
The csv Data sampled doesn't have sufficient data to fullfill the condition that the expiration day has to be between 23 to 37 days. That is, only the nearest two expiration dates are extracted. Try to adjust a little bit while using it, Thanks! 

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
from VIX_calculator import VIXCalculator
import pandas as pd

df = pd.read_csv("yourdata.csv")
vix_calc = VIXCalculator(df)

vix = vix_calc.calculate_vix("{objectdate}")
```
---

## Sample output

Date: 

Near-term: 

Next-term: 

F = , adjusted K₀ = 

VIX = 

---

## Notes
- This calculator assumes the dataset includes: strike price (K), option type (PC), bid/ask quotes, risk-free rate (rf), and time-to-expiry (T).
- Mid-price is calculated as (bid + ask) / 2.
- Time to expiry T is in days, converted to years.

---

## Author

Harvey Hsu  

Department of Economics, National Taipei University

Email: fujimahiroto@gmail.com

GitHub: [@harveysgisidt](https://github.com/harveysgisidt)

