---
marp: true
theme: default
paginate: true
---

# Rendements wallons × climat — technique

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![pandas](https://img.shields.io/badge/pandas-2.x-150458?logo=pandas&logoColor=white)
![requests](https://img.shields.io/badge/requests-HTTP-2b5b84)

*Feature 2 : jointure, anomalies, EDA*

---

## Cadrage

Question : sensibilité des rendements wallons aux variations climatiques
**récentes**. Approche dominante : analyse statistique / BI. Carte et ML
basique en complément. Pas de scénario climatique dans le jeu observé.

---

## Méthodologie

1. Eurostat `apro_cpshr` : rendement = production / superficie (t/ha).
2. ERA5 via Open-Meteo : 5 centroïdes, saison avril–septembre.
3. Jointure interne sur `geo` + `year` (2000–2024).
4. Anomalie et z-score **par territoire** vs moyenne 2000–2024.
5. Export CSV + Parquet ; EDA dans `docs/eda.md`.

---

## Stack

- **pandas** : TSV, JSON, jointure, agrégations.
- **pyarrow** : Parquet (types préservés).
- **matplotlib** : notebook d’exploration seulement (figures portfolio = F4).
- **requests** + **truststore** : téléchargements.

Code : `src/agri_climat/data/join.py` — `python -m agri_climat run`

---

## Qualité / EDA

- Couverture culture × territoire, manquants, bornes de rendements.
- Flag `imputed` conservé après jointure (corrections BE3).
- Granularité : région / province, pas la parcelle.

---

## Limites

- Un point climat par province, Wallonie = moyenne non pondérée par la SAU.
- Calendrier cultural unique (avril–septembre).
- **Pas de CMIP6 / SSP** ici : autre question (futur), après un modèle
  statistique (Feature 6 → Feature 9 optionnelle).
- Corrélation ≠ causalité (Feature 3).
