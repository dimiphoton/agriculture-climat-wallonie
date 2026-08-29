---
marp: true
theme: default
paginate: true
---

# Walloon crop yields and climate

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![pandas](https://img.shields.io/badge/pandas-2.x-150458?logo=pandas&logoColor=white)
![scipy](https://img.shields.io/badge/scipy-stats-8CAAE6?logo=scipy&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.x-F7931E?logo=scikitlearn&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-dashboard-FF4B4B?logo=streamlit&logoColor=white)

*Which crops, which years — plus a dashboard to explore*

---

## The problem

Droughts, excess rain and heat waves hit Walloon harvests. Cooperatives,
insurers and public bodies need a clear picture: **which crops, which
years**.

---

## The data

Official yields by crop (Wallonia, 2000–2024) combined with growing-season
temperature, rainfall and evapotranspiration (April–September).

---

## What we measure

We first remove the long-term yield trend (agronomic progress), then check
whether **residuals** move with an unusual season. That is **not** proof
that climate caused the loss.

---

## First finding (Wallonia)

- **Wheat**: strongest link with seasonal rainfall. Wetter seasons tend
  to sit below the yield trend — **2024** in particular.
- **Potato**: link with seasonal heat.
- **2018** (hot and dry): grain maize and potato below trend.

---

## Explore

A dashboard lets you pick a crop and period, then see the series, at-risk
years and the provincial map. The sensitivity ranking stays the full-series
result — sliding the years does not rewrite the league table.

---

## Where we are

Static report, map, linear check, and dashboard. Future climate scenarios
stay out of scope.
