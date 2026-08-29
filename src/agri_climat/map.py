"""Carte de synthèse : choroplèthe provinciale (matplotlib + GeoJSON)."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure

from agri_climat.analyse import add_yield_residuals, correlations_by_crop
from agri_climat.data.download import download_nuts_provinces, nuts_processed_path
from agri_climat.paths import pictures_readme_dir, processed_dir, raw_dir
from agri_climat.settings import (
    FOCUS_CROP_CODE,
    GEO_LABELS_EN,
    MAP_FOCUS_CLIMATE_VAR,
    MAP_FOCUS_YEAR,
    PROVINCE_CODES,
)

logger = logging.getLogger(__name__)

README_MAP = "wheat-provinces-map.png"
MISSING_FILL = "#d0d0d0"


def load_nuts_geojson(path: Path) -> dict:
    """Charge une FeatureCollection GeoJSON.

    Parameters
    ----------
    path
        Fichier ``nuts2_wallonie.geojson``.

    Returns
    -------
    dict
        GeoJSON.

    Raises
    ------
    FileNotFoundError
        Si le fichier n'existe pas.
    """
    if not path.exists():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def wheat_precip_spearman_by_province(table: pd.DataFrame) -> pd.DataFrame:
    """Spearman froment × pluie de saison, une ligne par province.

    Parameters
    ----------
    table
        Table consolidée (résidus ajoutés si absents).

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
        wheat = corr[
            (corr["crop_code"] == FOCUS_CROP_CODE)
            & (corr["climate_var"] == MAP_FOCUS_CLIMATE_VAR)
        ]
        if wheat.empty:
            rows.append({"geo": geo, "spearman_r": float("nan"), "n": 0})
            continue
        row = wheat.iloc[0]
        rows.append(
            {
                "geo": geo,
                "spearman_r": row["spearman_r"],
                "n": row["n"],
            }
        )
    return pd.DataFrame(rows)


def wheat_residual_by_province(
    table: pd.DataFrame,
    year: int = MAP_FOCUS_YEAR,
) -> pd.DataFrame:
    """Résidu de rendement froment (z) pour une année, par province.

    Parameters
    ----------
    table
        Table consolidée (résidus ajoutés si absents).
    year
        Année à cartographier (2024 par défaut).

    Returns
    -------
    pandas.DataFrame
        Colonnes ``geo``, ``year``, ``yield_resid_z``.
    """
    work = table.copy()
    if "yield_resid_z" not in work.columns:
        work = add_yield_residuals(work)
    subset = work[
        (work["crop_code"] == FOCUS_CROP_CODE)
        & (work["year"] == year)
        & (work["geo"].isin(PROVINCE_CODES))
    ]
    return subset[["geo", "year", "yield_resid_z"]].drop_duplicates("geo")


def _polygon_patches(geometry: dict) -> list:
    """Convertit un Polygon / MultiPolygon GeoJSON en patches matplotlib."""
    from matplotlib.patches import Polygon

    patches: list = []
    gtype = geometry.get("type")
    coords = geometry.get("coordinates", [])
    if gtype == "Polygon":
        rings = [coords]
    elif gtype == "MultiPolygon":
        rings = coords
    else:
        return patches
    for polygon in rings:
        if not polygon:
            continue
        exterior = polygon[0]
        patches.append(
            Polygon(exterior, closed=True, linewidth=0.9, edgecolor="white")
        )
    return patches


def _ring_centroid(geometry: dict) -> tuple[float, float]:
    """Centroid approximatif (moyenne des sommets de l'anneau extérieur)."""
    gtype = geometry.get("type")
    coords = geometry.get("coordinates", [])
    if gtype == "Polygon":
        exterior = coords[0]
    elif gtype == "MultiPolygon":
        # Plus grand polygone (le plus de sommets) pour le libellé.
        exterior = max((poly[0] for poly in coords if poly), key=len)
    else:
        return (0.0, 0.0)
    xs = [pt[0] for pt in exterior]
    ys = [pt[1] for pt in exterior]
    return (float(np.mean(xs)), float(np.mean(ys)))


