# Rendements agricoles wallons face à la variabilité climatique

**Orientation technique :** l'intégration de sources hétérogènes comme cœur du projet — une base relationnelle qui réconcilie des granularités temporelles et géographiques différentes (climat journalier, rendements annuels), avec des requêtes SQL qui font le travail de croisement. Distinct de PEB (sophistication des requêtes sur un schéma déjà homogène) et d'Épidémio bayésienne (rigueur statistique sur l'incertitude) : ici, la difficulté est la modélisation d'intégration, pas l'analyse en aval.

## Contexte et problématique

L'agriculture wallonne est directement exposée aux aléas climatiques : sécheresses, excès de pluie, vagues de chaleur. Les acteurs du secteur (coopératives agricoles, assureurs récolte, administration) ont besoin de comprendre quelles cultures et quelles périodes sont les plus vulnérables pour anticiper les risques. Mais les données disponibles ne s'emboîtent pas naturellement : les rendements agricoles sont rapportés annuellement par culture, le climat est mesuré au jour le jour sur une grille géographique qui ne correspond à aucune découpe administrative. Réconcilier ça proprement est un problème de modélisation relationnelle avant d'être un problème statistique.

Ce projet répond à la question :

> Quelles cultures wallonnes montrent la plus forte sensibilité aux variations climatiques récentes, et quelles années ont été les plus à risque — une fois les données climatiques et agricoles correctement recalées l'une sur l'autre ?

## Objectif

Construire une base de données relationnelle qui intègre des rendements agricoles wallons (annuels, par culture) et des variables climatiques (journalières, par zone) aux granularités incompatibles, en résolvant cette réconciliation par des requêtes SQL plutôt que par des fusions pandas en amont — puis exploiter cette base pour identifier des relations exploitables entre climat et rendements.

## Compétences démontrées

- Modélisation relationnelle multi-source (schéma accueillant des granularités temporelles et géographiques différentes)
- Résolution de granularités hétérogènes en SQL (agrégation de séries journalières à l'échelle annuelle, alignement géographique)
- Requêtes de croisement complexes (jointures multi-tables, CTE, fonctions de fenêtrage pour les tendances pluriannuelles)
- Détection et traitement des anomalies de données (ruptures de méthodologie, valeurs manquantes)
- Analyse de corrélation et de tendance sur les résultats de ces requêtes
- Esprit critique sur la causalité (distinguer corrélation et cause)

## Sources de données

- **État de l'Agriculture Wallonne** ([etat-agriculture.wallonie.be](https://etat-agriculture.wallonie.be)) : rendements par culture (froment, betterave sucrière, pomme de terre...) et par année, données SPW ARNE / Statbel — granularité annuelle.
- **Copernicus Climate Data Store** ([cds.climate.copernicus.eu](https://cds.climate.copernicus.eu)) : température moyenne, cumul de précipitations, indices de sécheresse — granularité journalière, à agréger en SQL vers l'échelle annuelle utilisée par les rendements.
- **Statbel** ([statbel.fgov.be](https://statbel.fgov.be), thème agriculture-pêche) : statistiques complémentaires (superficies, exploitations).

## Approche et choix techniques

- **Moteur** : DuckDB, cohérent avec le reste du portfolio SQL analytique (PEB) — embarqué, reproductible en une commande, pas de serveur à gérer.
- **Schéma** : une table de dimension temporelle partagée (année), une table de faits "rendements" (grain annuel × culture), une table de faits "climat" (grain journalier, agrégée en vue SQL au grain annuel). La réconciliation de granularité est un artefact du schéma et des vues, pas une étape cachée dans un notebook.
- **Le travail d'intégration est le livrable** : contrairement à un simple `pd.merge`, la vue SQL qui agrège le climat journalier à l'année (avec le choix explicite des agrégats — moyenne, cumul, nombre de jours au-dessus d'un seuil) doit être documentée et justifiée.

## Livrables attendus

1. Scripts d'import des données brutes (rendements et climat) dans leur granularité native.
2. Base DuckDB avec schéma documenté : tables de faits à grains différents, vues SQL de réconciliation de granularité.
3. Un fichier `queries.sql` regroupant les requêtes de croisement (jointures, CTE, fenêtrage pour les tendances pluriannuelles par culture).
4. Analyse statistique sur les résultats de ces requêtes : corrélations, cultures les plus sensibles, années atypiques.
5. 2-3 graphiques comparatifs (évolution des rendements vs anomalies climatiques).
6. README structuré : problématique, choix de schéma et de granularité, méthode, résultats, limites, recommandation à destination d'un acteur du secteur.

## Structure de repo attendue

```
projet-agriculture-climat-wallonie/
├── README.md
├── data/
│   ├── raw/
│   └── processed/
├── sql/
│   ├── schema.sql
│   └── queries.sql
├── src/
│   ├── import_rendements.py
│   └── import_climat.py
├── notebooks/
└── figures/
```

## Règles strictes de professionnalisme

- Environnement figé et reproductible : base DuckDB régénérée par script à partir des données brutes, en une seule commande documentée.
- Chaque requête SQL de réconciliation ou de croisement commentée : ce qu'elle fait, pourquoi ce choix d'agrégation plutôt qu'un autre.
- Le schéma relationnel justifié dans le README (pourquoi ces grains, pourquoi une vue plutôt qu'une table matérialisée).
- Les ruptures de méthodologie entre années (changement de mesure, de source) explicitées, pas lissées silencieusement.
- Le ton du README évite les conclusions hâtives : "corrélation ne veut pas dire causalité" doit transparaître dans l'analyse, pas juste être énoncé.
- Environnement Python figé (`requirements.txt`).
- Commits atomiques avec messages conventionnels.

## Pour aller plus loin (optionnel)

- Construire un indice composite simple de "risque climatique par culture" via une vue SQL dédiée.
- Comparer la Wallonie à une autre région européenne via Eurostat, en étendant le même schéma plutôt qu'en dupliquant le pipeline.
