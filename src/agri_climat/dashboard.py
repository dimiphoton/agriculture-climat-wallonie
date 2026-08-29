"""Figures Plotly et chargement pour le dashboard Streamlit."""

from __future__ import annotations

import logging
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from plotly.graph_objects import Figure

from agri_climat.analyse import (
    add_yield_residuals,
    atypical_years,
    correlations_by_crop,
    sensitivity_ranking,
)
from agri_climat.data.download import nuts_processed_path
from agri_climat.map import load_nuts_geojson
from agri_climat.ml import evaluate_all_crops
from agri_climat.paths import processed_dir, repo_root
from agri_climat.settings import (
    CLIMATE_EXTREME_ABS_Z,
    CROP_LABELS_FR,
    GEO_LABELS_FR,
    GROWING_SEASON_Z_COLS,
    PROVINCE_CODES,
    WALLONIA_NUTS1,
)

logger = logging.getLogger(__name__)

_CLIMATE_COLORS: dict[str, str] = {
    "température saison": "#c44e52",
    "précipitations saison": "#4c72b0",
    "ET0 saison": "#dd8452",
}

DISCLAIMER_FR = (
    "Corrélation ≠ causalité. Un écart de rendement qui va de pair avec "
    "un climat de saison anormal n'est pas une preuve que le climat a "
    "causé la perte. Prix, maladies, irrigation et variétés ne sont pas "
    "dans le modèle."
)


@dataclass
class DashboardBundle:
    """Données déjà calculées (analyse, ML, GeoJSON) pour l'app."""

    table: pd.DataFrame
    ranking: pd.DataFrame
    atypical: pd.DataFrame
    ml_metrics: pd.DataFrame
    geojson: dict


def load_dashboard_bundle(processed_root: Path | None = None) -> DashboardBundle:
    """Charge la table consolidée, les indicateurs et le GeoJSON.

    Parameters
    ----------
    processed_root
        Dossier ``data/processed``. Défaut : chemins du dépôt.

    Returns
    -------
    DashboardBundle
        Table avec résidus, classement, années atypiques, métriques ML,
        GeoJSON (vide si le fichier NUTS est absent).

    Raises
    ------
    FileNotFoundError
        Si ``rendements_climat.csv`` est absent.
    """
    processed = processed_root or processed_dir()
    csv_path = processed / "rendements_climat.csv"
    if not csv_path.exists():
        raise FileNotFoundError(csv_path)

    table = add_yield_residuals(pd.read_csv(csv_path))
    ranking = sensitivity_ranking(correlations_by_crop(table))
    atypical = atypical_years(table)
    ml_metrics = evaluate_all_crops(table)

    geo_path = nuts_processed_path(processed)
    if geo_path.exists():
        geojson = load_nuts_geojson(geo_path)
    else:
        geojson = {"type": "FeatureCollection", "features": []}

    return DashboardBundle(
        table=table,
        ranking=ranking,
        atypical=atypical,
        ml_metrics=ml_metrics,
        geojson=geojson,
    )


def crop_options(table: pd.DataFrame) -> list[tuple[str, str]]:
    """Couples (code, libellé) présents en Wallonie, ordre CROP_LABELS_FR.

    Parameters
    ----------
    table
        Table consolidée.

    Returns
    -------
    list of tuple
        ``(crop_code, crop_label)``.
    """
    wallonia = table[table["geo"] == WALLONIA_NUTS1]
    present = set(wallonia["crop_code"].astype(str))
    options: list[tuple[str, str]] = []
    for code, label in CROP_LABELS_FR.items():
        if code in present:
            options.append((code, label))
    extra = present - set(CROP_LABELS_FR)
    for code in sorted(extra):
        subset = wallonia[wallonia["crop_code"] == code]
        label = str(subset["crop_label"].iloc[0]) if not subset.empty else code
        options.append((code, label))
    return options


