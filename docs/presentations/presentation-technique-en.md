---
marp: true
theme: default
paginate: true
footer: '[Explore the data](../explore-en.html)'
---

# Does climate explain
# yield gaps?

Wallonia · 2000–2024 · statistics first, then a linear check

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.x-F7931E?logo=scikitlearn&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-dashboard-FF4B4B?logo=streamlit&logoColor=white)

---

## Isn’t this just genetic progress?

We first remove a year → t/ha trend. What we link to climate is the **gap**.

![w:880](../../pictures/presentations/detrend-en.png)

---

## Which signal actually holds?

Spearman on the residual (ranks, small n). **Wheat × rain**, ρ ≈ −0.68.

![w:900](../../pictures/presentations/ranking-en.png)

---

## Did you pool provinces to inflate n?

No. Provinces are not independent draws. Check: **same sign**
everywhere, no pooling.

![w:640](../../pictures/presentations/map-en.png)

---

## Why not XGBoost?

n = 14–25. A line + **leave-one-year-out**. For wheat, climate beats
“stay on trend” (MAE 0.51 → 0.38 t/ha). For most other crops, it does not.

![w:620](../../pictures/presentations/mae-en.png)

---

## Where does it break?

One ERA5 point per province. One April–September calendar.
Correlation ≠ cause. No CMIP6 scenario.

---

## How do I reproduce?

**[Explore online](../explore-en.html)** (same link in the slide footer).

```
python -m agri_climat run
python -m agri_climat dashboard
```

`analyse.py` · `ml.py` · `map.py` · `webapp/app.py`
