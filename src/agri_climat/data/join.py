"""EDA sur la table consolidée (la jointure elle-même est en SQL / DuckDB)."""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from agri_climat.settings import CLIMATE_ANNUAL_VALUE_COLS, END_YEAR, START_YEAR

logger = logging.getLogger(__name__)

JOIN_KEYS = ("geo", "year")
_YIELD_ID_COLS = (
    "year",
    "geo",
    "geo_label",
    "crop_code",
    "crop_label",
    "area_kha",
    "production_kt",
    "yield_t_ha",
    "imputed",
)


def add_climate_anomalies(
    annual: pd.DataFrame,
    value_cols: tuple[str, ...] = CLIMATE_ANNUAL_VALUE_COLS,
) -> pd.DataFrame:
    """Ajoute l'anomalie brute et le z-score par territoire.

    Pour chaque ``geo``, la normale est la moyenne de la colonne sur toute
    la période présente dans la table (en pratique 2000–2024). L'anomalie
    est ``valeur - normale`` ; le z-score divise par l'écart-type du même
    groupe (NaN si l'écart-type est nul).

    Parameters
    ----------
    annual
        Table annuelle (une ligne par ``geo`` × ``year``).
    value_cols
        Colonnes climatiques à transformer.

    Returns
    -------
    pandas.DataFrame
        Table d'origine plus ``{col}_anom`` et ``{col}_z`` pour chaque colonne.
    """
    out = annual.copy()
    grouped = out.groupby("geo", sort=False)
    means = grouped[list(value_cols)].transform("mean")
    stds = grouped[list(value_cols)].transform("std")
    for col in value_cols:
        if col not in out.columns:
            continue
        anom = out[col] - means[col]
        zscore = anom / stds[col].replace(0, float("nan"))
        # Températures : 2 décimales ; totaux mm : 1 ; z-score : 3.
        decimals = 2 if "temp" in col else 1
        out[f"{col}_anom"] = anom.round(decimals)
        out[f"{col}_z"] = zscore.round(3)
    return out


def join_rendements_climat(
    rendements: pd.DataFrame,
    climat_annuel: pd.DataFrame,
) -> pd.DataFrame:
    """Jointure interne rendements × climat (anomalies incluses).

    Une ligne = culture × territoire × année. Le climat (et ses anomalies)
    est le même pour toutes les cultures d'un couple ``geo`` × ``year``.
    Les années présentes d'un seul côté sont écartées.

    Parameters
    ----------
    rendements
        Sortie de ``clean_rendements``.
    climat_annuel
        Sortie annuelle de ``clean_climat`` (provinces + Wallonie).

    Returns
    -------
    pandas.DataFrame
        Table consolidée, triée par culture, territoire, année.

    Raises
    ------
    ValueError
        Si une clé de jointure est absente.
    """
    for name, table in ("rendements", rendements), ("climat", climat_annuel):
        missing = [col for col in JOIN_KEYS if col not in table.columns]
        if missing:
            raise ValueError(f"{name} : colonnes manquantes {missing}")

    climate = add_climate_anomalies(climat_annuel)
    climate_extra = [col for col in climate.columns if col not in JOIN_KEYS]
    # geo_label climat = doublon du label rendements ; on ne le reprend pas.
    climate_extra = [col for col in climate_extra if col != "geo_label"]
    right = climate[list(JOIN_KEYS) + climate_extra]
    joined = rendements.merge(right, on=list(JOIN_KEYS), how="inner")
    ordered = [col for col in _YIELD_ID_COLS if col in joined.columns]
    rest = [col for col in joined.columns if col not in ordered]
    return (
        joined[ordered + rest]
        .sort_values(["crop_code", "geo", "year"])
        .reset_index(drop=True)
    )


def coverage_by_crop_geo(joined: pd.DataFrame) -> pd.DataFrame:
    """Nombre d'années présentes par culture et territoire."""
    return (
        joined.groupby(["crop_label", "geo"], as_index=False)
        .size()
        .rename(columns={"size": "n_years"})
        .pivot(index="crop_label", columns="geo", values="n_years")
        .fillna(0)
        .astype(int)
    )


def yield_summary_by_crop(joined: pd.DataFrame) -> pd.DataFrame:
    """Min / médiane / max des rendements (t/ha) par culture, Wallonie seule.

    On se restreint à BE3 pour ne pas mélanger des niveaux géographiques.
    """
    wallonia = joined[joined["geo"] == "BE3"]
    if wallonia.empty:
        wallonia = joined
    summary = wallonia.groupby("crop_label")["yield_t_ha"].agg(
        n="count",
        min_t_ha="min",
        median_t_ha="median",
        max_t_ha="max",
        missing=lambda s: int(s.isna().sum()),
    )
    return summary.round(2).reset_index()


