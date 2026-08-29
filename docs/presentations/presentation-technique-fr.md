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
![matplotlib](https://img.shields.io/badge/matplotlib-figures-11557c)

*Analyse statistique / BI, ML en complément, dashboard*

---

## Cadrage

Question : sensibilité des rendements wallons aux variations climatiques
**récentes** (2000–2024). Dominant : statistique / BI. Carte NUTS 2 et
régression linéaire en complément. Pas de CMIP6 dans le jeu observé.

---

## Méthode

1. Jointure Eurostat `apro_cpshr` × ERA5 (Open-Meteo), `geo` × année.
2. **Détrend** OLS année → t/ha, par culture × territoire.
3. Spearman du **résidu** vs z-scores de saison (Pearson en contrôle).
4. Année atypique : résidu z ≤ −1 **et** |z| climatique ≥ 1.
5. OLS : résidu ~ temp + pluie + ET0 ; **leave-one-year-out** vs naïve (0).
6. Dashboard : filtres ; classement Spearman **non** recalculé au slider.

---

## Stack — pourquoi

- **pandas** : tables, jointure, export Parquet.
- **scipy.stats** : `linregress`, `spearmanr` (robuste aux extrêmes, n petit).
- **scikit-learn** : `LinearRegression` — pas de forêt (n = 14–25).
- **matplotlib** : figures README et choroplèthe statique.
- **Streamlit + Plotly** : exploration ; même GeoJSON GISCO que le rapport.

---

## Métriques

- **Spearman** : indicateur principal (rangs). Seuil de lecture p < 0,05,
  sans correction de multiplicité.
- **MAE leave-one-year-out** vs naïve (prédire 0), en t/ha. Le R² LOO
  peut être négatif : c’est informatif, pas un échec de « scoring ».
- Provinces = contrôle de **signe**, jamais poolées.

---

## Résultats (Wallonie)

- Froment × pluie de saison : ρ ≈ **−0,68** (p < 0,05) ; même signe dans
  les cinq provinces. MAE naïve 0,51 → LOO **0,38** t/ha (R² ≈ 0,40).
- Pomme de terre : chaleur, ρ ≈ −0,46 ; univariée température bat le
  modèle à 3 variables (collinéarité ET0).
- 2024 (humide) : six cultures flaggées. Autres cultures : le climat ne
  bat souvent pas « rester sur la tendance ».

---

## Limites

- Corrélation ≠ causalité ; un point ERA5 par centroïde provincial.
- Calendrier unique avril–septembre ; n = 14–25.
- Pas de déploiement cloud ; pas de scénario CMIP6 / SSP.

---

## Code

- Analyse : `src/agri_climat/analyse.py` — `python -m agri_climat analyse`
- ML : `src/agri_climat/ml.py` — `python -m agri_climat ml`
- Carte : `src/agri_climat/map.py` — `python -m agri_climat map`
- App : `webapp/app.py` — `python -m agri_climat dashboard`

Pipeline : `python -m agri_climat run` (sans le serveur Streamlit).
