"""Import du climat Open-Meteo au grain natif journalier.

Les agrégats mensuels / annuels et la moyenne wallonne vivent dans
``sql/schema.sql`` (vues DuckDB), pas ici.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

import pandas as pd

from agri_climat.settings import (
    CLIMATE_POINTS,
    GROWING_SEASON_MONTHS,
    WALLONIA_NUTS1,
)

logger = logging.getLogger(__name__)

_DAILY_RENAME = {
    "temperature_2m_mean": "temp_mean_c",
    "temperature_2m_max": "temp_max_c",
    "precipitation_sum": "precip_mm",
    "et0_fao_evapotranspiration": "et0_mm",
}


def daily_from_openmeteo_json(payload: dict) -> pd.DataFrame:
    """Transforme un JSON Open-Meteo archive en table quotidienne.

    Parameters
    ----------
    payload
        Réponse API (clés ``daily``, ``geo_code``, ``geo_label``).

    Returns
    -------
    pandas.DataFrame
        Une ligne par jour, avec ``geo`` et ``geo_label``.
    """
    daily = payload["daily"]
    frame = pd.DataFrame(daily)
    frame["date"] = pd.to_datetime(frame["time"])
    frame = frame.drop(columns=["time"])
    frame = frame.rename(columns=_DAILY_RENAME)
    frame["geo"] = payload["geo_code"]
    frame["geo_label"] = payload["geo_label"]
    return frame


def daily_to_monthly(daily: pd.DataFrame) -> pd.DataFrame:
    """Agrège le quotidien : moyenne des températures, somme pluie et ET0.

    Parameters
    ----------
    daily
        Table produite par ``daily_from_openmeteo_json``.

    Returns
    -------
    pandas.DataFrame
        Une ligne par ``geo`` × année × mois.
    """
    work = daily.copy()
    work["year"] = work["date"].dt.year
    work["month"] = work["date"].dt.month
    monthly = (
        work.groupby(["geo", "geo_label", "year", "month"], as_index=False)
        .agg(
            temp_mean_c=("temp_mean_c", "mean"),
            temp_max_c=("temp_max_c", "mean"),
            precip_mm=("precip_mm", "sum"),
            et0_mm=("et0_mm", "sum"),
        )
    )
    for col in ("temp_mean_c", "temp_max_c"):
        monthly[col] = monthly[col].round(2)
    for col in ("precip_mm", "et0_mm"):
        monthly[col] = monthly[col].round(1)
    return monthly.sort_values(["geo", "year", "month"]).reset_index(drop=True)


def monthly_to_annual(monthly: pd.DataFrame) -> pd.DataFrame:
    """Calcule les totaux annuels et la saison de végétation (avril–septembre).

    Parameters
    ----------
    monthly
        Table produite par ``daily_to_monthly``.

    Returns
    -------
    pandas.DataFrame
        Une ligne par ``geo`` × année.
    """
    annual = (
        monthly.groupby(["geo", "geo_label", "year"], as_index=False)
        .agg(
            temp_mean_c=("temp_mean_c", "mean"),
            precip_mm=("precip_mm", "sum"),
            et0_mm=("et0_mm", "sum"),
        )
    )
    growing = monthly[monthly["month"].isin(GROWING_SEASON_MONTHS)]
    growing_agg = (
        growing.groupby(["geo", "year"], as_index=False)
        .agg(
            temp_mean_growing_c=("temp_mean_c", "mean"),
            precip_growing_mm=("precip_mm", "sum"),
            et0_growing_mm=("et0_mm", "sum"),
        )
    )
    merged = annual.merge(growing_agg, on=["geo", "year"], how="left")
    for col in (
        "temp_mean_c",
        "temp_mean_growing_c",
    ):
        merged[col] = merged[col].round(2)
    for col in ("precip_mm", "et0_mm", "precip_growing_mm", "et0_growing_mm"):
        merged[col] = merged[col].round(1)
    return merged.sort_values(["geo", "year"]).reset_index(drop=True)


def add_wallonia_mean(table: pd.DataFrame) -> pd.DataFrame:
    """Ajoute une série Wallonie = moyenne simple des cinq provinces.

    Parameters
    ----------
    table
        Table mensuelle ou annuelle déjà agrégée par province.

    Returns
    -------
    pandas.DataFrame
        Table d'origine plus les lignes ``BE3``.
    """
    province_codes = {point.code for point in CLIMATE_POINTS}
    provinces = table[table["geo"].isin(province_codes)]
    value_cols = [
        col
        for col in table.columns
        if col not in {"geo", "geo_label", "year", "month"}
    ]
    group_cols = [col for col in ("year", "month") if col in table.columns]
    wallonia = provinces.groupby(group_cols, as_index=False)[value_cols].mean()
    wallonia["geo"] = WALLONIA_NUTS1
    wallonia["geo_label"] = "Wallonie"
    combined = pd.concat([table, wallonia], ignore_index=True)
    sort_cols = ["geo", "year"] + (["month"] if "month" in combined.columns else [])
    return combined.sort_values(sort_cols).reset_index(drop=True)


def clean_climat_files(raw_root: Path, processed_root: Path) -> Path:
    """Lit les JSON bruts et écrit ``climat_quotidien.csv`` (5 provinces).

    La Wallonie (moyenne des points) et les agrégats année / saison sont
    des vues SQL, calculées ensuite par ``warehouse.build_warehouse``.

    Parameters
    ----------
    raw_root
        Dossier ``data/raw``.
    processed_root
        Dossier ``data/processed``.

    Returns
    -------
    Path
        ``climat_quotidien.csv``.
    """
    processed_root.mkdir(parents=True, exist_ok=True)
    dailies: list[pd.DataFrame] = []
    for point in CLIMATE_POINTS:
        path = raw_root / f"openmeteo_{point.code}.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        dailies.append(daily_from_openmeteo_json(payload))
    daily = pd.concat(dailies, ignore_index=True)
    daily = daily.sort_values(["geo", "date"]).reset_index(drop=True)
    cols = [
        "date",
        "geo",
        "geo_label",
        "temp_mean_c",
        "temp_max_c",
        "precip_mm",
        "et0_mm",
    ]
    daily_path = processed_root / "climat_quotidien.csv"
    daily[cols].to_csv(daily_path, index=False)
    logger.info("Écrit %s (%s lignes)", daily_path, len(daily))
    return daily_path
