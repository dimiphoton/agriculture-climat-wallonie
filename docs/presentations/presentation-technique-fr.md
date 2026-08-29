---
marp: true
theme: default
paginate: true
footer: '[Explorer les données](../explore-fr.html)'
---

# Le climat explique-t-il
# les écarts de rendement ?

Wallonie · 2000–2024 · statistique d’abord, ML ensuite

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.x-F7931E?logo=scikitlearn&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-dashboard-FF4B4B?logo=streamlit&logoColor=white)

---

## Le progrès agronomique n’explique-t-il pas tout ?

On retire d’abord une tendance année → t/ha. Ce qu’on relie au climat,
c’est **l’écart**.

![w:880](../../pictures/presentations/detrend-fr.png)

---

## Quel signal tient vraiment ?

Spearman sur le résidu (rangs, n petit). **Froment × pluie**, ρ ≈ −0,68.

![w:900](../../pictures/presentations/ranking-fr.png)

---

## On a gonflé n avec les provinces ?

Non. Les provinces ne sont pas indépendantes. Contrôle : **même signe**
partout, sans pooling.

![w:640](../../pictures/presentations/map-fr.png)

---

## Pourquoi pas un XGBoost ?

n = 14–25. Une droite + **leave-one-year-out**. Pour le froment, le climat
bat « rester sur la tendance » (MAE 0,51 → 0,38 t/ha). Ailleurs, souvent non.

![w:620](../../pictures/presentations/mae-fr.png)

---

## Où ça casse ?

Un point ERA5 par province. Calendrier unique avril–septembre.
Corrélation ≠ cause. Pas de scénario CMIP6.

---

## Comment je reproduis ?

**[Explorer en ligne](../explore-fr.html)** (même lien en pied de slide).

```
python -m agri_climat run
python -m agri_climat dashboard
```

`analyse.py` · `ml.py` · `map.py` · `webapp/app.py`
