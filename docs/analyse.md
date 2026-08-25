# Analyse statistique — rendements × climat

Périmètre : **Wallonie (BE3)**, 2000–2024, saison avril–septembre. Le rendement est d'abord **détrendé** (droite année → t/ha par culture). On corréle ensuite le **résidu** aux z-scores climatiques de saison (température, pluie, ET0). Indicateur principal : **Spearman** (rangs, plus robuste aux extrêmes) ; Pearson en contrôle. Seuil de lecture : p < 0,05 — ce n'est pas une preuve de causalité.

Cultures classées : **8**. Maïs grain et orge d'hiver ont des séries plus courtes (~14 ans) : la puissance statistique est plus faible.

## Classement de sensibilité (Wallonie)

Pour chaque culture, la variable climatique au |Spearman| le plus élevé. Un |ρ| fort dit « les années hors tendance de rendement vont souvent de pair avec cette anomalie climatique » — pas « cette anomalie a causé la perte ».

| culture | n | variable climatique | spearman | p spearman | pearson | p pearson | p < 0.05 | tendance t/ha/an |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Froment et épeautre | 24 | précipitations saison | -0.683 | 0.0002 | -0.676 | 0.0003 | oui | -0.0069 |
| Pomme de terre | 25 | température saison | -0.459 | 0.0209 | -0.398 | 0.0486 | oui | -0.1776 |
| Maïs grain | 14 | précipitations saison | 0.446 | 0.1098 | 0.402 | 0.1541 | non | -0.0934 |
| Betterave sucrière | 25 | précipitations saison | -0.39 | 0.0539 | -0.289 | 0.1612 | non | 0.9483 |
| Colza | 25 | précipitations saison | -0.368 | 0.0705 | -0.51 | 0.0092 | non | 0.0036 |
| Orge | 25 | température saison | -0.286 | 0.1655 | -0.28 | 0.1752 | non | 0.0054 |
| Orge d'hiver | 14 | précipitations saison | -0.279 | 0.3338 | -0.304 | 0.2911 | non | -0.0728 |
| Maïs fourrager | 23 | précipitations saison | -0.198 | 0.366 | -0.204 | 0.3506 | non | -0.0485 |

## Corrélations détaillées

| culture | variable | n | tendance t/ha/an | spearman | p spearman | pearson | p pearson |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Froment et épeautre | température saison | 24 | -0.0069 | 0.221 | 0.2997 | 0.12 | 0.5759 |
| Froment et épeautre | précipitations saison | 24 | -0.0069 | -0.683 | 0.0002 | -0.676 | 0.0003 |
| Froment et épeautre | ET0 saison | 24 | -0.0069 | 0.463 | 0.0225 | 0.426 | 0.0378 |
| Orge | température saison | 25 | 0.0054 | -0.286 | 0.1655 | -0.28 | 0.1752 |
| Orge | précipitations saison | 25 | 0.0054 | -0.23 | 0.2687 | -0.351 | 0.0854 |
| Orge | ET0 saison | 25 | 0.0054 | -0.031 | 0.8839 | -0.033 | 0.8756 |
| Orge d'hiver | température saison | 14 | -0.0728 | -0.147 | 0.6154 | -0.189 | 0.5186 |
| Orge d'hiver | précipitations saison | 14 | -0.0728 | -0.279 | 0.3338 | -0.304 | 0.2911 |
| Orge d'hiver | ET0 saison | 14 | -0.0728 | 0.244 | 0.4006 | 0.23 | 0.4299 |
| Maïs grain | température saison | 14 | -0.0934 | -0.327 | 0.2531 | -0.335 | 0.2422 |
| Maïs grain | précipitations saison | 14 | -0.0934 | 0.446 | 0.1098 | 0.402 | 0.1541 |
| Maïs grain | ET0 saison | 14 | -0.0934 | -0.297 | 0.303 | -0.324 | 0.2579 |
| Maïs fourrager | température saison | 23 | -0.0485 | 0.162 | 0.4601 | 0.041 | 0.8539 |
| Maïs fourrager | précipitations saison | 23 | -0.0485 | -0.198 | 0.366 | -0.204 | 0.3506 |
| Maïs fourrager | ET0 saison | 23 | -0.0485 | 0.133 | 0.544 | 0.08 | 0.7167 |
| Colza | température saison | 25 | 0.0036 | 0.032 | 0.8781 | 0.098 | 0.6414 |
| Colza | précipitations saison | 25 | 0.0036 | -0.368 | 0.0705 | -0.51 | 0.0092 |
| Colza | ET0 saison | 25 | 0.0036 | 0.227 | 0.2753 | 0.187 | 0.3697 |
| Pomme de terre | température saison | 25 | -0.1776 | -0.459 | 0.0209 | -0.398 | 0.0486 |
| Pomme de terre | précipitations saison | 25 | -0.1776 | 0.278 | 0.179 | 0.231 | 0.2667 |
| Pomme de terre | ET0 saison | 25 | -0.1776 | -0.44 | 0.0277 | -0.332 | 0.1053 |
| Betterave sucrière | température saison | 25 | 0.9483 | -0.042 | 0.8409 | -0.051 | 0.8079 |
| Betterave sucrière | précipitations saison | 25 | 0.9483 | -0.39 | 0.0539 | -0.289 | 0.1612 |
| Betterave sucrière | ET0 saison | 25 | 0.9483 | 0.045 | 0.8323 | 0.058 | 0.7816 |

## Robustesse provinciale

Médiane du Spearman sur les cinq provinces, **sans pooler** les lignes (les provinces ne sont pas indépendantes). « Provinces même signe » : combien de provinces ont le même signe que la Wallonie.

