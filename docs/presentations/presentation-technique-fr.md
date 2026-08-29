---
marp: true
theme: default
paginate: true
---

# Rendements wallons × climat — technique

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![pandas](https://img.shields.io/badge/pandas-2.x-150458?logo=pandas&logoColor=white)
![scipy](https://img.shields.io/badge/scipy-stats-8CAAE6?logo=scipy&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.x-F7931E?logo=scikitlearn&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-dashboard-FF4B4B?logo=streamlit&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-interactive-3F4F75?logo=plotly&logoColor=white)

*Feature 7 : dashboard interactif*

---

## Cadrage

Question : sensibilité des rendements wallons aux variations climatiques
**récentes**. Approche dominante : statistique / BI. ML = baseline simple.
Dashboard = exploration, pas une nouvelle analyse.

---

## Méthodologie

1. Détrend, Spearman, années atypiques, carte NUTS 2, OLS LOO (features 3–6).
2. Dashboard : filtres culture / période ; séries et carte Plotly.
3. Classement Spearman **non recalculé** sur le slider (série entière).
4. Même GeoJSON GISCO que le rapport statique.

---

## Stack

- **Streamlit** : `webapp/app.py` (UI) ; `src/agri_climat/dashboard.py` (logique).
- **Plotly** : séries et `go.Choropleth` (pas Folium).
- Réutilise `analyse`, `map.load_nuts_geojson`, `evaluate_all_crops`.

`python -m agri_climat dashboard` — **pas** dans `run`.

---

## Résultat (inchangé)

- Froment : pluie, ρ ≈ −0,68 ; MAE LOO 0,38 vs naïve 0,51 t/ha.
- Autres cultures : le climat ne bat souvent pas « rester sur la tendance ».

---

## Limites

- Corrélation ≠ causalité ; n = 14–25 ; pas de pooling provincial.
- Pas de déploiement cloud ; pas de CMIP6 / SSP (Feature 9 optionnelle).
