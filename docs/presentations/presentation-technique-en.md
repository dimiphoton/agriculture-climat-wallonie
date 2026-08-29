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
![Streamlit](https://img.shields.io/badge/Streamlit-dashboard-FF4B4B?logo=streamlit&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-interactive-3F4F75?logo=plotly&logoColor=white)
![matplotlib](https://img.shields.io/badge/matplotlib-figures-11557c)

*Statistical analysis / BI, ML as a complement, dashboard*

---

## Framing

Question: sensitivity of Walloon yields to **recent** climate variability
(2000–2024). Primary approach: statistics / BI. NUTS 2 map and a linear
baseline as complements. No CMIP6 in the observed table.

---

## Method

1. Join Eurostat `apro_cpshr` × ERA5 (Open-Meteo), territory × year.
2. OLS **detrend** year → t/ha, per crop × territory.
3. Spearman of the **residual** vs season z-scores (Pearson as a check).
4. Atypical year: residual z ≤ −1 **and** climate |z| ≥ 1.
5. OLS: residual ~ temp + rain + ET0; **leave-one-year-out** vs naive (0).
6. Dashboard: filters; Spearman ranking is **not** recomputed on the slider.

---

## Stack — why

- **pandas**: tables, join, Parquet export.
- **scipy.stats**: `linregress`, `spearmanr` (robust to extremes, small n).
- **scikit-learn**: `LinearRegression` — no forest (n = 14–25).
- **matplotlib**: README figures and the static choropleth.
- **Streamlit + Plotly**: exploration; same GISCO GeoJSON as the report.

---

## Metrics

- **Spearman**: main indicator (ranks). Read p < 0.05; no multiplicity
  correction.
- **Leave-one-year-out MAE** vs naive (predict 0), in t/ha. A negative
  LOO R² is informative, not a scoring failure.
- Provinces are a **sign** check only, never pooled.

---

## Results (Wallonia)

- Wheat × seasonal rainfall: ρ ≈ **−0.68** (p < 0.05); same sign in all
  five provinces. Naive MAE 0.51 → LOO **0.38** t/ha (R² ≈ 0.40).
- Potato: heat, ρ ≈ −0.46; univariate temperature beats the 3-variable
  model (ET0 collinearity).
- 2024 (wet): six crops flagged. Other crops: climate often does not beat
  “stay on trend”.

---

## Limits

- Correlation ≠ causation; one ERA5 point per provincial centroid.
- One April–September calendar; n = 14–25.
- No cloud deploy; no CMIP6 / SSP scenario.

---

## Code

- Analysis: `src/agri_climat/analyse.py` — `python -m agri_climat analyse`
- ML: `src/agri_climat/ml.py` — `python -m agri_climat ml`
- Map: `src/agri_climat/map.py` — `python -m agri_climat map`
- App: `webapp/app.py` — `python -m agri_climat dashboard`

Pipeline: `python -m agri_climat run` (does not start Streamlit).
