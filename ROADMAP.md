# Roadmap

Projet : rendements agricoles wallons × variabilité climatique.  
Domaine : analyse statistique / BI, avec carte de synthèse et ML basique en
complément.  
Livrables : rapport statique (README, figures) + dashboard interactif.

---

## Feature 1 — Acquisition et nettoyage des données

- [x] Téléchargement des rendements wallons via Eurostat `apro_cpshr`
      (Statbel → Eurostat ; Wallonie + provinces)
- [x] Téléchargement des séries climatiques ERA5 via Open-Meteo
      (5 points provinciaux, agrégat Wallonie)
- [x] Scripts `clean_rendements` et `clean_climat` dans `src/agri_climat/`
- [x] Jeux intermédiaires dans `data/processed/` (`rendements.csv`,
      `climat_mensuel.csv`, `climat_annuel.csv`)
- [x] CLI `python -m agri_climat run` pour reproduire le pipeline

## Feature 2 — Consolidation et exploration

- [ ] Jointure temporelle rendements × climat
- [ ] Table consolidée exportée (CSV/Parquet)
- [ ] EDA : distributions, valeurs manquantes, années/cultures couvertes
- [ ] Note sur les limites de comparabilité (méthodologie, granularité)

## Feature 3 — Analyse statistique

- [ ] Corrélations et tendances par culture
- [ ] Identification des cultures les plus sensibles et des années atypiques
- [ ] Au moins une culture traitée en profondeur (graphiques dédiés)
- [ ] Rédaction des conclusions avec garde-fous causalité

## Feature 4 — Visualisations statiques

- [ ] Graphiques comparatifs rendements vs anomalies climatiques
- [ ] Export des figures dans `figures/` (ou `pictures/readme/` pour le README)
- [ ] Mise à jour du README (objectif, méthode, résultats, limites)

## Feature 5 — Carte de synthèse

- [ ] Choix du niveau géographique réaliste (province, arrondissement, ou
      Wallonie selon les données)
- [ ] Carte choroplèthe ou équivalent (folium / plotly — à valider)
- [ ] Intégration au rapport statique et préparation pour le dashboard

## Feature 6 — ML basique (complément)

- [ ] Baseline simple (ex. régression linéaire rendement ~ variables climat)
- [ ] Métriques interprétables ; comparaison avec l'analyse statistique
- [ ] Limites documentées dans `docs/decisions.md`

## Feature 7 — Dashboard interactif

- [ ] App Streamlit (ou équivalent validé) : filtres culture / période
- [ ] Graphiques clés + lien vers carte si disponible
- [ ] Instructions de lancement dans le README

## Feature 8 — Portfolio

- [ ] Présentations Marp (4 fichiers FR/EN)
- [ ] CHANGELOG et entrée JOURNAL après merge des features majeures

---

**Ordre** : une feature à la fois, branche `feature/<nom>` par étape, validation
avant merge dans `main`.
