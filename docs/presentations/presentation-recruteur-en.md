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

*Which crops, which years — plus a simple check*

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
  to sit below the yield trend — **2024** in particular. All five
  provinces share the same sign.
- **Potato**: link with seasonal heat.
- **2018** (hot and dry): grain maize and potato below trend.

---

## A simple check

Year by year (without looking at that year itself), does the season help
place the harvest gap? **For wheat, yes — mainly via rainfall.** For most
other crops, adding heat and evapotranspiration does not really improve the
diagnosis.

This is not a forecast, and not a cause.

---

## Where we are

A sensitivity ranking, at-risk years, a provincial map, and this linear
check. The interactive dashboard comes next.
