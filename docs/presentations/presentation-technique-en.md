---
marp: true
theme: default
paginate: true
---

# Walloon yields × climate — technical

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![pandas](https://img.shields.io/badge/pandas-2.x-150458?logo=pandas&logoColor=white)
![scipy](https://img.shields.io/badge/scipy-stats-8CAAE6?logo=scipy&logoColor=white)

*Feature 3: statistical analysis*

---

## Framing

Question: sensitivity of Walloon yields to **recent** climate variability.
Primary approach: statistics / BI. Map and a simple ML baseline come later.
No CMIP6 scenario in the observed table.

---

## Method

1. Eurostat yield (t/ha), ERA5 April–September season.
2. OLS **detrend** year → t/ha, per crop × territory.
3. Spearman (main) and Pearson of the **residual** vs season z-scores.
4. Ranking = max |ρ| per crop, Wallonia; provinces = sign check only.
5. Atypical year: residual z ≤ −1 **and** climate |z| ≥ 1.
6. Deep-dive: wheat and spelt.

---

## Stack

- **pandas**: tables, join.
- **scipy.stats**: `linregress`, `spearmanr`, `pearsonr`.
- **matplotlib**: heatmap and wheat series (Agg backend, no `plt.show`).

Code: `src/agri_climat/analyse.py` — `python -m agri_climat analyse`

---

## Limits

- Correlation ≠ causation; no multiple-testing correction.
- One ERA5 point per province; a single growing-season calendar.
- Small n (14 years for grain maize / winter barley).
- No CMIP6 / SSP (Feature 9, after a model — Feature 6).
