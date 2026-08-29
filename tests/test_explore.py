"""Pages d'exploration HTML (lien depuis les slides)."""

from agri_climat.analyse import add_yield_residuals
from agri_climat.explore import plot_explore_yields, write_explore_pages
from tests.test_analyse import _joined_fixture


def test_explore_html_menu_cultures(tmp_path) -> None:
    """HTML FR/EN avec le menu de cultures et Plotly."""
    processed = tmp_path / "processed"
    processed.mkdir()
    add_yield_residuals(_joined_fixture()).to_csv(
        processed / "rendements_climat.csv", index=False
    )
    written = write_explore_pages(processed, tmp_path / "pages")
    names = {path.name for path in written}
    assert names == {"explore-fr.html", "explore-en.html"}
    fr = (tmp_path / "pages" / "explore-fr.html").read_text(encoding="utf-8")
    assert "plotly" in fr.lower()
    assert "Froment" in fr
    assert "causalité" in fr


def test_explore_yields_dropdown() -> None:
    """Une paire de traces par culture, froment visible."""
    table = add_yield_residuals(_joined_fixture())
    fig = plot_explore_yields(table, "fr")
    assert fig.layout.updatemenus
    visibles = [tr.visible for tr in fig.data]
    assert True in visibles
