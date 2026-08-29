# Changelog

## [Non publié]

### Feature 4 — Visualisations statiques

- Trois PNG polies dans `pictures/readme/` (ranking de sensibilité, nuages
  résidu × climat, années à risque) générées par
  `python -m agri_climat figures` (inclus dans `run`).
- README public : sections Method / Results / Limits, figures embarquées,
  takeaway métier. Libellés anglais (le README l'est) ; les PNG
  d'analyse restent en français dans `pictures/experiments/`.

### Feature 3 — Analyse statistique

- Corrélations (Spearman + Pearson) entre **résidu** de rendement (tendance
  linéaire ôtée) et z-scores climatiques de saison, par culture, Wallonie.
- Classement de sensibilité, années atypiques (filtre rendement + climat),
  zoom froment ; robustesse = signe du Spearman dans les provinces (sans pool).
- Rapport `docs/analyse.md`, PNG dans `pictures/experiments/`,
  `python -m agri_climat analyse`. Dépendance : `scipy`.

### Feature 2 — Jointure et EDA

- Table consolidée `rendements_climat` (CSV + Parquet) : jointure interne
  `geo` × `year`, anomalies et z-scores climatiques par territoire
  (référence 2000–2024).
- Rapport `docs/eda.md` généré par le CLI ; notebook
  `notebooks/02-eda-jointure.ipynb`.
- `python -m agri_climat join` (inclus dans `run`) ; `python -m agri_climat eda`
  pour l'aperçu terminal + PNG (évite le blocage `plt.show()` / Tk).
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