def _draw_choropleth(
    ax: Axes,
    features: list[dict],
    value_by_geo: dict[str, float],
    cmap: str,
    vmin: float,
    vmax: float,
    title: str,
    cbar_label: str,
) -> None:
    """Remplit les provinces selon ``value_by_geo`` ; gris si valeur manquante."""
    import matplotlib.cm as cm
    import matplotlib.colors as mcolors

    norm = mcolors.Normalize(vmin=vmin, vmax=vmax)
    scaler = cm.ScalarMappable(norm=norm, cmap=cmap)
    scaler.set_array([])
    for feat in features:
        nuts_id = str(feat.get("properties", {}).get("NUTS_ID") or feat.get("id") or "")
        value = value_by_geo.get(nuts_id)
        face = MISSING_FILL
        if value is not None and not pd.isna(value):
            face = scaler.to_rgba(float(value))
        for patch in _polygon_patches(feat["geometry"]):
            patch.set_facecolor(face)
            ax.add_patch(patch)
        cx, cy = _ring_centroid(feat["geometry"])
        ax.text(
            cx,
            cy,
            GEO_LABELS_EN.get(nuts_id, nuts_id),
            ha="center",
            va="center",
            fontsize=8,
            color="0.15",
        )
    ax.autoscale()
    # Compensation latitude ~50° N pour limiter l'étirement est-ouest.
    ax.set_aspect(1.0 / np.cos(np.radians(50.4)))
    ax.set_axis_off()
    ax.set_title(title, fontsize=10)
    cbar = ax.figure.colorbar(scaler, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label(cbar_label, fontsize=8)


def plot_synthesis_map(
    geojson: dict,
    spearman: pd.DataFrame,
    residual: pd.DataFrame,
    year: int = MAP_FOCUS_YEAR,
) -> Figure:
    """Deux choroplèthes : Spearman froment–pluie, puis résidu de l'année focus.

    Parameters
    ----------
    geojson
        FeatureCollection des cinq provinces.
    spearman
        Sortie de ``wheat_precip_spearman_by_province``.
    residual
        Sortie de ``wheat_residual_by_province``.
    year
        Année du second panneau (titre).

    Returns
    -------
    matplotlib.figure.Figure
        Deux cartes côte à côte.
    """
    import matplotlib.pyplot as plt

    features = geojson.get("features", [])
    spearman_map = {
        str(row.geo): float(row.spearman_r)
        for row in spearman.itertuples(index=False)
        if not pd.isna(row.spearman_r)
    }
    residual_map = {
        str(row.geo): float(row.yield_resid_z)
        for row in residual.itertuples(index=False)
        if not pd.isna(row.yield_resid_z)
    }
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 5.2))
    _draw_choropleth(
        axes[0],
        features,
        spearman_map,
        cmap="RdBu_r",
        vmin=-1.0,
        vmax=1.0,
        title="Wheat vs seasonal rainfall (Spearman ρ)",
        cbar_label="ρ",
    )
    _draw_choropleth(
        axes[1],
        features,
        residual_map,
        cmap="RdBu_r",
        vmin=-2.5,
        vmax=2.5,
        title=f"Wheat yield residual in {year} (z)",
        cbar_label="z",
    )
    fig.suptitle(
        "Walloon provinces — wheat climate signal is not a single-province artefact",
        fontsize=11,
    )
    fig.tight_layout()
    return fig


def run_map(
    processed_root: Path | None = None,
    raw_root: Path | None = None,
    figures_root: Path | None = None,
) -> Path:
    """Écrit le GeoJSON filtré (si besoin), le CSV provincial et le PNG README.

    Parameters
    ----------
    processed_root
        Dossier ``data/processed``.
    raw_root
        Dossier ``data/raw`` (téléchargement GISCO).
    figures_root
        Dossier ``pictures/readme``.

    Returns
    -------
    Path
        Chemin du PNG.

    Raises
    ------
    FileNotFoundError
        Si ``rendements_climat.csv`` est absent.
    """
    processed = processed_root or processed_dir()
    raw = raw_root or raw_dir()
    figures = figures_root or pictures_readme_dir()
    csv_path = processed / "rendements_climat.csv"
    if not csv_path.exists():
        raise FileNotFoundError(csv_path)

    geo_path = nuts_processed_path(processed)
    if not geo_path.exists():
        download_nuts_provinces(raw, processed)
    geojson = load_nuts_geojson(geo_path)

    joined = pd.read_csv(csv_path)
    table = add_yield_residuals(joined)
    spearman = wheat_precip_spearman_by_province(table)
    residual = wheat_residual_by_province(table)
    # Table réutilisable par le dashboard (Feature 7).
    summary = spearman.merge(residual, on="geo", how="left")
    summary_path = processed / "carte_provinces.csv"
    summary.to_csv(summary_path, index=False)
    logger.info("Écrit %s", summary_path)

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    figures.mkdir(parents=True, exist_ok=True)
    png_path = figures / README_MAP
    fig = plot_synthesis_map(geojson, spearman, residual)
    fig.savefig(png_path, dpi=140, bbox_inches="tight")
    plt.close(fig)
    logger.info("Écrit %s", png_path)
    print(summary.to_string(index=False))
    print(f"\nMap : {png_path}")
    return png_path