def climate_extremes(joined: pd.DataFrame, geo: str = "BE3") -> pd.DataFrame:
    """Années les plus chaudes / sèches / humides (saison de végétation).

    Parameters
    ----------
    joined
        Table consolidée.
    geo
        Territoire à extraire (Wallonie par défaut).

    Returns
    -------
    pandas.DataFrame
        Une ligne par indicateur, avec l'année min et l'année max du z-score.
    """
    subset = joined[joined["geo"] == geo].drop_duplicates(subset=["year"])
    rows: list[dict[str, object]] = []
    indicators = [
        ("temp_mean_growing_c_z", "température saison (z)"),
        ("precip_growing_mm_z", "précipitations saison (z)"),
        ("et0_growing_mm_z", "ET0 saison (z)"),
    ]
    for col, label in indicators:
        if col not in subset.columns or subset[col].isna().all():
            continue
        idx_min = subset[col].idxmin()
        idx_max = subset[col].idxmax()
        rows.append(
            {
                "indicateur": label,
                "annee_min": int(subset.loc[idx_min, "year"]),
                "z_min": subset.loc[idx_min, col],
                "annee_max": int(subset.loc[idx_max, "year"]),
                "z_max": subset.loc[idx_max, col],
            }
        )
    return pd.DataFrame(rows)


def missingness(joined: pd.DataFrame) -> pd.DataFrame:
    """Part de valeurs manquantes par colonne (colonnes > 0 % seulement)."""
    share = joined.isna().mean().rename("part_na")
    counts = joined.isna().sum().rename("n_na")
    table = pd.concat([counts, share], axis=1)
    table = table[table["n_na"] > 0].sort_values("n_na", ascending=False)
    table["part_na"] = table["part_na"].round(4)
    return table.reset_index().rename(columns={"index": "colonne"})


def _md_table(frame: pd.DataFrame) -> str:
    """Table Markdown simple (sans dépendance tabulate)."""
    if frame.empty:
        return "*(aucune ligne)*\n"
    cols = [str(c) for c in frame.columns]
    header = "| " + " | ".join(cols) + " |"
    sep = "| " + " | ".join("---" for _ in cols) + " |"
    lines = [header, sep]
    for _, row in frame.iterrows():
        cells = [str(row[c]) for c in frame.columns]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines) + "\n"


def build_eda_markdown(joined: pd.DataFrame) -> str:
    """Rédige le rapport d'exploration à partir de la table consolidée.

    Parameters
    ----------
    joined
        Sortie de ``join_rendements_climat``.

    Returns
    -------
    str
        Texte Markdown (français).
    """
    years = joined["year"]
    n_imputed = int(joined["imputed"].sum()) if "imputed" in joined.columns else 0
    coverage = coverage_by_crop_geo(joined).reset_index().rename(
        columns={"crop_label": "culture"}
    )
    yields = yield_summary_by_crop(joined).rename(columns={"crop_label": "culture"})
    extremes = climate_extremes(joined)
    missing = missingness(joined)

    parts = [
        "# Exploration — table rendements × climat",
        "",
        "Table exportée de la vue DuckDB ``v_rendements_climat`` "
        "(schéma : ``sql/schema.sql``).",
        "",
        f"Période observée : {int(years.min())}–{int(years.max())} "
        f"(référence d'anomalie climatique = {START_YEAR}–{END_YEAR} "
        "par territoire).",
        "",
        f"- Lignes : **{len(joined)}** (culture × geo × année).",
        f"- Cultures : {joined['crop_label'].nunique()} "
        f"({', '.join(sorted(joined['crop_label'].unique()))}).",
        f"- Territoires : {', '.join(sorted(joined['geo'].unique()))}.",
        f"- Lignes de rendement imputées (BE3) : **{n_imputed}**.",
        "",
        "## Couverture (nombre d'années)",
        "",
        _md_table(coverage),
        "## Rendements wallons (t/ha)",
        "",
        _md_table(yields),
        "## Extrêmes climatiques (Wallonie, z-score saison avril–septembre)",
        "",
        _md_table(extremes),
        "## Valeurs manquantes",
        "",
        _md_table(missing) if not missing.empty else "Aucune valeur manquante.\n",
        "## Limites de comparabilité",
        "",
        "- Un point ERA5 par centroïde provincial : ce n'est pas une moyenne",
        "  des parcelles, ni une pondération par la SAU.",
        "- Saison de végétation unique (avril–septembre) pour toutes les cultures.",
        "- Rendement = production / superficie (Eurostat) ; quelques BE3 imputés.",
        "- Jointure interne SQL (vue ``v_rendements_climat``) : les années",
        "  absentes d'une source sont écartées. Agrégation journalier → annuel",
        "  dans ``sql/schema.sql`` (pas un ``pd.merge`` amont).",
        "- Corrélation ≠ causalité (analyse statistique : feature 3).",
        "- Pas de scénario CMIP6 / SSP dans cette table (observation seule).",
        "",
    ]
    return "\n".join(parts)


def join_processed_files(processed_root: Path, docs_root: Path | None = None) -> Path:
    """Construit l'entrepôt DuckDB, exporte les vues, écrit le rapport EDA.

    Parameters
    ----------
    processed_root
        Dossier ``data/processed``.
    docs_root
        Dossier ``docs/`` pour ``eda.md``. Ignoré si ``None``.

    Returns
    -------
    Path
        Chemin du CSV consolidé (export de ``v_rendements_climat``).

    Raises
    ------
    FileNotFoundError
        Si ``rendements.csv`` ou ``climat_quotidien.csv`` est absent.
    """
    from agri_climat.data.warehouse import build_warehouse

    joined = build_warehouse(processed_root)
    csv_path = processed_root / "rendements_climat.csv"

    if docs_root is not None:
        docs_root.mkdir(parents=True, exist_ok=True)
        eda_path = docs_root / "eda.md"
        eda_path.write_text(build_eda_markdown(joined), encoding="utf-8")
        logger.info("Écrit %s", eda_path)

    return csv_path
