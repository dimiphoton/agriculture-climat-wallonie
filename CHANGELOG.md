# Changelog

## [Non publié]

### Feature 1 — Acquisition et nettoyage

- Pipeline CLI (`python -m agri_climat run`) : téléchargement Eurostat
  (rendements NUTS 1–2 wallons) et Open-Meteo / ERA5 (climat quotidien),
  puis tables nettoyées dans `data/processed/`.
- Correction des productions wallonnes aberrantes (ex. froment 2011) par
  somme des provinces lorsque le rendement officiel sort des bornes.
- Package renommé `agri_climat` (l'ancien `mon_projet` du template est retiré).
- `truststore` pour le TLS via les certificats système (Windows / proxy).

### Initialisation

- Projet créé à partir du template portfolio.
