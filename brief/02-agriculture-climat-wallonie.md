# Rendements agricoles wallons face à la variabilité climatique

## Contexte et problématique

L'agriculture wallonne est directement exposée aux aléas climatiques : sécheresses, excès de pluie, vagues de chaleur. Les acteurs du secteur (coopératives agricoles, assureurs récolte, administration) ont besoin de comprendre quelles cultures et quelles périodes sont les plus vulnérables pour anticiper les risques.

Ce projet répond à la question :

> Quelles cultures wallonnes montrent la plus forte sensibilité aux variations climatiques récentes, et quelles années ont été les plus à risque ?

## Objectif

Croiser des données de rendements agricoles wallons avec des variables climatiques sur plusieurs années pour identifier des corrélations exploitables. L'accent est mis sur l'analyse statistique et la mise en récit — pas sur la cartographie ni le traitement d'image satellite.

## Compétences démontrées

- Nettoyage et harmonisation de données multi-sources (formats, granularité, unités différentes)
- Jointures temporelles entre séries climatiques et séries agricoles
- Analyse de corrélation et de tendance
- Visualisation comparative (cultures, années)
- Esprit critique sur la causalité (distinguer corrélation et cause)

## Sources de données

- **État de l'Agriculture Wallonne** ([etat-agriculture.wallonie.be](https://etat-agriculture.wallonie.be)) : rendements par culture (froment, betterave sucrière, pomme de terre...) et par année, données SPW ARNE / Statbel.
- **Copernicus Climate Data Store** ([cds.climate.copernicus.eu](https://cds.climate.copernicus.eu)) : température moyenne, cumul de précipitations, indices de sécheresse — utilisés comme séries temporelles simples agrégées à l'échelle de la Wallonie, sans traitement raster ni SIG.
- **Statbel** ([statbel.fgov.be](https://statbel.fgov.be), thème agriculture-pêche) : statistiques complémentaires (superficies, exploitations).

## Livrables attendus

1. Jeu de données consolidé (rendement × année × culture × variables climatiques).
2. Analyse statistique documentée : corrélations, cultures les plus sensibles, années atypiques.
3. Visualisations comparatives claires (évolution des rendements vs anomalies climatiques).
4. README structuré : problématique, méthode, résultats, limites, recommandation à destination d'un acteur du secteur (coopérative, assureur, administration).

## Structure de repo attendue

```
projet-agriculture-climat-wallonie/
├── README.md
├── data/
│   ├── raw/
│   └── processed/
├── src/
│   ├── clean_rendements.py
│   ├── clean_climat.py
│   └── analyse.py
├── notebooks/
└── figures/
```

## Critères de qualité (definition of done)

- Les sources sont clairement citées et les limites de comparabilité explicitées (ex. changement de méthodologie de mesure au fil des ans).
- Au moins une culture est analysée en profondeur avec un graphique dédié.
- Le ton du README évite les conclusions hâtives : "corrélation ne veut pas dire causalité" doit transparaître dans l'analyse.

## Pour aller plus loin (optionnel)

- Construire un indice composite simple de "risque climatique par culture".
- Comparer la Wallonie à une autre région européenne via Eurostat.
