# Agriculture and climate in Wallonia

| | |
|---|---|
| **Stack** | ![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white) ![pandas](https://img.shields.io/badge/pandas-2.x-150458?logo=pandas&logoColor=white) ![scipy](https://img.shields.io/badge/scipy-stats-8CAAE6?logo=scipy&logoColor=white) ![pyarrow](https://img.shields.io/badge/pyarrow-Parquet-34A001) ![matplotlib](https://img.shields.io/badge/matplotlib-EDA-11557c) ![requests](https://img.shields.io/badge/requests-HTTP-2b5b84) |
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

Feature 3 ranks Walloon crops by climate sensitivity: yield is linearly
detrended, then the residual is correlated (Spearman, Pearson as a check)
with growing-season temperature, rainfall and ET0 z-scores. On 2000–2024
Wallonia, **wheat** shows the clearest signal (seasonal rainfall,
Spearman ρ ≈ −0.68): wetter seasons tend to sit below the yield trend.
**Potato** tracks seasonal heat (ρ ≈ −0.46). **2024** (very wet) flags
several crops; **2018** (hot and dry) flags grain maize and potato. See
`docs/analyse.md` and `pictures/experiments/`. Correlation is not
causation. Portfolio README charts come in Feature 4; CMIP6 scenarios
remain out of scope until after a simple model (Feature 6 → optional
Feature 9).

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
python -m agri_climat analyse           # correlations, atypical years, wheat
python -m agri_climat download climat   # climate only
```

Internet access is needed for the first download (Eurostat and Open-Meteo).
Afterwards, `clean` and `join` work offline from `data/raw/` (join needs the
cleaned CSVs). Fast preview (no Jupyter window):

```bash
python -m agri_climat eda
```

This prints the EDA tables and writes
`pictures/experiments/eda-froment-pluie-saison.png`. Statistical analysis
(no GUI):

```bash
python -m agri_climat analyse
```

writes `docs/analyse.md` plus
`pictures/experiments/corr-spearman-wallonie.png` and
`froment-detrend-climat.png`. Optional notebooks (kernel = project `.venv`):
`notebooks/02-eda-jointure.ipynb`, `notebooks/03-analyse.ipynb`. Do not use
`plt.show()` — on Windows the Tk window can hang for minutes.

## Repo structure

```
brief/                 # original goal and portfolio brief
data/raw/              # downloaded files (gitignored)
data/processed/        # clean and joined tables (CSV / Parquet)
src/agri_climat/       # download, clean, join, analyse, CLI
notebooks/             # notebooks (call src/, no duplicated logic)
tests/                 # unit tests
docs/                  # decisions, EDA, statistical note, Marp presentations
pictures/experiments/  # analysis PNG (not the polished README figures)
```

See also `ROADMAP.md` and `JOURNAL.md` (French, like the rest of the
codebase comments).

## Presentations

- [Recruiter overview (EN)](docs/slides/presentation-recruteur-en.html)
- [Technical deep dive (EN)](docs/slides/presentation-technique-en.html)
- [Présentation grand public (FR)](docs/slides/presentation-recruteur-fr.html)
- [Présentation technique (FR)](docs/slides/presentation-technique-fr.html)
