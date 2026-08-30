# Journal de développement

## 2026-08-30 — Photos 16:9 sous docs/pictures

- Fonds Marp (froment, collines, pluie, maïs) servis par GitHub Pages.
- Graphes de slides copiés dans `docs/pictures/presentations/`.

## 2026-08-30 — Brief SQL / DuckDB

- Schéma à grains hétérogènes (`sql/schema.sql`) : climat quotidien en
  fait, annuel en vue ; jointure et z-scores en SQL. `queries.sql` pour
  les questions métier (CTE, fenêtres, Spearman via rangs, indice de
  risque). `python -m agri_climat join` / `sql`.

## 2026-08-30 — Slides impact (thème agri)

- Quatre decks réécrits en fil de questions : photos plein cadre, thème
  `agri`, graphes sans titre matplotlib. Explorer Plotly sur GitHub Pages
  (`docs/explore-{fr,en}.html`). `python -m agri_climat slides`.

## 2026-08-29 — Feature 8 : portfolio

- Quatre decks Marp en état final (recruteur + technique, FR/EN) : visuel
  de ranking côté non spécialiste ; méthode, stack, métriques et liens
  `src/` côté technique.

## 2026-08-29 — Feature 7 : dashboard interactif

- Streamlit + Plotly : filtres culture / période, séries, classement,
  années atypiques, carte NUTS 2 ; `python -m agri_climat dashboard`.
- Classement Spearman = série entière (le slider ne le recalcule pas).

## 2026-08-29 — Feature 6 : ML basique

- Régression linéaire leave-one-year-out (résidu ~ z-scores de saison)
  vs naïve (prédire 0) ; `python -m agri_climat ml`.
- Froment : MAE 0,51 → 0,38 t/ha ; les autres cultures ne battent en
  général pas la naïve (n petit, collinéarité ET0 / température).

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
