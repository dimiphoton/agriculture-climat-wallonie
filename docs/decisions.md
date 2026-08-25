# Décisions

| Date | Décision | Alternative envisagée | Raison |
|---|---|---|---|
| 2026-08-25 | Rendements via Eurostat `apro_cpshr` (NUTS 1 Wallonie + 5 provinces), source nationale = Statbel | Télécharger les Excel Statbel / fiches EAW | Les pages Statbel sont protégées par captcha et les noms de fichiers changent chaque année ; Eurostat redistribue les mêmes chiffres officiels en TSV stable. L'EAW reste une source narrative, pas un extract brut. |
| 2026-08-25 | Climat via Open-Meteo Archive (ERA5), 5 points provinciaux, moyenne simple = Wallonie | Copernicus CDS (`cdsapi` + NetCDF) | Pas de compte ni de raster ; ERA5 reste la réanalyse de référence. CDS pourra être ajouté plus tard si un compte est disponible. |
| 2026-08-25 | Imputer BE3 par la somme des provinces si le rendement sort des bornes agronomiques | Laisser les valeurs officielles telles quelles | Rupture d'unité documentée (froment wallon 2011 à 1,17 kt au lieu d'environ 1 100 kt) alors que les provinces sont cohérentes. |
| 2026-08-25 | Saison de végétation = avril–septembre | Année civile seule, ou calendrier par culture | Compromis unique pour comparer les cultures à ce stade ; un calendrier cultural pourra affiner l'analyse (feature 3). |
| 2026-08-25 | Dépendances : pandas, requests, truststore | openpyxl, cdsapi, xarray, PyYAML | Suffisant pour TSV/JSON ; config en dataclasses. `truststore` aligne TLS sur les certificats Windows (certifi échoue souvent derrière un proxy). |
