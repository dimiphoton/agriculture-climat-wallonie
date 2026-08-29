"""Tests du dashboard (figures Plotly, sans lancer Streamlit)."""

import json

from agri_climat.analyse import add_yield_residuals
from agri_climat.dashboard import (
    DISCLAIMER_FR,
    crop_options,
    filter_wallonia_crop,
    load_dashboard_bundle,
    plot_climate_z,
    plot_province_choropleth,
    plot_yield_series,
    residual_z_by_province,
    spearman_by_province,
    year_bounds,
)
from agri_climat.data.download import nuts_processed_path
from tests.test_analyse import _joined_fixture
from tests.test_map import _fixture_geojson


def test_filtre_wallonie_borne_les_annees() -> None:
    """Le filtre ne garde que BE3 et la plage demandée."""
    table = add_yield_residuals(_joined_fixture())
    panel = filter_wallonia_crop(table, "C1110", 2012, 2015)
    assert set(panel["geo"]) == {"BE3"}
    assert panel["year"].min() >= 2012
    assert panel["year"].max() <= 2015
    assert panel["crop_code"].eq("C1110").all()


def test_bornes_et_options_froment() -> None:
    """Le froment du fixture couvre 2010–2019."""
    table = add_yield_residuals(_joined_fixture())
    y_min, y_max = year_bounds(table, "C1110")
    assert (y_min, y_max) == (2010, 2019)
    labels = [label for _, label in crop_options(table)]
    assert "Froment et épeautre" in labels


def test_spearman_provincial_froment_pluie() -> None:
    """Même signal que la carte : ρ positif en Hainaut sur le fixture."""
    table = add_yield_residuals(_joined_fixture())
    spearman = spearman_by_province(table, "C1110", "precip_growing_mm_z")
    hainaut = spearman[spearman["geo"] == "BE32"].iloc[0]
    assert hainaut["spearman_r"] > 0.95


def test_residu_provincial_annee() -> None:
    """2010 existe : une ligne Hainaut."""
    table = add_yield_residuals(_joined_fixture())
    residual = residual_z_by_province(table, "C1110", 2010)
    assert "BE32" in set(residual["geo"])


def test_figures_plotly() -> None:
    """Les figures ont des traces ; la carte utilise le GeoJSON de fixture."""
    table = add_yield_residuals(_joined_fixture())
    panel = filter_wallonia_crop(table, "C1110", 2010, 2019)
    fig_y = plot_yield_series(panel, "Froment et épeautre")
    assert len(fig_y.data) >= 2
    fig_c = plot_climate_z(panel)
    assert len(fig_c.data) >= 1
    values = spearman_by_province(table, "C1110", "precip_growing_mm_z")
    fig_m = plot_province_choropleth(
        _fixture_geojson(),
        values,
        "spearman_r",
        "test",
        "ρ",
        zmin=-1.0,
        zmax=1.0,
    )
    assert fig_m.data
    empty = plot_province_choropleth(
        {"type": "FeatureCollection", "features": []},
        values,
        "spearman_r",
        "vide",
        "ρ",
        zmin=-1.0,
        zmax=1.0,
    )
    assert "indisponible" in (empty.layout.title.text or "")


def test_disclaimer_et_load(tmp_path) -> None:
    """Le bundle se charge depuis un CSV de fixture ; fichier absent → erreur."""
    assert "causalité" in DISCLAIMER_FR
    processed = tmp_path / "processed"
    processed.mkdir()
    _joined_fixture().to_csv(processed / "rendements_climat.csv", index=False)
    geo_path = nuts_processed_path(processed)
    geo_path.write_text(json.dumps(_fixture_geojson()), encoding="utf-8")
    bundle = load_dashboard_bundle(processed)
    assert not bundle.ranking.empty
    assert bundle.geojson["features"]
    missing = tmp_path / "empty"
    missing.mkdir()
    try:
        load_dashboard_bundle(missing)
        raise AssertionError("FileNotFoundError attendu")
    except FileNotFoundError:
        pass


def test_app_streamlit_sans_exception() -> None:
    """L'app Streamlit se lance (AppTest) et affiche le garde-fou."""
    from streamlit.testing.v1 import AppTest

    from agri_climat.paths import repo_root

    at = AppTest.from_file(repo_root() / "webapp" / "app.py", default_timeout=60)
    at.run()
    assert not at.exception
    texts = " ".join(str(w.value) for w in at.warning)
    assert "causalité" in texts
    assert at.selectbox

