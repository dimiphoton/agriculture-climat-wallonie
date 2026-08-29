"""Figures polies pour le README (anglais) : ranking, nuages, années à risque."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure

from agri_climat.analyse import (
    add_yield_residuals,
    atypical_years,
    correlations_by_crop,
    sensitivity_ranking,
)
from agri_climat.paths import pictures_readme_dir, processed_dir
from agri_climat.settings import (
    CLIMATE_EXTREME_ABS_Z,
    CLIMATE_LABELS_EN,
    CROP_LABELS_EN,
    CROP_LABELS_FR,
    GROWING_SEASON_Z_COLS,
    WALLONIA_NUTS1,
)

logger = logging.getLogger(__name__)

# Couleurs stables par type d'aléa (même teinte dans les trois figures).
_CLIMATE_COLORS: dict[str, str] = {
    "température saison": "#c44e52",
    "précipitations saison": "#4c72b0",
    "ET0 saison": "#dd8452",
}

README_FIGURES: tuple[str, ...] = (
    "crop-sensitivity-ranking.png",
    "yield-residual-vs-climate.png",
    "at-risk-years.png",
)

_FR_LABEL_TO_CODE: dict[str, str] = {label: code for code, label in CROP_LABELS_FR.items()}
_CLIMATE_LABEL_TO_COL: dict[str, str] = {
    label: col for col, label in GROWING_SEASON_Z_COLS
}


def _crop_label_en(fr_label: str) -> str:
    """Traduit un libellé culture FR vers l'anglais du README."""
    code = _FR_LABEL_TO_CODE.get(fr_label)
    if code is None:
        return fr_label
    return CROP_LABELS_EN.get(code, fr_label)


def _climate_label_en(fr_label: str) -> str:
    """Traduit un libellé climatique FR vers l'anglais du README."""
    return CLIMATE_LABELS_EN.get(fr_label, fr_label)


def _style_ax(ax: Axes) -> None:
    """Retire les bordures haut / droite (lecture plus claire)."""
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def plot_sensitivity_ranking(ranking: pd.DataFrame) -> Figure:
    """Barres horizontales : Spearman par culture (variable au |ρ| max).

    Parameters
    ----------
    ranking
        Sortie de ``sensitivity_ranking`` (Wallonie).

    Returns
    -------
    matplotlib.figure.Figure
        Une barre par culture, colorée selon la variable climatique.
    """
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    if ranking.empty:
        ax.set_title("No ranking available")
        _style_ax(ax)
        fig.tight_layout()
        return fig

    work = ranking.copy()
    work["abs_spearman"] = work["spearman_r"].abs()
    work = work.sort_values("abs_spearman", ascending=True)
    colors = [
        _CLIMATE_COLORS.get(str(label), "#7f7f7f") for label in work["climate_label"]
    ]
    y_pos = np.arange(len(work))
    ax.barh(y_pos, work["spearman_r"], color=colors, height=0.7)
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_yticks(y_pos)
    ax.set_yticklabels([_crop_label_en(str(label)) for label in work["crop_label"]])
    ax.set_title("Which Walloon crops track climate variability? (2000–2024)")
    ax.set_xlim(-1.05, 1.05)
    _style_ax(ax)

    for i, row in enumerate(work.itertuples(index=False)):
        star = "*" if bool(row.signif_5pct) else ""
        ax.text(
            float(row.spearman_r) + (0.04 if float(row.spearman_r) >= 0 else -0.04),
            i,
            f"{float(row.spearman_r):.2f}{star}",
            va="center",
            ha="left" if float(row.spearman_r) >= 0 else "right",
            fontsize=8,
        )

    # Légende : une entrée par variable climatique présente.
    from matplotlib.patches import Patch

    seen: list[str] = []
    handles: list[Patch] = []
    for fr_label in work["climate_label"]:
        key = str(fr_label)
        if key in seen:
            continue
        seen.append(key)
        handles.append(
            Patch(facecolor=_CLIMATE_COLORS.get(key, "#7f7f7f"), label=_climate_label_en(key))
        )
    ax.legend(
        handles=handles,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.22),
        ncol=max(1, len(handles)),
        fontsize=8,
        frameon=False,
    )
    ax.set_xlabel("Spearman ρ (yield residual vs growing-season z-score)  * p < 0.05")
    fig.tight_layout()
    return fig


