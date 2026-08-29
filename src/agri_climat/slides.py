"""Figures sobres pour les slides Marp (un message par image)."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

from agri_climat.analyse import (
    add_yield_residuals,
    atypical_years,
    correlations_by_crop,
    sensitivity_ranking,
)
from agri_climat.data.download import nuts_processed_path
from agri_climat.map import (
    _draw_choropleth,
    load_nuts_geojson,
    wheat_precip_spearman_by_province,
)
from agri_climat.ml import evaluate_crop
from agri_climat.paths import pictures_presentations_dir, processed_dir
from agri_climat.settings import (
    CROP_LABELS_EN,
    CROP_LABELS_FR,
    FOCUS_CROP_CODE,
    GEO_LABELS_EN,
    GEO_LABELS_FR,
    MAP_FOCUS_YEAR,
    WALLONIA_NUTS1,
)

if TYPE_CHECKING:
    from matplotlib.figure import Figure

logger = logging.getLogger(__name__)

_RAIN = "#4c72b0"
_HEAT = "#c44e52"
_CREAM = "#f3eee6"
_SLIDE_RANKING_N = 5

_FR_TO_CODE: dict[str, str] = {label: code for code, label in CROP_LABELS_FR.items()}


def _style(ax) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def _cream(fig, ax) -> None:
    """Fond crème : le graphe se fond dans le thème Marp."""
    fig.patch.set_facecolor(_CREAM)
    ax.set_facecolor(_CREAM)


def _crop_name(fr_label: str, lang: str) -> str:
    if lang == "en":
        code = _FR_TO_CODE.get(fr_label)
        if code:
            return CROP_LABELS_EN.get(code, fr_label)
    return fr_label


def plot_slide_ranking(ranking: pd.DataFrame, lang: str) -> Figure:
    """Cinq cultures au |Spearman| le plus fort — barre = pluie ou chaleur.

    Parameters
    ----------
    ranking
        Sortie de ``sensitivity_ranking``.
    lang
        ``fr`` ou ``en``.

    Returns
    -------
    matplotlib.figure.Figure
        Une idée : froment/pluie vs pomme de terre/chaleur.
    """
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch

    fig, ax = plt.subplots(figsize=(9.0, 4.2))
    work = ranking.dropna(subset=["spearman_r"]).copy()
    if work.empty:
        ax.set_title("—")
        fig.tight_layout()
        return fig
    work["abs_r"] = work["spearman_r"].abs()
    work = work.nlargest(_SLIDE_RANKING_N, "abs_r").sort_values("abs_r")
    colors = [
        _RAIN if "précip" in str(lab) else _HEAT for lab in work["climate_label"]
    ]
    y_pos = np.arange(len(work))
    ax.barh(y_pos, work["spearman_r"], color=colors, height=0.65)
    ax.axvline(0, color="0.2", linewidth=0.9)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(
        [_crop_name(str(lab), lang) for lab in work["crop_label"]],
        fontsize=12,
    )
    lo = min(-1.0, float(work["spearman_r"].min()) - 0.08)
    hi = max(0.15, float(work["spearman_r"].max()) + 0.15)
    ax.set_xlim(lo, hi)
    ax.set_xlabel("Spearman ρ", fontsize=11)
    if lang == "fr":
        legend = [
            Patch(facecolor=_RAIN, label="Pluie de saison"),
            Patch(facecolor=_HEAT, label="Chaleur de saison"),
        ]
    else:
        legend = [
            Patch(facecolor=_RAIN, label="Rain"),
            Patch(facecolor=_HEAT, label="Heat"),
        ]
    ax.legend(handles=legend, loc="lower left", frameon=False, fontsize=11)
    _style(ax)
    _cream(fig, ax)
    fig.tight_layout()
    return fig


def plot_slide_map(geojson: dict, spearman: pd.DataFrame, lang: str) -> Figure:
    """Une seule carte : Spearman froment × pluie par province.

    Parameters
    ----------
    geojson
        Provinces NUTS 2.
    spearman
        Sortie de ``wheat_precip_spearman_by_province``.
    lang
        ``fr`` ou ``en``.

    Returns
    -------
    matplotlib.figure.Figure
        Message : ce n'est pas un artefact d'une seule province.
    """
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(7.2, 5.4))
    value_by_geo = {
        str(row.geo): float(row.spearman_r)
        for row in spearman.itertuples(index=False)
        if not pd.isna(row.spearman_r)
    }
    _draw_choropleth(
        ax,
        geojson.get("features", []),
        value_by_geo,
        cmap="RdBu_r",
        vmin=-1.0,
        vmax=1.0,
        title="",
        cbar_label="wheat × rain (ρ)" if lang == "en" else "froment × pluie (ρ)",
        labels=GEO_LABELS_FR if lang == "fr" else GEO_LABELS_EN,
    )
    ax.set_title("")
    _cream(fig, ax)
    fig.tight_layout()
    return fig


def plot_slide_detrend(table: pd.DataFrame, lang: str) -> Figure:
    """Froment wallon : observé vs tendance (réponse au progrès agronomique).

    Parameters
    ----------
    table
        Table avec résidus.
    lang
        ``fr`` ou ``en``.

    Returns
    -------
    matplotlib.figure.Figure
        Deux courbes (le message est sur la slide).
    """
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8.5, 4.0))
    wheat = table[
        (table["crop_code"] == FOCUS_CROP_CODE) & (table["geo"] == WALLONIA_NUTS1)
    ].sort_values("year")
    if wheat.empty:
        fig.tight_layout()
        return fig
    ax.plot(wheat["year"], wheat["yield_t_ha"], marker="o", markersize=5, label="Observé" if lang == "fr" else "Observed")
    ax.plot(
        wheat["year"],
        wheat["yield_trend_t_ha"],
        color="0.45",
        linewidth=2,
        label="Tendance (progrès, etc.)" if lang == "fr" else "Long-term trend",
    )
    ax.set_ylabel("t/ha", fontsize=12)
    # 2024 : le creux que le brief demande de voir, pas seulement la droite.
    mark = wheat[wheat["year"] == MAP_FOCUS_YEAR]
    if not mark.empty:
        y_mark = float(mark["yield_t_ha"].iloc[0])
        ax.scatter([MAP_FOCUS_YEAR], [y_mark], s=70, color=_HEAT, zorder=5)
        ax.annotate(
            str(MAP_FOCUS_YEAR),
            (MAP_FOCUS_YEAR, y_mark),
            xytext=(-28, -18),
            textcoords="offset points",
            fontsize=11,
            color=_HEAT,
            fontweight="bold",
        )
    ax.legend(frameon=False, fontsize=11)
    _style(ax)
    _cream(fig, ax)
    fig.tight_layout()
    return fig


def plot_slide_atrisk(atypical: pd.DataFrame, years: pd.Series, lang: str) -> Figure:
    """Cultures flaggées par année (filtre rendement sous tendance + climat).

    Parameters
    ----------
    atypical
        Sortie de ``atypical_years``.
    years
        Années wallonnes à afficher (même si zéro culture flaggée).
    lang
        ``fr`` ou ``en``.

    Returns
    -------
    matplotlib.figure.Figure
        Un message : 2024 sort du lot.
    """
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(9.0, 4.0))
    if atypical.empty:
        counts = pd.Series(0, index=years, dtype=int)
    else:
        counts = atypical.groupby("year").size().reindex(years, fill_value=0)
    colors = [_HEAT if int(year) == MAP_FOCUS_YEAR else "0.45" for year in counts.index]
    ax.bar(counts.index.astype(int), counts.to_numpy(), color=colors, width=0.8)
    ax.set_ylabel("Cultures flaggées" if lang == "fr" else "Crops flagged")
    ax.set_ylim(0, max(1, int(counts.max()) + 1))
    _style(ax)
    _cream(fig, ax)
    fig.tight_layout()
    return fig


def plot_slide_mae(mae_naive: float, mae_model: float, lang: str) -> Figure:
    """Deux barres : erreur sans climat vs avec climat (froment, LOO).

    Parameters
    ----------
    mae_naive, mae_model
        MAE en t/ha.
    lang
        ``fr`` ou ``en``.

    Returns
    -------
    matplotlib.figure.Figure
        Un seul message chiffré.
    """
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    labels = (
        ["Sans le climat", "Avec le climat\n(année laissée de côté)"]
        if lang == "fr"
        else ["Without climate", "With climate\n(year left out)"]
    )
    bars = ax.bar([0, 1], [mae_naive, mae_model], color=["#9e9e9e", _RAIN], width=0.55)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(labels, fontsize=11)
    ax.set_ylabel("MAE (t/ha)", fontsize=12)
    for bar, val in zip(bars, (mae_naive, mae_model)):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.02,
            f"{val:.2f}",
            ha="center",
            va="bottom",
            fontsize=13,
        )
    ax.set_ylim(0, max(mae_naive, mae_model) * 1.25)
    _style(ax)
    _cream(fig, ax)
    fig.tight_layout()
    return fig


def run_slide_figures(
    processed_root: Path | None = None,
    figures_root: Path | None = None,
    explore_root: Path | None = None,
) -> list[Path]:
    """Écrit les PNG FR/EN et les pages d'exploration GitHub Pages.

    Parameters
    ----------
    processed_root
        ``data/processed``.
    figures_root
        ``docs/pictures/presentations``.
    explore_root
        Dossier des HTML ``explore-*.html`` (défaut : ``docs/``).

    Returns
    -------
    list of Path
        Fichiers écrits.

    Raises
    ------
    FileNotFoundError
        Si la table consolidée manque.
    """
    from agri_climat.explore import write_explore_pages
    from agri_climat.paths import docs_dir

    processed = processed_root or processed_dir()
    figures = figures_root or pictures_presentations_dir()
    csv_path = processed / "rendements_climat.csv"
    if not csv_path.exists():
        raise FileNotFoundError(csv_path)

    table = add_yield_residuals(pd.read_csv(csv_path))
    ranking = sensitivity_ranking(correlations_by_crop(table))
    atypical = atypical_years(table)
    wallonia_years = (
        table.loc[table["geo"] == WALLONIA_NUTS1, "year"].drop_duplicates().sort_values()
    )
    wheat_ml = evaluate_crop(table, FOCUS_CROP_CODE)
    mae_naive = float(wheat_ml["mae_naive"]) if pd.notna(wheat_ml["mae_naive"]) else 0.0
    mae_model = float(wheat_ml["mae_loo_multi"]) if pd.notna(wheat_ml["mae_loo_multi"]) else 0.0

    geojson: dict = {"type": "FeatureCollection", "features": []}
    geo_path = nuts_processed_path(processed)
    if geo_path.exists():
        geojson = load_nuts_geojson(geo_path)
    spearman = wheat_precip_spearman_by_province(table)

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    figures.mkdir(parents=True, exist_ok=True)
    jobs: list[tuple[str, object]] = [
        ("ranking-fr.png", lambda: plot_slide_ranking(ranking, "fr")),
        ("ranking-en.png", lambda: plot_slide_ranking(ranking, "en")),
        ("map-fr.png", lambda: plot_slide_map(geojson, spearman, "fr")),
        ("map-en.png", lambda: plot_slide_map(geojson, spearman, "en")),
        ("detrend-fr.png", lambda: plot_slide_detrend(table, "fr")),
        ("detrend-en.png", lambda: plot_slide_detrend(table, "en")),
        ("mae-fr.png", lambda: plot_slide_mae(mae_naive, mae_model, "fr")),
        ("mae-en.png", lambda: plot_slide_mae(mae_naive, mae_model, "en")),
        ("atrisk-fr.png", lambda: plot_slide_atrisk(atypical, wallonia_years, "fr")),
        ("atrisk-en.png", lambda: plot_slide_atrisk(atypical, wallonia_years, "en")),
    ]
    written: list[Path] = []
    for name, builder in jobs:
        path = figures / name
        fig = builder()
        fig.savefig(path, dpi=140, bbox_inches="tight", facecolor=fig.get_facecolor())
        plt.close(fig)
        logger.info("Écrit %s", path)
        written.append(path)

    dest = explore_root if explore_root is not None else docs_dir()
    written.extend(write_explore_pages(processed, dest))
    print("Slide figures:")
    for path in written:
        print(f"  {path}")
    return written
