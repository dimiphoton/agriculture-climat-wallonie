# Agriculture and climate in Wallonia

| | |
|---|---|
| **Stack** | ![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white) ![pandas](https://img.shields.io/badge/pandas-2.x-150458?logo=pandas&logoColor=white) ![pyarrow](https://img.shields.io/badge/pyarrow-Parquet-34A001) ![matplotlib](https://img.shields.io/badge/matplotlib-EDA-11557c) ![requests](https://img.shields.io/badge/requests-HTTP-2b5b84) |
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
  simple mean of the five points. Annual series include anomalies and
  z-scores versus the 2000–2024 mean of each territory.

Raw files stay in `data/raw/` (not committed). Clean and joined tables are
in `data/processed/` (`rendements.csv`, `climat_*.csv`,
`rendements_climat.csv` / `.parquet`).

## Result

Feature 2 delivers a joined yield × climate table (CSV and Parquet) with
climate anomalies, a generated EDA note (`docs/eda.md`), and an exploration
notebook (`notebooks/02-eda-jointure.ipynb`). Correlations, portfolio charts
and the dashboard come in later features. Climate-model scenarios (CMIP6)
are intentionally out of this table — see `docs/decisions.md`.

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
python -m agri_climat clean             # rebuild processed climate/yield tables
python -m agri_climat join              # join + anomalies + docs/eda.md
python -m agri_climat eda               # tables + PNG, no GUI
python -m agri_climat download climat   # climate only
```

Internet access is needed for the first download (Eurostat and Open-Meteo).
Afterwards, `clean` and `join` work offline from `data/raw/` (join needs the
cleaned CSVs). Fast preview (no Jupyter window):

```bash
python -m agri_climat eda
```

This prints the EDA tables and writes
`pictures/experiments/eda-froment-pluie-saison.png`. Optional notebook:
`notebooks/02-eda-jointure.ipynb` (kernel = project `.venv`). Do not use
`plt.show()` — on Windows the Tk window can hang for minutes.

## Repo structure

```
brief/                 # original goal and portfolio brief
data/raw/              # downloaded files (gitignored)
data/processed/        # clean and joined tables (CSV / Parquet)
src/agri_climat/       # download, clean, join, CLI
notebooks/             # EDA notebook (calls src/, no duplicated logic)
tests/                 # unit tests
docs/                  # decisions, EDA note, Marp presentations
```

See also `ROADMAP.md` and `JOURNAL.md` (French, like the rest of the
codebase comments).

## Presentations

- [Recruiter overview (EN)](docs/slides/presentation-recruteur-en.html)
- [Technical deep dive (EN)](docs/slides/presentation-technique-en.html)
- [Présentation grand public (FR)](docs/slides/presentation-recruteur-fr.html)
- [Présentation technique (FR)](docs/slides/presentation-technique-fr.html)
