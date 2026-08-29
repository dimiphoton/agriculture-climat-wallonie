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

*Feature 6 : baseline linéaire (complément)*

---

## Cadrage

Question : sensibilité des rendements wallons aux variations climatiques
**récentes**. Approche dominante : statistique / BI. Carte NUTS 2
disponible. ML = baseline simple, pas l’objectif principal. Pas de
scénario CMIP6 dans le jeu observé.

---

## Méthodologie

1. Rendement Eurostat (t/ha), climat ERA5 saison avril–septembre.
2. **Détrend** OLS année → t/ha, par culture × territoire.
3. Spearman (principal) du **résidu** vs z-scores de saison.
4. Année atypique : résidu z ≤ −1 **et** |z| climatique ≥ 1.
5. Carte : Spearman froment × pluie, provinces.
6. OLS : résidu ~ temp + pluie + ET0 ; **leave-one-year-out** vs naïve (0).

---

## Stack

- **pandas** : tables, jointure.
- **scipy.stats** : `linregress`, `spearmanr`.
- **scikit-learn** : `LinearRegression` (pas de forêt : n trop petit).
- **matplotlib** : figures et choroplèthe (backend Agg).

Code : `src/agri_climat/ml.py` — `python -m agri_climat ml`

---

## Résultat ML vs statistique

- **Froment** : MAE naïve 0,51 → LOO 0,38 t/ha (R² ≈ 0,40). Meilleure
  univariée = pluie. Coefficient pluie négatif, cohérent avec ρ ≈ −0,68.
- **Pomme de terre** : univariée température bat le modèle à 3 variables
  (collinéarité ET0 / chaleur, VIF ET0 ≈ 4).
- Autres cultures : R² LOO souvent **négatif** — le climat n’améliore pas
  le diagnostic hors échantillon.

---

## Limites

- Corrélation ≠ causalité ; n = 14–25 ; pas de pooling provincial.
- LOO bruyant ; MAE en t/ha prioritaire sur le R².
- 2016 (froment) mal capté hors échantillon.
- Pas de CMIP6 / SSP (Feature 9 optionnelle, overlay séparé).
