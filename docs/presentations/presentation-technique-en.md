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

*Feature 7: interactive dashboard*

---

## Framing

Question: sensitivity of Walloon yields to **recent** climate variability.
Primary approach: statistics / BI. ML is a simple baseline. The dashboard
explores existing results; it is not a new analysis.

---

## Method

1. Detrend, Spearman, atypical years, NUTS 2 map, LOO OLS (features 3–6).
2. Dashboard: crop / period filters; Plotly series and map.
3. Spearman ranking is **not** recomputed on the year slider (full series).
4. Same GISCO GeoJSON as the static report.

---

## Stack

- **Streamlit**: `webapp/app.py` (UI); `src/agri_climat/dashboard.py` (logic).
- **Plotly**: series and `go.Choropleth` (no Folium).
- Reuses `analyse`, `map.load_nuts_geojson`, `evaluate_all_crops`.

`python -m agri_climat dashboard` — **not** in `run`.

---

## Result (unchanged)

- Wheat: rainfall, ρ ≈ −0.68; LOO MAE 0.38 vs naive 0.51 t/ha.
- Other crops: climate often does not beat “stay on trend”.

---

## Limits

- Correlation ≠ causation; n = 14–25; provinces not pooled.
- No cloud deploy; no CMIP6 / SSP (optional Feature 9).
