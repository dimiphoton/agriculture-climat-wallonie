---
marp: true
theme: default
paginate: true
---

# Rendements wallons × climat — technique

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![pandas](https://img.shields.io/badge/pandas-2.x-150458?logo=pandas&logoColor=white)
![scipy](https://img.shields.io/badge/scipy-stats-8CAAE6?logo=scipy&logoColor=white)

*Feature 3 : analyse statistique*

---

## Cadrage

Question : sensibilité des rendements wallons aux variations climatiques
**récentes**. Approche dominante : statistique / BI. Carte et ML basique
ensuite. Pas de scénario CMIP6 dans le jeu observé.

---

## Méthodologie

1. Rendement Eurostat (t/ha), climat ERA5 saison avril–septembre.
2. **Détrend** OLS année → t/ha, par culture × territoire.
3. Spearman (principal) et Pearson du **résidu** vs z-scores de saison.
4. Classement = |ρ| max par culture, Wallonie ; provinces = contrôle de signe.
5. Année atypique : résidu z ≤ −1 **et** |z| climatique ≥ 1.
6. Zoom : froment et épeautre.

---

## Stack

- **pandas** : tables, jointure.
- **scipy.stats** : `linregress`, `spearmanr`, `pearsonr`.
- **matplotlib** : heatmap et série froment (backend Agg, pas de `plt.show`).

Code : `src/agri_climat/analyse.py` — `python -m agri_climat analyse`

---

## Limites

- Corrélation ≠ causalité ; pas de correction pour tests multiples.
- Un point ERA5 par province ; calendrier cultural unique.
- n petit (14 ans pour maïs grain / orge d’hiver).
- Pas de CMIP6 / SSP (Feature 9, après un modèle — Feature 6).
