# Roadmap

**Statut : v1.0 terminée (août 2026).** Features 1–8 livrées.
La Feature 9 (scénarios CMIP6 / SSP) reste volontairement hors périmètre
— ce n'est pas un oubli.

Projet : rendements agricoles wallons × variabilité climatique.  
Domaine : intégration SQL de sources à grains hétérogènes (DuckDB),
puis analyse statistique / BI, carte et ML basique en complément.  
Livrables : schéma + `queries.sql`, rapport statique (README, figures),
dashboard interactif.

---

## Feature 1 — Acquisition et nettoyage des données

- [x] Téléchargement des rendements wallons via Eurostat `apro_cpshr`
      (Statbel → Eurostat ; Wallonie + provinces)
- [x] Téléchargement des séries climatiques ERA5 via Open-Meteo
      (5 points provinciaux, grain **journalier** natif)
- [x] Scripts `clean_rendements` et `clean_climat` dans `src/agri_climat/`
- [x] Jeux natifs dans `data/processed/` (`rendements.csv`,
      `climat_quotidien.csv`)
- [x] CLI `python -m agri_climat run` pour reproduire le pipeline

## Feature 2 — Entrepôt DuckDB et exploration

- [x] Schéma relationnel (`sql/schema.sql`) : faits à grains différents,
      vues d'agrégation (moyenne / cumul / jours au-dessus d'un seuil),
      z-scores en fenêtre `PARTITION BY geo`, INNER JOIN `(geo, year)`
- [x] `sql/queries.sql` : CTE, fenêtrage (tendance, rangs), Spearman SQL,
      années atypiques, indice de risque
- [x] Table consolidée exportée des vues (`rendements_climat.csv` +
      `.parquet`) ; base `agri_climat.duckdb` régénérable
- [x] EDA : `docs/eda.md` généré + notebook `notebooks/02-eda-jointure.ipynb`
- [x] Note sur les limites de comparabilité (méthodologie, granularité, pas de CMIP6)

## Feature 3 — Analyse statistique

- [x] Corrélations et tendances par culture
- [x] Identification des cultures les plus sensibles et des années atypiques
- [x] Au moins une culture traitée en profondeur (graphiques dédiés)
- [x] Rédaction des conclusions avec garde-fous causalité

## Feature 4 — Visualisations statiques

- [x] Graphiques comparatifs rendements vs anomalies climatiques
- [x] Export des figures dans `pictures/readme/` (libellés anglais)
- [x] Mise à jour du README (objectif, méthode, résultats, limites)

## Feature 5 — Carte de synthèse

- [x] Choix du niveau géographique réaliste (province, arrondissement, ou
      Wallonie selon les données)
- [x] Carte choroplèthe ou équivalent (folium / plotly — à valider)
- [x] Intégration au rapport statique et préparation pour le dashboard

## Feature 6 — ML basique (complément)

- [x] Baseline simple (ex. régression linéaire rendement ~ variables climat)
- [x] Métriques interprétables ; comparaison avec l'analyse statistique
- [x] Limites documentées dans `docs/decisions.md`

## Feature 7 — Dashboard interactif

- [x] App Streamlit (ou équivalent validé) : filtres culture / période
- [x] Graphiques clés + lien vers carte si disponible
- [x] Instructions de lancement dans le README

## Feature 8 — Portfolio

- [x] Présentations Marp (4 fichiers FR/EN)
- [x] CHANGELOG et entrée JOURNAL après merge des features majeures

## Feature 9 — Scénarios climatiques (hors v1.0)

- [ ] **Hors v1.0** : pas de rendements futurs dans le jeu observé
- [ ] Si un repo ultérieur : API Climate Open-Meteo (CMIP6 / SSP), overlay
      séparé, jamais mélangé aux années observées 2000–2024
- [ ] Documenter l'incertitude modèle + downscaling (voir `docs/decisions.md`)

---

**Ordre** : une feature à la fois, branche `feature/<nom>` par étape, validation
avant merge dans `main`.
