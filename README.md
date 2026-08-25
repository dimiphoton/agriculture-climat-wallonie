# Agriculture and climate in Wallonia

| | |
|---|---|
| **Stack** | ![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white) ![pandas](https://img.shields.io/badge/pandas-2.x-150458?logo=pandas&logoColor=white) ![requests](https://img.shields.io/badge/requests-HTTP-2b5b84) |
| **Level** | Intermediate *(proposal — to confirm)* |
| **Data specialty** | BI / statistical analysis |

## Objective

Which Walloon crops are most sensitive to recent climate variability, and
which years were most at risk? This project builds a clean yield × climate
dataset and will turn it into a static report plus an interactive dashboard
for sector stakeholders (cooperatives, crop insurers, public administration).

## Data

- **Yields**: Eurostat table `apro_cpshr` (crop area and production at NUTS 1
  Wallonia and NUTS 2 provinces). The national source is Statbel; Eurostat is
  used because it exposes a stable TSV API. Period: 2000–2024. Crops: wheat
  and spelt, barley, winter barley, grain maize, fodder maize, potatoes,
  sugar beet, rapeseed.
- **Climate**: Open-Meteo Archive (ERA5 reanalysis) at five provincial
  centroids — daily temperature, precipitation and FAO ET0, then aggregated
  to monthly / annual / growing-season (April–September) series. Wallonia =
  simple mean of the five points.

Raw files stay in `data/raw/` (not committed). Clean tables are in
`data/processed/`.

## Result

Feature 1 delivers a reproducible pipeline and three analysis-ready tables
(`rendements.csv`, `climat_mensuel.csv`, `climat_annuel.csv`). Statistical
analysis, charts and the dashboard come in later features.

## Reproduce

Python 3.11+ required.

```bash
pip install -e ".[dev]"
python -m agri_climat run
pytest
```

Useful commands:

```bash
python -m agri_climat download          # raw files only
python -m agri_climat clean             # rebuild processed tables
python -m agri_climat download climat   # climate only
```

Internet access is needed for the first download (Eurostat and Open-Meteo).
Afterwards, `clean` works offline from `data/raw/`.

## Repo structure

```
brief/                 # original goal and portfolio brief
data/raw/              # downloaded files (gitignored)
data/processed/        # clean CSV tables
src/agri_climat/       # download, clean, CLI
tests/                 # unit tests on the cleaners
docs/                  # decisions, Marp presentations
```

See also `ROADMAP.md` and `JOURNAL.md` (French, like the rest of the
codebase comments).

## Presentations

- [Recruiter overview (EN)](docs/slides/presentation-recruteur-en.html)
- [Technical deep dive (EN)](docs/slides/presentation-technique-en.html)
- [Présentation grand public (FR)](docs/slides/presentation-recruteur-fr.html)
- [Présentation technique (FR)](docs/slides/presentation-technique-fr.html)