| culture | variable | ρ Wallonie | ρ médiane provinces | provinces même signe |
| --- | --- | --- | --- | --- |
| Froment et épeautre | température saison | 0.221 | 0.191 | 5 |
| Froment et épeautre | précipitations saison | -0.683 | -0.597 | 5 |
| Froment et épeautre | ET0 saison | 0.463 | 0.446 | 5 |
| Orge | température saison | -0.286 | -0.279 | 5 |
| Orge | précipitations saison | -0.23 | -0.231 | 5 |
| Orge | ET0 saison | -0.031 | 0.003 | 2 |
| Orge d'hiver | température saison | -0.147 | -0.233 | 5 |
| Orge d'hiver | précipitations saison | -0.279 | -0.182 | 5 |
| Orge d'hiver | ET0 saison | 0.244 | 0.2 | 5 |
| Maïs grain | température saison | -0.327 | -0.478 | 5 |
| Maïs grain | précipitations saison | 0.446 | 0.363 | 5 |
| Maïs grain | ET0 saison | -0.297 | -0.222 | 5 |
| Maïs fourrager | température saison | 0.162 | -0.002 | 2 |
| Maïs fourrager | précipitations saison | -0.198 | -0.151 | 4 |
| Maïs fourrager | ET0 saison | 0.133 | 0.039 | 3 |
| Colza | température saison | 0.032 | 0.012 | 3 |
| Colza | précipitations saison | -0.368 | -0.359 | 5 |
| Colza | ET0 saison | 0.227 | 0.23 | 4 |
| Pomme de terre | température saison | -0.459 | -0.235 | 4 |
| Pomme de terre | précipitations saison | 0.278 | 0.106 | 4 |
| Pomme de terre | ET0 saison | -0.44 | -0.253 | 4 |
| Betterave sucrière | température saison | -0.042 | 0.038 | 1 |
| Betterave sucrière | précipitations saison | -0.39 | -0.376 | 5 |
| Betterave sucrière | ET0 saison | 0.045 | 0.182 | 4 |

## Années atypiques

Filtre : résidu de rendement z ≤ -1.0 **et** au moins un |z| climatique de saison ≥ 1.0. Une année très sèche sans baisse de rendement (hors tendance) n'apparaît pas ici, et inversement.

| année | culture | t/ha | résidu z | temp z | pluie z | ET0 z | aléa |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2000 | Colza | 3.022 | -2.068 | -0.706 | 1.575 | -1.246 | humide, ET0- |
| 2000 | Orge | 6.899 | -1.074 | -0.706 | 1.575 | -1.246 | humide, ET0- |
| 2001 | Betterave sucrière | 58.863 | -1.118 | -1.261 | 0.839 | -0.679 | froid |
| 2003 | Orge | 6.533 | -1.618 | 1.526 | -0.909 | 1.429 | chaud, ET0+ |
| 2018 | Maïs grain | 7.4 | -1.575 | 2.345 | -1.821 | 1.916 | chaud, sec, ET0+ |
| 2018 | Pomme de terre | 32.931 | -1.4 | 2.345 | -1.821 | 1.916 | chaud, sec, ET0+ |
| 2020 | Maïs grain | 7.417 | -1.308 | 1.351 | -1.4 | 2.107 | chaud, sec, ET0+ |
| 2021 | Colza | 3.406 | -1.264 | -1.824 | 1.677 | -0.945 | froid, humide |
| 2024 | Betterave sucrière | 77.801 | -1.506 | 0.096 | 2.32 | -0.598 | humide |
| 2024 | Colza | 3.353 | -1.431 | 0.096 | 2.32 | -0.598 | humide |
| 2024 | Froment et épeautre | 6.517 | -2.436 | 0.096 | 2.32 | -0.598 | humide |
| 2024 | Maïs fourrager | 41.545 | -1.073 | 0.096 | 2.32 | -0.598 | humide |
| 2024 | Orge | 6.224 | -2.219 | 0.096 | 2.32 | -0.598 | humide |
| 2024 | Orge d'hiver | 6.409 | -1.438 | 0.096 | 2.32 | -0.598 | humide |

Années avec au moins deux cultures flaggées : 2024 (6 cultures), 2018 (2 cultures), 2000 (2 cultures).

## Zoom : froment et épeautre

Culture retenue : **froment et épeautre** (série longue, culture phare wallonne). Le rendement observé est d'abord ramené à un résidu autour d'une tendance linéaire, pour ne pas attribuer au climat le progrès agronomique.

- Tendance wallonne : **-0.007 t/ha par an** (n = 24 années avec rendement).
- Liaison la plus forte (Spearman) : **précipitations saison** (ρ = -0.683, p = 0.0002).
- Pluie de saison : ρ = -0.683 (p = 0.0002). Lecture : « saison plus humide ↔ rendement sous la tendance ». Ce n'est pas une preuve de cause.
- Années atypiques froment (filtre joint rendement + climat) : **2024**.

Figures : `pictures/experiments/corr-spearman-wallonie.png` et `pictures/experiments/froment-detrend-climat.png`.

## Garde-fous (corrélation ≠ causalité)

- Un point ERA5 par centroïde provincial, Wallonie = moyenne non pondérée par la SAU : ce n'est pas le climat de la parcelle.
- Calendrier unique avril–septembre pour toutes les cultures (le maïs et le froment n'ont pas le même calendrier cultural).
- Tendance linéaire : approximation. Un saut méthodologique Eurostat ou un progrès non linéaire reste dans le résidu.
- Pas de contrôle d'autres facteurs (prix, maladies, irrigation, changement de variétés au-delà de la droite de tendance).
- Les p-values ne sont pas corrigées pour la multiplicité (plusieurs cultures × trois variables).
- Observation 2000–2024 seulement : pas de scénario CMIP6 / SSP.
