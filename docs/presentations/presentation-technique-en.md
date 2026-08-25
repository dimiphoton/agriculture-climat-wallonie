---
marp: true
theme: default
paginate: true
---

# Walloon yields × climate — technical

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![pandas](https://img.shields.io/badge/pandas-2.x-150458?logo=pandas&logoColor=white)
![requests](https://img.shields.io/badge/requests-HTTP-2b5b84)

*Feature 2: join, anomalies, EDA*

---

## Framing

Question: sensitivity of Walloon crop yields to **recent** climate
variability. Primary approach: statistical analysis / BI. Map and a simple
ML baseline come later. No climate-model scenario in the observed table.

---

## Method

1. Eurostat `apro_cpshr`: yield = production / area (t/ha).
2. ERA5 via Open-Meteo: five centroids, April–September season.
3. Inner join on `geo` + `year` (2000–2024).
4. Anomaly and z-score **per territory** vs the 2000–2024 mean.
5. CSV + Parquet export; EDA in `docs/eda.md`.

---

## Stack

- **pandas**: TSV, JSON, join, aggregations.
- **pyarrow**: Parquet (types preserved).
- **matplotlib**: exploration notebook only (portfolio figures = F4).
- **requests** + **truststore**: downloads.

Code: `src/agri_climat/data/join.py` — `python -m agri_climat run`

---

## Quality / EDA

- Coverage by crop × territory, missingness, yield ranges.
- `imputed` flag kept after the join (BE3 fixes).
- Granularity: region / province, not the plot.

---

## Limits

- One climate point per province; Wallonia = unweighted mean (not UAA).
- Single growing-season calendar (April–September).
- **No CMIP6 / SSP** here: different question (the future), after a
  statistical model (Feature 6 → optional Feature 9).
- Correlation ≠ causation (Feature 3).
