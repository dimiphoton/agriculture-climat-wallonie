"""Tests de l'analyse statistique (détrend, corrélations, années atypiques)."""

import numpy as np
import pandas as pd

from agri_climat.analyse import (
    add_yield_residuals,
    atypical_years,
    build_analyse_markdown,
    correlations_by_crop,
    plot_spearman_heatmap,
    plot_wheat_deep_dive,
    run_analyse,
    sensitivity_ranking,
)


def _joined_fixture() -> pd.DataFrame:
    """10 années, 2 cultures. Froment lié à la pluie ; betterave à la température."""
    years = np.arange(2010, 2020)
    # Motifs palindromes : pas de tendance linéaire vs l'année, pour que
    # l'OLS du rendement retrouve la pente 0,1 / 0,2 sans la confondre au climat.
    precip_z = np.array([-1.8, -1.2, 0.5, 1.0, 0.2, 0.2, 1.0, 0.5, -1.2, -1.8])
    temp_z = np.array([0.2, -1.5, 0.0, 1.4, -0.2, -0.2, 1.4, 0.0, -1.5, 0.2])
    et0_z = -0.5 * precip_z
    rows: list[dict[str, object]] = []
    for geo in ("BE3", "BE32"):
        for i, year in enumerate(years):
            # Résidu froment = 0,5 × z-pluie (liaison monotone par construction).
            yield_wheat = 8.0 + 0.1 * (year - 2010) + 0.5 * precip_z[i]
            rows.append(
                {
                    "year": int(year),
                    "geo": geo,
                    "geo_label": "Wallonie" if geo == "BE3" else "Hainaut",
                    "crop_code": "C1110",
                    "crop_label": "Froment et épeautre",
                    "yield_t_ha": yield_wheat,
                    "temp_mean_growing_c_z": temp_z[i],
                    "precip_growing_mm_z": precip_z[i],
                    "et0_growing_mm_z": et0_z[i],
                }
            )
            yield_beet = 70.0 + 0.2 * (year - 2010) + 0.5 * temp_z[i]
            rows.append(
                {
                    "year": int(year),
                    "geo": geo,
                    "geo_label": "Wallonie" if geo == "BE3" else "Hainaut",
                    "crop_code": "R2000",
                    "crop_label": "Betterave sucrière",
                    "yield_t_ha": yield_beet,
                    "temp_mean_growing_c_z": temp_z[i],
                    "precip_growing_mm_z": precip_z[i],
                    "et0_growing_mm_z": et0_z[i],
                }
            )
    return pd.DataFrame(rows)


def test_detrend_retrouve_la_pente() -> None:
    """La pente OLS du froment wallon est proche de +0,1 t/ha/an."""
    table = add_yield_residuals(_joined_fixture())
    wheat = table[(table["crop_code"] == "C1110") & (table["geo"] == "BE3")]
    slope = float(wheat["yield_trend_slope"].iloc[0])
    assert abs(slope - 0.1) < 0.02
    # Après détrend, le résidu suit la pluie (corrélation positive ici).
    assert wheat["yield_resid_t_ha"].corr(wheat["precip_growing_mm_z"]) > 0.99


def test_classement_froment_lie_a_la_pluie() -> None:
    """Le |Spearman| max du froment porte sur les précipitations de saison."""
    table = add_yield_residuals(_joined_fixture())
    corr = correlations_by_crop(table, geo="BE3")
    ranking = sensitivity_ranking(corr)
    wheat = ranking[ranking["crop_label"] == "Froment et épeautre"].iloc[0]
    assert wheat["climate_label"] == "précipitations saison"
    assert wheat["spearman_r"] > 0.95
    beet = ranking[ranking["crop_label"] == "Betterave sucrière"].iloc[0]
    assert beet["climate_label"] == "température saison"


def test_annee_seche_froment_flaggee() -> None:
    """2010 (pluie z = -1,8) est atypique pour le froment, pas la betterave."""
    table = add_yield_residuals(_joined_fixture())
    flagged = atypical_years(table, geo="BE3")
    wheat_2010 = flagged[
        (flagged["year"] == 2010) & (flagged["crop_label"] == "Froment et épeautre")
    ]
    assert len(wheat_2010) == 1
    assert "sec" in wheat_2010.iloc[0]["alea"]
    beet_2010 = flagged[
        (flagged["year"] == 2010) & (flagged["crop_label"] == "Betterave sucrière")
    ]
    assert beet_2010.empty


def test_rapport_rappelle_la_causalite() -> None:
    """Le markdown contient le classement et le garde-fou causalité."""
    table = add_yield_residuals(_joined_fixture())
    corr = correlations_by_crop(table)
    ranking = sensitivity_ranking(corr)
    atypical = atypical_years(table)
    # Robustesse : une seule province dans le fixture hors BE3 — tableau quand même.
    from agri_climat.analyse import provincial_robustness

    robust = provincial_robustness(table)
    text = build_analyse_markdown(ranking, corr, atypical, robust, table)
    assert "Froment et épeautre" in text
    assert "causalité" in text
    assert "Spearman" in text
    assert "Lecture" in text


def test_figures_et_run_analyse(tmp_path) -> None:
    """PNG et rapport écrits sans fenêtre graphique."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    table = add_yield_residuals(_joined_fixture())
    corr = correlations_by_crop(table)
    fig_h = plot_spearman_heatmap(corr)
    assert fig_h.axes
    fig_w = plot_wheat_deep_dive(table)
    assert len(fig_w.axes) == 3
    plt.close(fig_h)
    plt.close(fig_w)

    processed = tmp_path / "processed"
    docs = tmp_path / "docs"
    figures = tmp_path / "figures"
    processed.mkdir()
    _joined_fixture().to_csv(processed / "rendements_climat.csv", index=False)
    report = run_analyse(processed, docs, figures)
    assert report.exists()
    assert (processed / "correlations.csv").exists()
    assert (processed / "annees_atypiques.csv").exists()
    assert (figures / "corr-spearman-wallonie.png").stat().st_size > 0
    assert (figures / "froment-detrend-climat.png").stat().st_size > 0
