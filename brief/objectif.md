# Objectif du projet

- **But** : analyser la sensibilité des rendements agricoles wallons aux
  variations climatiques récentes — identifier les cultures et les années les
  plus à risque — et en restituer les résultats sous forme de rapport statique
  et de dashboard interactif.
- **Origine** : brief portfolio (`brief/02-agriculture-climat-wallonie.md`),
  cas d'usage inspiré des besoins d'acteurs du secteur (coopératives,
  assureurs récolte, administration).
- **Contraintes de départ** : aucune contrainte technique imposée ; sources
  de données identifiées dans le brief (État de l'Agriculture Wallonne,
  Copernicus CDS, Statbel).

## Question centrale

> Quelles cultures wallonnes montrent la plus forte sensibilité aux
> variations climatiques récentes, et quelles années ont été les plus à
> risque ?

## Domaine et approche

- **Dominant** : analyse statistique / BI (nettoyage multi-sources, jointures
  temporelles, corrélations, tendances, visualisations comparatives).
- **Compléments validés** :
  - une **carte** pour contextualiser géographiquement les résultats (dans
    la limite de la granularité disponible dans les sources) ;
  - un **ML basique** en complément (baseline simple, pas l'objectif
    principal) — avec esprit critique sur la causalité.
- **Hors scope initial** : traitement raster / imagerie satellite, modèle
  prédictif complexe ou déploiement production.

## Livrables finaux

1. Jeu de données consolidé (rendement × année × culture × variables
   climatiques).
2. Analyse statistique documentée (corrélations, cultures sensibles, années
   atypiques, limites de comparabilité).
3. Visualisations comparatives et, si les données le permettent, carte(s)
   de synthèse.
4. **Rapport statique** : README structuré, figures exportées, recommandation
   pour un acteur du secteur.
5. **Dashboard interactif** : exploration des séries, filtres culture/année,
   graphiques clés (outil à valider avant installation — Streamlit envisagé).

## Definition of done (rappel brief)

- Sources citées ; limites explicites (méthodologie, granularité, causalité).
- Au moins une culture analysée en profondeur avec graphique dédié.
- Ton analytique : corrélation ≠ causalité.

Ce fichier capture le but brut, tel qu'il a été formulé au départ. Les
versions polies destinées au portfolio vivent dans `README.md` et `docs/`.