def plot_residual_vs_climate(
    table: pd.DataFrame,
    ranking: pd.DataFrame,
) -> Figure:
    """Nuages comparatifs : résidu de rendement vs z-score climatique dominant.

    Parameters
    ----------
    table
        Table consolidée avec résidus.
    ranking
        Une ligne par culture (variable au |Spearman| max).

    Returns
    -------
    matplotlib.figure.Figure
        Une facette par culture.
    """
    import matplotlib.pyplot as plt

    n = len(ranking)
    if n == 0:
        fig, ax = plt.subplots(figsize=(6, 3))
        ax.set_title("No crops to plot")
        _style_ax(ax)
        fig.tight_layout()
        return fig

    ncols = min(4, n)
    nrows = int(np.ceil(n / ncols))
    fig, axes = plt.subplots(
        nrows,
        ncols,
        figsize=(3.1 * ncols, 2.8 * nrows),
        squeeze=False,
    )
    work = table[table["geo"] == WALLONIA_NUTS1].copy()
    if "yield_resid_z" not in work.columns:
        work = add_yield_residuals(work)
        work = work[work["geo"] == WALLONIA_NUTS1]

    for i, row in enumerate(ranking.itertuples(index=False)):
        ax = axes[i // ncols][i % ncols]
        climate_col = _CLIMATE_LABEL_TO_COL.get(str(row.climate_label))
        crop_df = work[work["crop_label"] == row.crop_label]
        color = _CLIMATE_COLORS.get(str(row.climate_label), "#7f7f7f")
        if climate_col is None or crop_df.empty:
            ax.set_title(_crop_label_en(str(row.crop_label)))
            _style_ax(ax)
            continue
        x = crop_df[climate_col].astype(float)
        y = crop_df["yield_resid_z"].astype(float)
        mask = x.notna() & y.notna()
        ax.scatter(x[mask], y[mask], c=color, s=22, alpha=0.8, edgecolors="none")
        # Droite de tendance visuelle (degré 1), pas un modèle causal.
        if int(mask.sum()) >= 3:
            fit = np.polyfit(x[mask].to_numpy(), y[mask].to_numpy(), 1)
            x_line = np.linspace(float(x[mask].min()), float(x[mask].max()), 40)
            ax.plot(x_line, np.polyval(fit, x_line), color="0.35", linewidth=1.2)
        ax.axhline(0, color="black", linewidth=0.5)
        ax.axvline(0, color="black", linewidth=0.5)
        rho = float(row.spearman_r)
        ax.set_title(
            f"{_crop_label_en(str(row.crop_label))}\n"
            f"ρ = {rho:.2f} ({_climate_label_en(str(row.climate_label))})",
            fontsize=9,
        )
        _style_ax(ax)

    for j in range(n, nrows * ncols):
        axes[j // ncols][j % ncols].set_visible(False)

    fig.supxlabel("Growing-season climate z-score", fontsize=10)
    fig.supylabel("Yield residual (z)", fontsize=10)
    fig.suptitle(
        "Yield residual vs the climate signal each crop tracks most closely",
        fontsize=11,
    )
    fig.tight_layout()
    return fig


def plot_at_risk_years(
    table: pd.DataFrame,
    atypical: pd.DataFrame,
) -> Figure:
    """Série climatique wallonne et nombre de cultures flaggées par année.

    Parameters
    ----------
    table
        Table consolidée (climat de saison identique pour toutes les cultures).
    atypical
        Sortie de ``atypical_years`` (Wallonie).

    Returns
    -------
    matplotlib.figure.Figure
        Deux panneaux : z-scores climatiques, puis décompte des cultures.
    """
    import matplotlib.pyplot as plt

    wallonia = table[table["geo"] == WALLONIA_NUTS1]
    climat = wallonia.drop_duplicates(subset=["year"]).sort_values("year")
    fig, axes = plt.subplots(
        2,
        1,
        figsize=(9.0, 5.6),
        sharex=True,
        gridspec_kw={"height_ratios": [2.2, 1.0]},
    )
    axes[0].plot(
        climat["year"],
        climat["temp_mean_growing_c_z"],
        color=_CLIMATE_COLORS["température saison"],
        label="temperature",
        marker="o",
        markersize=3,
    )
    axes[0].plot(
        climat["year"],
        climat["precip_growing_mm_z"],
        color=_CLIMATE_COLORS["précipitations saison"],
        label="rainfall",
        marker="o",
        markersize=3,
    )
    axes[0].plot(
        climat["year"],
        climat["et0_growing_mm_z"],
        color=_CLIMATE_COLORS["ET0 saison"],
        label="ET0",
        marker="o",
        markersize=3,
    )
    axes[0].axhline(0, color="black", linewidth=0.7)
    axes[0].axhline(CLIMATE_EXTREME_ABS_Z, color="0.5", linestyle="--", linewidth=0.7)
    axes[0].axhline(-CLIMATE_EXTREME_ABS_Z, color="0.5", linestyle="--", linewidth=0.7)
    axes[0].set_ylabel("Growing-season z-score")
    axes[0].set_title("Climate anomalies and years with several crops below trend")
    axes[0].legend(loc="best", fontsize=8, frameon=False, ncol=3)
    _style_ax(axes[0])

    if atypical.empty:
        counts = pd.Series(0, index=climat["year"], dtype=int)
    else:
        counts = atypical.groupby("year").size()
        counts = counts.reindex(climat["year"], fill_value=0)

    # Bandes dorées : années où au moins deux cultures passent le filtre joint.
    multi_years = [int(year) for year, n_crops in counts.items() if n_crops >= 2]
    for year in multi_years:
        axes[0].axvspan(year - 0.45, year + 0.45, color="#f4d35e", alpha=0.35, zorder=0)

    axes[1].bar(counts.index.astype(int), counts.to_numpy(), color="0.35", width=0.8)
    axes[1].set_ylabel("Crops flagged")
    axes[1].set_xlabel("Year")
    axes[1].set_ylim(0, max(1, int(counts.max()) + 1))
    _style_ax(axes[1])
    fig.tight_layout()
    return fig


def run_figures(
    processed_root: Path | None = None,
    figures_root: Path | None = None,
) -> list[Path]:
    """Génère les trois PNG du README (backend Agg, pas de fenêtre).

    Parameters
    ----------
    processed_root
        Dossier ``data/processed``. Défaut : chemins du dépôt.
    figures_root
        Dossier ``pictures/readme``. Défaut : chemins du dépôt.

    Returns
    -------
    list of Path
        Chemins des PNG écrits, dans l'ordre de ``README_FIGURES``.

    Raises
    ------
    FileNotFoundError
        Si ``rendements_climat.csv`` est absent.
    """
    processed = processed_root or processed_dir()
    figures = figures_root or pictures_readme_dir()
    csv_path = processed / "rendements_climat.csv"
    if not csv_path.exists():
        raise FileNotFoundError(csv_path)

    joined = pd.read_csv(csv_path)
    table = add_yield_residuals(joined)
    corr = correlations_by_crop(table)
    ranking = sensitivity_ranking(corr)
    atypical = atypical_years(table)

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    figures.mkdir(parents=True, exist_ok=True)
    builders = (
        lambda: plot_sensitivity_ranking(ranking),
        lambda: plot_residual_vs_climate(table, ranking),
        lambda: plot_at_risk_years(table, atypical),
    )
    written: list[Path] = []
    for name, builder in zip(README_FIGURES, builders, strict=True):
        path = figures / name
        fig = builder()
        fig.savefig(path, dpi=140, bbox_inches="tight")
        plt.close(fig)
        logger.info("Écrit %s", path)
        written.append(path)

    print("README figures:")
    for path in written:
        print(f"  {path}")
    return written
