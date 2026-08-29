"""Tests des figures README (backend Agg, pas de fenêtre)."""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from agri_climat.analyse import (
    add_yield_residuals,
    atypical_years,
    correlations_by_crop,
    sensitivity_ranking,
)
from agri_climat.figures import (
    README_FIGURES,
    plot_at_risk_years,
    plot_residual_vs_climate,
    plot_sensitivity_ranking,
    run_figures,
)
from tests.test_analyse import _joined_fixture


def test_ranking_a_un_axe_et_titre_anglais() -> None:
    """Le classement a un axe et un titre lisible dans le README anglais."""
    table = add_yield_residuals(_joined_fixture())
    ranking = sensitivity_ranking(correlations_by_crop(table))
    fig = plot_sensitivity_ranking(ranking)
    assert len(fig.axes) >= 1
    assert "Walloon crops" in fig.axes[0].get_title()
    plt.close(fig)


def test_nuages_une_facette_par_culture() -> None:
    """Autant de facettes visibles que de cultures classées."""
    table = add_yield_residuals(_joined_fixture())
    ranking = sensitivity_ranking(correlations_by_crop(table))
    fig = plot_residual_vs_climate(table, ranking)
    visible = [ax for ax in fig.axes if ax.get_visible()]
    assert len(visible) == len(ranking)
    titles = " ".join(ax.get_title() for ax in visible)
    assert "Wheat and spelt" in titles
    plt.close(fig)


def test_annees_a_risque_deux_panneaux() -> None:
    """Climat en haut, décompte des cultures flaggées en bas."""
    table = add_yield_residuals(_joined_fixture())
    atypical = atypical_years(table)
    fig = plot_at_risk_years(table, atypical)
    assert len(fig.axes) == 2
    plt.close(fig)


def test_run_figures_ecrit_trois_png(tmp_path) -> None:
    """Les trois PNG README sont écrits (taille > 0)."""
    processed = tmp_path / "processed"
    figures = tmp_path / "readme"
    processed.mkdir()
    _joined_fixture().to_csv(processed / "rendements_climat.csv", index=False)
    written = run_figures(processed, figures)
    assert [path.name for path in written] == list(README_FIGURES)
    for path in written:
        assert path.exists() and path.stat().st_size > 0