def year_bounds(table: pd.DataFrame, crop_code: str) -> tuple[int, int]:
    """Année min / max du rendement wallon pour une culture.

    Parameters
    ----------
    table
        Table consolidée.
    crop_code
        Code Eurostat.

    Returns
    -------
    tuple of int
        ``(year_min, year_max)``. ``(0, 0)`` si aucune ligne.
    """
    panel = table[
        (table["geo"] == WALLONIA_NUTS1)
        & (table["crop_code"] == crop_code)
        & table["year"].notna()
        & table["yield_t_ha"].notna()
    ]
    if panel.empty:
        return 0, 0
    years = panel["year"].astype(int)
    return int(years.min()), int(years.max())


def filter_wallonia_crop(
    table: pd.DataFrame,
    crop_code: str,
    year_min: int,
    year_max: int,
) -> pd.DataFrame:
    """Série Wallonie pour une culture et une plage d'années.

    Parameters
    ----------
    table
        Table consolidée (résidus si déjà calculés).
    crop_code
        Code Eurostat.
    year_min, year_max
        Bornes inclusives.

    Returns
    -------
    pandas.DataFrame
        Lignes triées par année.
    """
    mask = (
        (table["geo"] == WALLONIA_NUTS1)
        & (table["crop_code"] == crop_code)
        & (table["year"] >= year_min)
        & (table["year"] <= year_max)
    )
    return table.loc[mask].sort_values("year").reset_index(drop=True)


def spearman_by_province(
    table: pd.DataFrame,
    crop_code: str,
    climate_var: str,
) -> pd.DataFrame:
    """Spearman résidu × une variable climatique, une ligne par province.

    Parameters
    ----------
    table
        Table consolidée.
    crop_code
        Code Eurostat.
    climate_var
        Nom de colonne (ex. ``precip_growing_mm_z``).

    Returns
    -------
    pandas.DataFrame
        Colonnes ``geo``, ``spearman_r``, ``n``.
    """
    work = table.copy()
    if "yield_resid_t_ha" not in work.columns:
        work = add_yield_residuals(work)
    rows: list[dict[str, object]] = []
    for geo in PROVINCE_CODES:
        corr = correlations_by_crop(work, geo=geo)
        if corr.empty:
            rows.append({"geo": geo, "spearman_r": float("nan"), "n": 0})
            continue
        subset = corr[
            (corr["crop_code"] == crop_code) & (corr["climate_var"] == climate_var)
        ]
        if subset.empty:
            rows.append({"geo": geo, "spearman_r": float("nan"), "n": 0})
            continue
        row = subset.iloc[0]
        rows.append(
            {
                "geo": geo,
                "spearman_r": row["spearman_r"],
                "n": row["n"],
            }
        )
    return pd.DataFrame(rows)


def residual_z_by_province(
    table: pd.DataFrame,
    crop_code: str,
    year: int,
) -> pd.DataFrame:
    """Résidu de rendement (z) pour une culture × année, par province.

    Parameters
    ----------
    table
        Table consolidée.
    crop_code
        Code Eurostat.
    year
        Année à cartographier.

    Returns
    -------
    pandas.DataFrame
        Colonnes ``geo``, ``year``, ``yield_resid_z``.
    """
    work = table.copy()
    if "yield_resid_z" not in work.columns:
        work = add_yield_residuals(work)
    subset = work[
        (work["crop_code"] == crop_code)
        & (work["year"] == year)
        & (work["geo"].isin(PROVINCE_CODES))
    ]
    return subset[["geo", "year", "yield_resid_z"]].drop_duplicates("geo")


def plot_yield_series(panel: pd.DataFrame, crop_label: str) -> Figure:
    """Rendement observé et tendance linéaire (Wallonie).

    Parameters
    ----------
    panel
        Sortie de ``filter_wallonia_crop``.
    crop_label
        Libellé pour le titre.

    Returns
    -------
    plotly.graph_objects.Figure
        Série temporelle.
    """
    fig = go.Figure()
    if panel.empty:
        fig.update_layout(title=f"{crop_label} — aucune donnée")
        return fig
    fig.add_trace(
        go.Scatter(
            x=panel["year"],
            y=panel["yield_t_ha"],
            name="Observé",
            mode="lines+markers",
        )
    )
    if "yield_trend_t_ha" in panel.columns:
        fig.add_trace(
            go.Scatter(
                x=panel["year"],
                y=panel["yield_trend_t_ha"],
                name="Tendance",
                mode="lines",
                line={"dash": "dash", "color": "gray"},
            )
        )
    fig.update_layout(
        title=f"{crop_label} — Wallonie",
        xaxis_title="Année",
        yaxis_title="t/ha",
        template="plotly_white",
        legend={"orientation": "h", "y": 1.12},
        margin={"l": 40, "r": 20, "t": 60, "b": 40},
    )
    return fig


