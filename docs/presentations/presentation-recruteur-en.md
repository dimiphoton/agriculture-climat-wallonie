---
marp: true
theme: default
paginate: true
---

# Walloon crop yields and climate

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![pandas](https://img.shields.io/badge/pandas-2.x-150458?logo=pandas&logoColor=white)
![scipy](https://img.shields.io/badge/scipy-stats-8CAAE6?logo=scipy&logoColor=white)

*Feature 3: which crops, which years*

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

- **Wheat**: strongest link with seasonal rainfall (ρ ≈ −0.68). Wetter
  seasons tend to sit below the yield trend — **2024** in particular.
  All five provinces share the same sign.
- **Potato**: link with seasonal heat (ρ ≈ −0.46).
- **2018** (hot and dry): grain maize and potato below trend.

These are **correlations**, not causes: one weather point per province,
not the climate of the field.

---

## Where we are

A sensitivity ranking by crop, a list of atypical years, and a wheat
deep-dive. Polished charts and the dashboard come next.
