# Journal de développement

## 2026-08-29 — Feature 5 : carte de synthèse

- Choroplèthe NUTS 2 (matplotlib + GeoJSON GISCO) : Spearman froment ×
  pluie, et résidu 2024 ; `python -m agri_climat map`.
- Folium / Plotly reportés au dashboard ; GeoJSON réutilisable dans
  `data/processed/nuts2_wallonie.geojson`.

## 2026-08-29 — Feature 4 : visualisations statiques

- Trois PNG README (`pictures/readme/`) : ranking de sensibilité, nuages
  résidu × climat, années à risque ; `python -m agri_climat figures`.
- README public : Method / Results / Limits et takeaway métier.

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
