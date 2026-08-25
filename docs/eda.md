# Exploration — table rendements × climat

Période observée : 2000–2024 (référence d'anomalie climatique = 2000–2024 par territoire).

- Lignes : **1068** (culture × geo × année).
- Cultures : 8 (Betterave sucrière, Colza, Froment et épeautre, Maïs fourrager, Maïs grain, Orge, Orge d'hiver, Pomme de terre).
- Territoires : BE3, BE31, BE32, BE33, BE34, BE35.
- Lignes de rendement imputées (BE3) : **3**.

## Couverture (nombre d'années)

| culture | BE3 | BE31 | BE32 | BE33 | BE34 | BE35 |
| --- | --- | --- | --- | --- | --- | --- |
| Betterave sucrière | 25 | 25 | 25 | 25 | 25 | 25 |
| Colza | 25 | 25 | 25 | 25 | 25 | 25 |
| Froment et épeautre | 25 | 25 | 25 | 25 | 25 | 25 |
| Maïs fourrager | 25 | 25 | 25 | 25 | 25 | 25 |
| Maïs grain | 14 | 14 | 14 | 14 | 14 | 14 |
| Orge | 25 | 25 | 25 | 25 | 25 | 25 |
| Orge d'hiver | 14 | 14 | 14 | 14 | 14 | 14 |
| Pomme de terre | 25 | 25 | 25 | 25 | 25 | 25 |

## Rendements wallons (t/ha)

| culture | n | min_t_ha | median_t_ha | max_t_ha | missing |
| --- | --- | --- | --- | --- | --- |
| Betterave sucrière | 25 | 53.96 | 77.8 | 96.93 | 0 |
| Colza | 25 | 3.02 | 3.83 | 4.54 | 0 |
| Froment et épeautre | 24 | 6.5 | 8.38 | 9.22 | 1 |
| Maïs fourrager | 23 | 38.82 | 44.43 | 49.34 | 2 |
| Maïs grain | 14 | 7.4 | 8.55 | 10.14 | 0 |
| Orge | 25 | 6.07 | 7.79 | 8.89 | 0 |
| Orge d'hiver | 14 | 6.15 | 8.13 | 9.2 | 0 |
| Pomme de terre | 25 | 20.88 | 42.73 | 50.21 | 0 |

## Extrêmes climatiques (Wallonie, z-score saison avril–septembre)

| indicateur | annee_min | z_min | annee_max | z_max |
| --- | --- | --- | --- | --- |
| température saison (z) | 2021 | -1.824 | 2018 | 2.345 |
| précipitations saison (z) | 2018 | -1.821 | 2024 | 2.32 |
| ET0 saison (z) | 2000 | -1.246 | 2020 | 2.107 |

## Valeurs manquantes

| colonne | n_na | part_na |
| --- | --- | --- |
| yield_t_ha | 31 | 0.029 |
| production_kt | 12 | 0.0112 |
| area_kha | 6 | 0.0056 |

## Limites de comparabilité

- Un point ERA5 par centroïde provincial : ce n'est pas une moyenne
  des parcelles, ni une pondération par la SAU.
- Saison de végétation unique (avril–septembre) pour toutes les cultures.
- Rendement = production / superficie (Eurostat) ; quelques BE3 imputés.
- Jointure interne : les années absentes d'une source sont écartées.
- Corrélation ≠ causalité (analyse statistique : feature 3).
- Pas de scénario CMIP6 / SSP dans cette table (observation seule).
