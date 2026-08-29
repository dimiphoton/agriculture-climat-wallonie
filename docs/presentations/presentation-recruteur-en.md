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
![matplotlib](https://img.shields.io/badge/matplotlib-figures-11557c)

*Which crops, which years — report plus dashboard*

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

We first remove long-term yield progress, then check whether **gaps** move
with an unusual season. That is **not** proof that climate caused the loss.

---

## Finding (Wallonia)

- **Wheat**: strongest link with **rainfall**. Very wet seasons tend to sit
  below the trend — **2024** in particular.
- **Potato**: link with seasonal **heat**.
- **2018** (hot and dry): grain maize and potato below trend.

Watch wheat in very wet seasons; potato / grain maize in hot-dry summers.

---

## Visual takeaway

Bars show which crop tracks growing-season climate most closely. A star
means the link is statistically readable — not a cause.

![w:880](../../pictures/readme/crop-sensitivity-ranking.png)

---

## Deliverables

A static report (README + maps), a simple check (“does climate help place
the gap?”), and a **dashboard** to explore crop and period.

This is not a forecast, and not a 2050 scenario.
