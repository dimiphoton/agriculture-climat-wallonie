---
marp: true
theme: default
paginate: true
---

# Walloon yields × climate — technical

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![pandas](https://img.shields.io/badge/pandas-2.x-150458?logo=pandas&logoColor=white)
![requests](https://img.shields.io/badge/requests-HTTP-2b5b84)

*Feature 1: data acquisition and cleaning*

---

## Framing

Question: sensitivity of Walloon crop yields to recent climate variability.
Primary approach: statistical analysis / BI. A map and a simple ML baseline
come later, as complements, not as the main goal.

---

## Method (step 1)

1. Eurostat `apro_cpshr`: area and production, NUTS 1 (BE3) and NUTS 2.
2. Yield = production / area (t/ha).
3. If NUTS 1 is implausible (agronomic bounds), sum the provinces.
4. Open-Meteo Archive (ERA5): five provincial centroids, aggregated to
   monthly / annual / April–September growing season.

---

## Stack

- **pandas**: Eurostat TSV, Open-Meteo JSON, aggregations.
- **requests** + **truststore**: reproducible downloads (OS certificate store).
- No CDS / NetCDF at this stage: time series only.

Code: `src/agri_climat/data/` — `python -m agri_climat run`

---

## Data quality

- Eurostat flags (`:`, `e`, `p`) → missing values.
- Documented unit break (Walloon wheat 2011) is corrected and flagged
  (`imputed=True`).
- Granularity: region / province, not the plot.

---

## Limits (so far)

No yield × climate join yet, and no correlation. The Wallonia climate series
is an unweighted mean of five points, not UAA-weighted. Causality is out of
scope: correlation only, later.
