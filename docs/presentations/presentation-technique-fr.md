---
marp: true
theme: default
paginate: true
---

# Rendements wallons × climat — technique

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![pandas](https://img.shields.io/badge/pandas-2.x-150458?logo=pandas&logoColor=white)
![requests](https://img.shields.io/badge/requests-HTTP-2b5b84)

*Feature 1 : acquisition et nettoyage*

---

## Cadrage

Question : sensibilité des rendements wallons aux variations climatiques
récentes. Approche dominante : analyse statistique / BI. Carte et ML basique
en complément, pas en objectif principal.

---

## Méthodologie (étape 1)

1. Eurostat `apro_cpshr` : superficie et production, NUTS 1 (BE3) et NUTS 2.
2. Rendement = production / superficie (t/ha).
3. Si le NUTS 1 est aberrant (bornes agronomiques), somme des provinces.
4. Open-Meteo Archive (ERA5) : 5 centroïdes provinciaux, agrégation
   mensuelle / annuelle / saison avril–septembre.

---

## Stack

- **pandas** : TSV Eurostat, JSON Open-Meteo, agrégations.
- **requests** + **truststore** : téléchargement reproductible (TLS via certificats OS).
- Pas de CDS / NetCDF à ce stade : séries temporelles seulement.

Code : `src/agri_climat/data/` — `python -m agri_climat run`

---

## Qualité des données

- Flags Eurostat (`:`, `e`, `p`) → valeurs manquantes.
- Rupture d’unité documentée (froment wallon 2011) corrigée et flaggée
  (`imputed=True`).
- Granularité : région / province, pas la parcelle.

---

## Limites (à ce stade)

Pas encore de jointure rendements × climat, ni de corrélation. La moyenne
simple des 5 points climatiques n’est pas pondérée par la SAU. Causalité
hors scope : corrélation seulement, plus tard.
