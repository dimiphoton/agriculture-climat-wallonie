# Journal de développement

## 2026-08-25 — Feature 3 : analyse statistique

- Sensibilité par culture (Spearman sur résidu de rendement vs climat de
  saison), années atypiques, zoom froment ; rapport `docs/analyse.md`.
- Garde-fou : corrélation ≠ causalité ; provinces en contrôle de signe.

## 2026-08-25 — Feature 2 : jointure et EDA

- Table `rendements_climat` (CSV + Parquet), anomalies climatiques par
  territoire, rapport `docs/eda.md`.
- Aperçu reproductible : `python -m agri_climat eda` (terminal + PNG),
  sans `plt.show()` qui bloquait sous Windows.

## 2026-08-25 — Feature 1 : acquisition et nettoyage

- Pipeline CLI (`python -m agri_climat run`) : rendements Eurostat
  (`apro_cpshr`, Wallonie + provinces) et climat Open-Meteo / ERA5.
- Tables nettoyées dans `data/processed/` ; productions wallonnes aberrantes
  (ex. froment 2011) imputées par somme des provinces.
- Package `agri_climat` à la place du template `mon_projet`.

## AAAA-MM-JJ — Initialisation du projet

- Repo créé à partir du template portfolio.
