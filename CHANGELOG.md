# Changelog

## [Non publié]

### Feature 7 — Dashboard interactif

- App Streamlit (`webapp/app.py`) : filtres culture / période, séries
  Plotly, classement Spearman, années atypiques, choroplèthe NUTS 2
  (GeoJSON déjà produit en Feature 5).
- `python -m agri_climat dashboard` (pas inclus dans `run` : ça lance un
  serveur). Logique dans `src/agri_climat/dashboard.py`.

### Feature 6 — ML basique

- Régression linéaire (scikit-learn) : résidu de rendement ~ z-scores de
  saison, Wallonie, leave-one-year-out vs baseline naïve (prédire 0).
- Rapport `docs/ml.md`, CSV `ml_metrics.csv`, PNG froment
  (`pictures/experiments/`) et ratio MAE README
  (`pictures/readme/ml-mae-vs-naive.png`). `python -m agri_climat ml`
  (inclus dans `run`).
- Froment : MAE 0,51 → 0,38 t/ha (R² LOO ≈ 0,40) ; pour la plupart des
  autres cultures le modèle à 3 variables ne bat pas la naïve.

### Feature 5 — Carte de synthèse

- Choroplèthe provinciale (NUTS 2) : Spearman froment × pluie de saison, et
  résidu de rendement 2024. PNG `pictures/readme/wheat-provinces-map.png`,
  GeoJSON `data/processed/nuts2_wallonie.geojson` (source Eurostat GISCO).
- `python -m agri_climat map` (inclus dans `run`). Pas de Folium / Plotly /
  GeoPandas : matplotlib + GeoJSON, déjà dans la stack.

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