def plot_climate_z(panel: pd.DataFrame) -> Figure:
    """Z-scores de saison (température, pluie, ET0) pour les mêmes années.

    Parameters
    ----------
    panel
        Série Wallonie (une ligne par année).

    Returns
    -------
    plotly.graph_objects.Figure
        Trois courbes de z-scores.
    """
    fig = go.Figure()
    if panel.empty:
        fig.update_layout(title="Climat de saison — aucune donnée")
        return fig
    climate = panel.drop_duplicates(subset=["year"]).sort_values("year")
    for col, label in GROWING_SEASON_Z_COLS:
        if col not in climate.columns:
            continue
        fig.add_trace(
            go.Scatter(
                x=climate["year"],
                y=climate[col],
                name=label,
                mode="lines+markers",
                line={"color": _CLIMATE_COLORS.get(label, "#7f7f7f")},
            )
        )
    fig.add_hline(y=0, line_color="black", line_width=1)
    fig.add_hline(
        y=CLIMATE_EXTREME_ABS_Z,
        line_dash="dash",
        line_color="gray",
        line_width=1,
    )
    fig.add_hline(
        y=-CLIMATE_EXTREME_ABS_Z,
        line_dash="dash",
        line_color="gray",
        line_width=1,
    )
    fig.update_layout(
        title="Climat de saison (z-scores, avril–septembre)",
        xaxis_title="Année",
        yaxis_title="z-score",
        template="plotly_white",
        legend={"orientation": "h", "y": 1.12},
        margin={"l": 40, "r": 20, "t": 60, "b": 40},
    )
    return fig


def plot_province_choropleth(
    geojson: dict,
    values: pd.DataFrame,
    value_col: str,
    title: str,
    colorbar_title: str,
    zmin: float,
    zmax: float,
) -> Figure:
    """Choroplèthe provinciale Plotly (GeoJSON GISCO déjà filtré).

    Parameters
    ----------
    geojson
        FeatureCollection NUTS 2 wallonnes.
    values
        Une ligne par ``geo``, colonne ``value_col``.
    value_col
        Colonne à colorer.
    title, colorbar_title
        Libellés.
    zmin, zmax
        Échelle de couleur (fixe, comparable d'une année à l'autre).

    Returns
    -------
    plotly.graph_objects.Figure
        Carte.
    """
    fig = go.Figure()
    if not geojson.get("features") or values.empty:
        fig.update_layout(title=title + " — carte indisponible")
        return fig

    work = values.copy()
    work["label"] = work["geo"].map(lambda code: GEO_LABELS_FR.get(str(code), str(code)))
    # px.choropleth tire plotly.express ; go.Choropleth évite une dépendance d'import tardif.
    fig.add_trace(
        go.Choropleth(
            geojson=geojson,
            locations=work["geo"].astype(str),
            z=work[value_col],
            featureidkey="properties.NUTS_ID",
            text=work["label"],
            hovertemplate="%{text}<br>%{z:.2f}<extra></extra>",
            colorscale="RdBu_r",
            zmin=zmin,
            zmax=zmax,
            marker_line_color="white",
            marker_line_width=0.8,
            colorbar={"title": colorbar_title},
        )
    )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(
        title=title,
        margin={"l": 0, "r": 0, "t": 40, "b": 0},
        template="plotly_white",
    )
    return fig


def launch_dashboard() -> int:
    """Lance Streamlit sur ``webapp/app.py``.

    Returns
    -------
    int
        Code de sortie du processus Streamlit.
    """
    app = repo_root() / "webapp" / "app.py"
    if not app.exists():
        logger.error("App introuvable : %s", app)
        return 1
    return int(
        subprocess.call(
            [sys.executable, "-m", "streamlit", "run", str(app)],
        )
    )
