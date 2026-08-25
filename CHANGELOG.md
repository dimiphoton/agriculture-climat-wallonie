# Changelog

## [Non publié]

### Feature 2 — Jointure et EDA

- Table consolidée `rendements_climat` (CSV + Parquet) : jointure interne
  `geo` × `year`, anomalies et z-scores climatiques par territoire
  (référence 2000–2024).
- Rapport `docs/eda.md` généré par le CLI ; notebook
  `notebooks/02-eda-jointure.ipynb`.
- `python -m agri_climat join` (inclus dans `run`).
- Scénarios CMIP6 / SSP volontairement exclus de cette table (décision
  documentée ; Feature 9 optionnelle après le ML).

### Feature 1 — Acquisition et nettoyage

- Pipeline CLI (`python -m agri_climat run`) : téléchargement Eurostat
  (rendements NUTS 1–2 wallons) et Open-Meteo / ERA5 (climat quotidien),
  puis tables nettoyées dans `data/processed/`.
- Correction des productions wallonnes aberrantes (ex. froment 2011) par
  somme des provinces lorsque le rendement officiel sort des bornes.
- Package renommé `agri_climat` (l'ancien `mon_projet` du template est retiré).
- `truststore` pour le TLS via les certificats système (Windows / proxy).

### Initialisation

- Projet créé à partir du template portfolio.
