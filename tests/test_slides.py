"""Tests des figures de slides (un message par PNG)."""

from agri_climat.analyse import add_yield_residuals, correlations_by_crop, sensitivity_ranking
from agri_climat.slides import (
    plot_slide_detrend,
    plot_slide_mae,
    plot_slide_ranking,
    run_slide_figures,
)
from tests.test_analyse import _joined_fixture
from tests.test_map import _fixture_geojson


def test_ranking_cinq_barres_max() -> None:
    """Au plus cinq cultures, titre en français."""
    table = add_yield_residuals(_joined_fixture())
    ranking = sensitivity_ranking(correlations_by_crop(table))
    fig = plot_slide_ranking(ranking, "fr")
    assert "froment" in (fig.axes[0].get_title() or "").lower()
    assert len(fig.axes[0].patches) <= 7  # barres + éventuels extra


def test_mae_deux_barres() -> None:
    """Exactement deux barres : naïve vs modèle."""
    fig = plot_slide_mae(0.51, 0.38, "en")
    assert "Wheat" in (fig.axes[0].get_title() or "")
    assert len(fig.axes[0].patches) == 2


def test_detrend_et_run(tmp_path) -> None:
    """PNG FR/EN écrits sans fenêtre."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    table = add_yield_residuals(_joined_fixture())
    fig = plot_slide_detrend(table, "fr")
    assert fig.axes
    plt.close(fig)

    processed = tmp_path / "processed"
    figures = tmp_path / "slides"
    processed.mkdir()
    from agri_climat.data.download import nuts_processed_path
    import json

    _joined_fixture().to_csv(processed / "rendements_climat.csv", index=False)
    nuts_processed_path(processed).write_text(
        json.dumps(_fixture_geojson()), encoding="utf-8"
    )
    written = run_slide_figures(processed, figures, explore_root=tmp_path / "pages")
    names = {path.name for path in written}
    assert "ranking-fr.png" in names
    assert "mae-en.png" in names
    assert "explore-fr.html" in names
    assert all(path.stat().st_size > 0 for path in written)
