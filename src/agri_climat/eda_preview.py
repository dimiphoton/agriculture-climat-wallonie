"""Aperçu EDA sans fenêtre Tk (``plt.show()`` bloque souvent sous Windows)."""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd
from matplotlib.figure import Figure

from agri_climat.data.join import (
    climate_extremes,
    coverage_by_crop_geo,
    missingness,
    yield_summary_by_crop,
)
from agri_climat.paths import processed_dir, repo_root

logger = logging.getLogger(__name__)


def load_joined_table() -> pd.DataFrame:
    """Charge ``rendements_climat.csv``.

    Returns
    -------
    pandas.DataFrame
        Table consolidée.

    Raises
    ------
    FileNotFoundError
        Si ``python -m agri_climat join`` n'a pas encore été lancé.
    """
    csv_path = processed_dir() / "rendements_climat.csv"
    if not csv_path.exists():
        raise FileNotFoundError(csv_path)
    return pd.read_csv(csv_path)


def plot_wheat_vs_precip_z(joined: pd.DataFrame) -> Figure:
    """Rendement froment wallon et z-score de pluie en saison.

    Parameters
    ----------
    joined
        Table consolidée.

    Returns
    -------
    matplotlib.figure.Figure
        Figure à afficher ou à enregistrer.
    """
    import matplotlib.pyplot as plt

    wallonie = joined[joined["geo"] == "BE3"]
    climat = wallonie.drop_duplicates(subset=["year"]).sort_values("year")
    froment = wallonie[wallonie["crop_code"] == "C1110"].sort_values("year")
    fig, axes = plt.subplots(2, 1, figsize=(8, 6), sharex=True)
    axes[0].plot(froment["year"], froment["yield_t_ha"], marker="o")
    axes[0].set_ylabel("Rendement froment (t/ha)")
    axes[1].bar(climat["year"], climat["precip_growing_mm_z"], color="steelblue")
    axes[1].axhline(0, color="black", linewidth=0.8)
    axes[1].set_ylabel("Pluie saison (z-score)")
    axes[1].set_xlabel("Année")
    fig.tight_layout()
    return fig


def run_eda_preview(figure_path: Path | None = None) -> Path:
    """Affiche les tableaux EDA dans le terminal et enregistre le graphique.

    Parameters
    ----------
    figure_path
        PNG de sortie ; défaut ``pictures/experiments/eda-froment-pluie-saison.png``.

    Returns
    -------
    Path
        Chemin du PNG écrit.
    """
    joined = load_joined_table()
    print(f"Lignes : {len(joined)}")
    print("\n--- Couverture (années) ---")
    print(coverage_by_crop_geo(joined).to_string())
    print("\n--- Rendements Wallonie (t/ha) ---")
    print(yield_summary_by_crop(joined).to_string(index=False))
    print("\n--- Extrêmes climatiques BE3 ---")
    print(climate_extremes(joined).to_string(index=False))
    missing = missingness(joined)
    print("\n--- Manquants ---")
    print("(aucun)" if missing.empty else missing.to_string(index=False))

    if figure_path is None:
        figure_path = (
            repo_root() / "pictures" / "experiments" / "eda-froment-pluie-saison.png"
        )
    figure_path.parent.mkdir(parents=True, exist_ok=True)
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig = plot_wheat_vs_precip_z(joined)
    fig.savefig(figure_path, dpi=120)
    plt.close(fig)
    logger.info("Figure écrite : %s", figure_path)
    print(f"\nFigure : {figure_path}")
    return figure_path
