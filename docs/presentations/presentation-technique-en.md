---
marp: true
theme: default
paginate: true
---

# Walloon yields × climate — technical

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![pandas](https://img.shields.io/badge/pandas-2.x-150458?logo=pandas&logoColor=white)
![scipy](https://img.shields.io/badge/scipy-stats-8CAAE6?logo=scipy&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.x-F7931E?logo=scikitlearn&logoColor=white)

*Feature 6: linear baseline (complement)*

---

## Framing

Question: sensitivity of Walloon yields to **recent** climate variability.
Primary approach: statistics / BI. NUTS 2 map is in. ML is a simple
baseline, not the goal. No CMIP6 scenario in the observed table.

---

## Method

1. Eurostat yield (t/ha), ERA5 April–September season.
2. OLS **detrend** year → t/ha, per crop × territory.
3. Spearman (main) of the **residual** vs season z-scores.
4. Atypical year: residual z ≤ −1 **and** climate |z| ≥ 1.
5. Map: wheat × rainfall Spearman by province.
6. OLS: residual ~ temp + rain + ET0; **leave-one-year-out** vs naive (0).

---

## Stack

- **pandas**: tables, join.
- **scipy.stats**: `linregress`, `spearmanr`.
- **scikit-learn**: `LinearRegression` (no forest: n is too small).
- **matplotlib**: figures and choropleth (Agg backend).

Code: `src/agri_climat/ml.py` — `python -m agri_climat ml`

---

## ML vs statistics

- **Wheat**: naive MAE 0.51 → LOO 0.38 t/ha (R² ≈ 0.40). Best univariate
  = rainfall. Negative rain coefficient, in line with ρ ≈ −0.68.
- **Potato**: univariate temperature beats the 3-variable model
  (ET0 / heat collinearity, ET0 VIF ≈ 4).
- Other crops: LOO R² often **negative** — climate does not improve the
  out-of-sample diagnosis.

---

## Limits

- Correlation ≠ causation; n = 14–25; provinces not pooled.
- Noisy LOO; MAE in t/ha over R².
- 2016 wheat dip poorly captured out of sample.
- No CMIP6 / SSP (optional Feature 9, separate overlay).
