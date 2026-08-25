"""Nettoyage des rendements Eurostat (superficie, production, rendement)."""

from __future__ import annotations

import logging
from io import StringIO
from pathlib import Path

import numpy as np
import pandas as pd

from agri_climat.settings import (
    CROP_LABELS_FR,
    END_YEAR,
    GEO_LABELS_FR,
    PROVINCE_CODES,
    START_YEAR,
    WALLONIA_NUTS1,
    YIELD_BOUNDS_T_HA,
)

logger = logging.getLogger(__name__)

_AREA = "AR_THS_HA"
_PROD = "HPRD_HUMD_EU_THS_T"


def parse_eurostat_obs(value: object) -> float:
    """Convertit une cellule TSV Eurostat en nombre (``:`` et flags ignorés).

    Parameters
    ----------
    value
        Texte brut (ex. ``"8.42"``, ``":"``, ``"196.42 e"``).

    Returns
    -------
    float
        Valeur numérique, ou NaN si absente / non parsable.
    """
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return float("nan")
    text = str(value).strip()
    if text in {"", ":"}:
        return float("nan")
    token = text.split()[0]
    try:
        return float(token)
    except ValueError:
        return float("nan")


def parse_eurostat_tsv(text: str) -> pd.DataFrame:
    """Passe un TSV SDMX Eurostat (format large) en table longue.

    Parameters
    ----------
    text
        Contenu brut du fichier TSV.

    Returns
    -------
    pandas.DataFrame
        Colonnes : ``crop_code``, ``strucpro``, ``geo``, ``year``, ``value``.
    """
    frame = pd.read_csv(StringIO(text), sep="\t")
    id_col = frame.columns[0]
    year_cols = [str(col).strip() for col in frame.columns[1:]]
    frame.columns = ["id"] + year_cols
    parts = frame["id"].str.split(",", expand=True)
    parts.columns = ["freq", "crop_code", "strucpro", "geo"]
    long_df = pd.concat([parts, frame[year_cols]], axis=1)
    long_df = long_df.melt(
        id_vars=["freq", "crop_code", "strucpro", "geo"],
        var_name="year",
        value_name="raw_value",
    )
    long_df["year"] = pd.to_numeric(long_df["year"], errors="coerce")
    long_df["value"] = long_df["raw_value"].map(parse_eurostat_obs)
    return long_df.drop(columns=["freq", "raw_value"])


def _is_plausible_yield(crop_code: str, yield_t_ha: float) -> bool:
    """True si le rendement tombe dans les bornes attendues de la culture."""
    if pd.isna(yield_t_ha):
        return False
    low, high = YIELD_BOUNDS_T_HA.get(crop_code, (0.0, 1e6))
    return low <= float(yield_t_ha) <= high


def _fix_wallonia_from_provinces(wide: pd.DataFrame) -> pd.DataFrame:
    """Remplace la ligne Wallonie (BE3) par la somme des provinces si aberrante.

    Eurostat publie parfois une production NUTS1 incohérente (unité cassée)
    alors que les cinq provinces sont exploitables.
    """
    provinces = wide[wide["geo"].isin(PROVINCE_CODES)]
    if provinces.empty:
        return wide

    summed = (
        provinces.groupby(["crop_code", "year"], as_index=False)
        .agg(area_kha=("area_kha", "sum"), production_kt=("production_kt", "sum"))
    )
    summed["geo"] = WALLONIA_NUTS1
    summed["yield_t_ha"] = summed["production_kt"] / summed["area_kha"]

    rows: list[pd.Series] = []
    for _, row in wide.iterrows():
        if row["geo"] != WALLONIA_NUTS1:
            rows.append(row)
            continue
        official_ok = _is_plausible_yield(row["crop_code"], row["yield_t_ha"])
        if official_ok:
            rows.append(row)
            continue
        replacement = summed[
            (summed["crop_code"] == row["crop_code"]) & (summed["year"] == row["year"])
        ]
        if replacement.empty or not _is_plausible_yield(
            row["crop_code"], replacement.iloc[0]["yield_t_ha"]
        ):
            rows.append(row)
            continue
        fixed = row.copy()
        fixed["area_kha"] = replacement.iloc[0]["area_kha"]
        fixed["production_kt"] = replacement.iloc[0]["production_kt"]
        fixed["yield_t_ha"] = replacement.iloc[0]["yield_t_ha"]
        fixed["imputed"] = True
        logger.warning(
            "BE3 %s %s : production officielle remplacée par la somme des provinces",
            row["crop_code"],
            int(row["year"]),
        )
        rows.append(fixed)
    return pd.DataFrame(rows)


def clean_rendements(tsv_text: str) -> pd.DataFrame:
    """Harmonise les rendements wallons (une ligne = culture × territoire × année).

    Parameters
    ----------
    tsv_text
        TSV Eurostat brut.

    Returns
    -------
    pandas.DataFrame
        Colonnes : ``year``, ``geo``, ``geo_label``, ``crop_code``,
        ``crop_label``, ``area_kha``, ``production_kt``, ``yield_t_ha``,
        ``imputed``.
    """
    long_df = parse_eurostat_tsv(tsv_text)
    long_df = long_df[
        long_df["crop_code"].isin(CROP_LABELS_FR)
        & long_df["geo"].isin(GEO_LABELS_FR)
        & long_df["year"].between(START_YEAR, END_YEAR)
    ]
    wide = long_df.pivot_table(
        index=["crop_code", "geo", "year"],
        columns="strucpro",
        values="value",
        aggfunc="first",
    ).reset_index()
    wide = wide.rename(columns={_AREA: "area_kha", _PROD: "production_kt"})
    for col in ("area_kha", "production_kt"):
        if col not in wide.columns:
            wide[col] = float("nan")
    wide["yield_t_ha"] = wide["production_kt"] / wide["area_kha"]
    wide["yield_t_ha"] = wide["yield_t_ha"].replace([np.inf, -np.inf], np.nan)
    wide["imputed"] = False
    wide = _fix_wallonia_from_provinces(wide)
    wide["crop_label"] = wide["crop_code"].map(CROP_LABELS_FR)
    wide["geo_label"] = wide["geo"].map(GEO_LABELS_FR)
    wide["yield_t_ha"] = wide["yield_t_ha"].round(3)
    wide["area_kha"] = wide["area_kha"].round(3)
    wide["production_kt"] = wide["production_kt"].round(3)
    cols = [
        "year",
        "geo",
        "geo_label",
        "crop_code",
        "crop_label",
        "area_kha",
        "production_kt",
        "yield_t_ha",
        "imputed",
    ]
    return (
        wide[cols]
        .sort_values(["crop_code", "geo", "year"])
        .reset_index(drop=True)
    )


def clean_rendements_file(raw_tsv: Path, processed_root: Path) -> Path:
    """Lit le TSV brut, écrit ``rendements.csv``.

    Parameters
    ----------
    raw_tsv
        Fichier Eurostat brut.
    processed_root
        Dossier ``data/processed``.

    Returns
    -------
    Path
        CSV nettoyé.
    """
    processed_root.mkdir(parents=True, exist_ok=True)
    table = clean_rendements(raw_tsv.read_text(encoding="utf-8"))
    target = processed_root / "rendements.csv"
    table.to_csv(target, index=False)
    logger.info("Écrit %s (%s lignes)", target, len(table))
    return target
