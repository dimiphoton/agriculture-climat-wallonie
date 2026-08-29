"""Dashboard Streamlit : exploration rendements × climat (Wallonie)."""

from __future__ import annotations

import pandas as pd
import streamlit as st

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
from agri_climat.settings import FOCUS_CROP_CODE, GROWING_SEASON_Z_COLS

st.set_page_config(
    page_title="Rendements wallons × climat",
    layout="wide",
)


@st.cache_data
def _bundle_parts() -> tuple:
    """Cache les tables (le GeoJSON reste un dict JSON-serializable)."""
    bundle = load_dashboard_bundle()
    return (
        bundle.table,
        bundle.ranking,
        bundle.atypical,
        bundle.ml_metrics,
        bundle.geojson,
    )


def main() -> None:
    """Construit la page : filtres, séries, classement, carte."""
    st.title("Rendements agricoles wallons et climat")
    st.warning(DISCLAIMER_FR)

    try:
        table, ranking, atypical, ml_metrics, geojson = _bundle_parts()
    except FileNotFoundError:
        st.error(
            "Table consolidée introuvable. Lancer d'abord "
            "`python -m agri_climat join` (ou `run`)."
        )
        return

    options = crop_options(table)
    if not options:
        st.error("Aucune culture dans la table Wallonie.")
        return

    labels = [label for _, label in options]
    codes_by_label = {label: code for code, label in options}
    default_ix = 0
    for i, (code, _) in enumerate(options):
        if code == FOCUS_CROP_CODE:
            default_ix = i
            break

    st.sidebar.header("Filtres")
    crop_label = st.sidebar.selectbox("Culture", labels, index=default_ix)
    crop_code = codes_by_label[crop_label]
    y_min, y_max = year_bounds(table, crop_code)
    if y_min == 0:
        st.info("Pas de rendement pour cette culture en Wallonie.")
        return
    year_range = st.sidebar.slider(
        "Période",
        min_value=y_min,
        max_value=y_max,
        value=(y_min, y_max),
    )
    climate_labels = [label for _, label in GROWING_SEASON_Z_COLS]
    climate_label = st.sidebar.selectbox(
        "Variable climatique (carte Spearman)",
        climate_labels,
        index=1 if len(climate_labels) > 1 else 0,
    )
    climate_var = next(col for col, lab in GROWING_SEASON_Z_COLS if lab == climate_label)
    map_mode = st.sidebar.radio(
        "Carte provinciale",
        ("Spearman (toute la série)", "Résidu d'une année"),
    )
    map_year = st.sidebar.selectbox(
        "Année (résidu)",
        list(range(year_range[0], year_range[1] + 1)),
        index=year_range[1] - year_range[0],
    )

    panel = filter_wallonia_crop(table, crop_code, year_range[0], year_range[1])

    wheat_ml = ml_metrics[ml_metrics["crop_code"] == crop_code]
    cols = st.columns(3)
    cols[0].metric("Années (filtre)", len(panel))
    if not ranking.empty:
        crop_rank = ranking[ranking["crop_label"] == crop_label]
        if not crop_rank.empty:
            rho = crop_rank.iloc[0]["spearman_r"]
            clim = crop_rank.iloc[0]["climate_label"]
            cols[1].metric("Spearman max (série entière)", f"{float(rho):.2f}", clim)
    if not wheat_ml.empty and pd.notna(wheat_ml.iloc[0]["mae_loo_multi"]):
        row = wheat_ml.iloc[0]
        cols[2].metric(
            "MAE LOO / naïve",
            f"{float(row['mae_loo_multi']):.2f} / {float(row['mae_naive']):.2f} t/ha",
        )

    left, right = st.columns(2)
    with left:
        st.plotly_chart(plot_yield_series(panel, crop_label), width="stretch")
    with right:
        st.plotly_chart(plot_climate_z(panel), width="stretch")

    st.subheader("Classement de sensibilité (Wallonie, série entière)")
    st.caption(
        "Variable climatique au |Spearman| le plus fort. Le filtre d'années "
        "ci-dessus ne recalcule pas ce tableau — ce n'est pas un palmarès "
        "sur la sous-période."
    )
    if ranking.empty:
        st.info("Pas de classement.")
    else:
        show = ranking.rename(
            columns={
                "crop_label": "culture",
                "climate_label": "variable",
                "spearman_r": "spearman",
                "spearman_p": "p",
            }
        )[["culture", "n", "variable", "spearman", "p"]]
        st.dataframe(show, hide_index=True, width="stretch")

    st.subheader("Années atypiques (filtre culture + période)")
    st.caption(
        "Résidu z ≤ −1 et au moins un |z| climatique de saison ≥ 1. "
        "Filtre joint, pas un diagnostic causal."
    )
    atyp = atypical.copy()
    if not atyp.empty:
        atyp = atyp[
            (atyp["crop_label"] == crop_label)
            & (atyp["year"] >= year_range[0])
            & (atyp["year"] <= year_range[1])
        ]
    if atyp.empty:
        st.info("Aucune année ne passe le filtre pour cette sélection.")
    else:
        st.dataframe(
            atyp.rename(
                columns={
                    "year": "année",
                    "crop_label": "culture",
                    "yield_t_ha": "t/ha",
                    "yield_resid_z": "résidu z",
                    "alea": "aléa",
                }
            ),
            hide_index=True,
            width="stretch",
        )

    st.subheader("Carte des provinces (NUTS 2)")
    has_map = bool(geojson.get("features"))
    if not has_map:
        st.info(
            "GeoJSON provincial absent. Lancer `python -m agri_climat download nuts` "
            "puis `python -m agri_climat map`."
        )
    elif map_mode.startswith("Spearman"):
        values = spearman_by_province(table, crop_code, climate_var)
        fig = plot_province_choropleth(
            geojson,
            values,
            "spearman_r",
            f"{crop_label} × {climate_label} (Spearman ρ)",
            "ρ",
            zmin=-1.0,
            zmax=1.0,
        )
        st.plotly_chart(fig, width="stretch")
    else:
        values = residual_z_by_province(table, crop_code, int(map_year))
        fig = plot_province_choropleth(
            geojson,
            values,
            "yield_resid_z",
            f"{crop_label} — résidu {map_year} (z)",
            "z",
            zmin=-2.5,
            zmax=2.5,
        )
        st.plotly_chart(fig, width="stretch")


if __name__ == "__main__":
    main()
