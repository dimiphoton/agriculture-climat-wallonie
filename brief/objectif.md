# Objectif du projet

- **But** : réconcilier en SQL des rendements agricoles wallons (grain
  annuel × culture) et un climat journalier (grain jour × zone), puis
  identifier les cultures et les années les plus sensibles — rapport
  statique et dashboard interactif.
- **Origine** : brief portfolio (`brief/02-agriculture-climat-wallonie.md`),
  cas d'usage inspiré des besoins d'acteurs du secteur (coopératives,
  assureurs récolte, administration).
- **Contraintes de départ** : le brief impose DuckDB, un schéma à grains
  hétérogènes, des vues SQL de réconciliation (pas un `pd.merge` amont)
  et un fichier `queries.sql`. Sources : État de l'Agriculture Wallonne
  / Statbel via Eurostat, Copernicus ERA5 via Open-Meteo.

## Question centrale

> Quelles cultures wallonnes montrent la plus forte sensibilité aux
> variations climatiques récentes, et quelles années ont été les plus à
> risque — une fois les données climatiques et agricoles correctement
> recalées l'une sur l'autre ?

## Domaine et approche

- **Dominant** : modélisation relationnelle multi-source (schéma DuckDB,
  agrégation journalier → annuel en SQL, jointures / CTE / fenêtres).
- **Compléments validés** :
  - analyse statistique sur les **résultats** de ces requêtes
    (corrélations, années atypiques, esprit critique sur la causalité) ;
  - une **carte** pour contextualiser géographiquement les résultats ;
  - un **ML basique** en complément (baseline simple, pas l'objectif
    principal) ;
  - un **dashboard** Streamlit / pages Plotly.
- **Hors scope initial** : traitement raster / imagerie satellite, modèle
  prédictif complexe ou déploiement production.

## Livrables finaux

1. Scripts d'import des données brutes dans leur granularité native.
2. Base DuckDB (`sql/schema.sql`) : faits à grains différents, vues de
   réconciliation, indice de risque en vue dédiée.
3. `sql/queries.sql` : croisement, CTE, fenêtrage, Spearman via rangs.
4. Analyse statistique documentée (corrélations, cultures sensibles,
   années atypiques, limites).
5. Visualisations comparatives et carte(s) de synthèse.
6. **Rapport statique** : README (justification du schéma), figures,
   recommandation pour un acteur du secteur.
7. **Dashboard interactif** : exploration des séries (complément au brief).

## Definition of done (rappel brief)

- Schéma justifié (pourquoi ces grains, pourquoi une vue).
- Chaque requête SQL de réconciliation commentée.
- Sources citées ; ruptures de méthodologie explicites ; causalité
  gardée (corrélation ≠ cause).
- Au moins une culture analysée en profondeur avec graphique dédié.

Ce fichier capture le but brut. Les versions polies destinées au
portfolio vivent dans `README.md` et `docs/`.
