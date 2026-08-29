"""Pages HTML autonomes : explorer les séries depuis les slides (GitHub Pages)."""

from __future__ import annotations

import html
import logging
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from plotly.graph_objects import Figure

from agri_climat.dashboard import (
    crop_options,
    filter_wallonia_crop,
    load_dashboard_bundle,
    year_bounds,
)
from agri_climat.paths import docs_dir, processed_dir
from agri_climat.settings import (
    CLIMATE_EXTREME_ABS_Z,
    CLIMATE_LABELS_EN,
    CROP_LABELS_EN,
    CROP_LABELS_FR,
    FOCUS_CROP_CODE,
    GROWING_SEASON_Z_COLS,
    WALLONIA_NUTS1,
)

logger = logging.getLogger(__name__)

_CLIMATE_COLORS: dict[str, str] = {
    "température saison": "#c44e52",
    "précipitations saison": "#4c72b0",
    "ET0 saison": "#dd8452",
}

_DISCLAIMER = {
    "fr": (
        "Corrélation ≠ causalité. Prix, maladies, irrigation et variétés "
        "ne sont pas dans le modèle."
    ),
    "en": (
        "Correlation is not causation. Prices, pests, irrigation and variety "
        "changes are not in the model."
    ),
}


def _crop_label(code: str, label_fr: str, lang: str) -> str:
    if lang == "en":
        return CROP_LABELS_EN.get(code, label_fr)
    return label_fr


def plot_explore_yields(table: pd.DataFrame, lang: str) -> Figure:
    """Rendement observé + tendance, menu déroulant par culture.

    Parameters
    ----------
    table
        Table consolidée avec résidus.
    lang
        ``fr`` ou ``en``.

    Returns
    -------
    plotly.graph_objects.Figure
        Une trace visible à la fois (froment par défaut).
    """
    options = crop_options(table)
    fig = go.Figure()
    if not options:
        fig.update_layout(title="—")
        return fig

    default_ix = 0
    for i, (code, _) in enumerate(options):
        if code == FOCUS_CROP_CODE:
            default_ix = i
            break

    obs_name = "Observé" if lang == "fr" else "Observed"
    trend_name = "Tendance" if lang == "fr" else "Trend"
    for i, (code, label_fr) in enumerate(options):
        y_min, y_max = year_bounds(table, code)
        panel = filter_wallonia_crop(table, code, y_min, y_max)
        visible = i == default_ix
        fig.add_trace(
            go.Scatter(
                x=panel["year"],
                y=panel["yield_t_ha"],
                name=obs_name,
                mode="lines+markers",
                visible=visible,
                legendgroup="obs",
            )
        )
        y_trend = (
            panel["yield_trend_t_ha"]
            if "yield_trend_t_ha" in panel.columns
            else pd.Series(dtype=float)
        )
        fig.add_trace(
            go.Scatter(
                x=panel["year"],
                y=y_trend,
                name=trend_name,
                mode="lines",
                line={"dash": "dash", "color": "gray"},
                visible=visible,
                legendgroup="trend",
            )
        )

    buttons: list[dict] = []
    n = len(options)
    for i, (code, label_fr) in enumerate(options):
        visible = [False] * (2 * n)
        visible[2 * i] = True
        visible[2 * i + 1] = True
        name = _crop_label(code, label_fr, lang)
        title = f"{name} — Wallonie" if lang == "fr" else f"{name} — Wallonia"
        buttons.append(
            {
                "label": name,
                "method": "update",
                "args": [{"visible": visible}, {"title": {"text": title}}],
            }
        )

    default_name = _crop_label(
        options[default_ix][0], options[default_ix][1], lang
    )
    default_title = (
        f"{default_name} — Wallonie" if lang == "fr" else f"{default_name} — Wallonia"
    )
    fig.update_layout(
        title=default_title,
        xaxis_title="Année" if lang == "fr" else "Year",
        yaxis_title="t/ha",
        template="plotly_white",
        legend={"orientation": "h", "y": 1.18},
        margin={"l": 40, "r": 20, "t": 80, "b": 40},
        updatemenus=[
            {
                "buttons": buttons,
                "direction": "down",
                "x": 0,
                "xanchor": "left",
                "y": 1.28,
                "yanchor": "top",
                "showactive": True,
                "active": default_ix,
            }
        ],
    )
    fig.update_xaxes(rangeslider_visible=True)
    return fig


def plot_explore_climate(table: pd.DataFrame, lang: str) -> Figure:
    """Z-scores de saison wallons (identiques pour toutes les cultures).

    Parameters
    ----------
    table
        Table consolidée.
    lang
        ``fr`` ou ``en``.

    Returns
    -------
    plotly.graph_objects.Figure
        Trois courbes.
    """
    climate = (
        table[table["geo"] == WALLONIA_NUTS1]
        .drop_duplicates(subset=["year"])
        .sort_values("year")
    )
    fig = go.Figure()
    for col, label_fr in GROWING_SEASON_Z_COLS:
        if col not in climate.columns:
            continue
        label = CLIMATE_LABELS_EN.get(label_fr, label_fr) if lang == "en" else label_fr
        fig.add_trace(
            go.Scatter(
                x=climate["year"],
                y=climate[col],
                name=label,
                mode="lines+markers",
                line={"color": _CLIMATE_COLORS.get(label_fr, "#7f7f7f")},
            )
        )
    fig.add_hline(y=0, line_color="black", line_width=1)
    fig.add_hline(y=CLIMATE_EXTREME_ABS_Z, line_dash="dash", line_color="gray")
    fig.add_hline(y=-CLIMATE_EXTREME_ABS_Z, line_dash="dash", line_color="gray")
    fig.update_layout(
        title=(
            "Climat de saison (z-scores, avril–septembre)"
            if lang == "fr"
            else "Growing-season climate (z-scores, April–September)"
        ),
        xaxis_title="Année" if lang == "fr" else "Year",
        yaxis_title="z-score",
        template="plotly_white",
        legend={"orientation": "h", "y": 1.12},
        margin={"l": 40, "r": 20, "t": 60, "b": 40},
    )
    return fig


def _ranking_table_html(ranking: pd.DataFrame, lang: str) -> str:
    """Tableau HTML du classement Spearman (série entière)."""
    if ranking.empty:
        return "<p>—</p>"
    rows = ["<table><thead><tr>"]
    headers = (
        ("Culture", "Variable", "Spearman ρ", "n")
        if lang == "fr"
        else ("Crop", "Variable", "Spearman ρ", "n")
    )
    for h in headers:
        rows.append(f"<th>{h}</th>")
    rows.append("</tr></thead><tbody>")
    for row in ranking.itertuples(index=False):
        crop = str(row.crop_label)
        for code, label_fr in CROP_LABELS_FR.items():
            if label_fr == str(row.crop_label):
                crop = _crop_label(code, label_fr, lang)
                break
        var = str(row.climate_label)
        if lang == "en":
            var = CLIMATE_LABELS_EN.get(var, var)
        rho = float(row.spearman_r)
        n = int(row.n)
        rows.append(
            "<tr>"
            f"<td>{html.escape(crop)}</td>"
            f"<td>{html.escape(var)}</td>"
            f"<td>{rho:.2f}</td>"
            f"<td>{n}</td>"
            "</tr>"
        )
    rows.append("</tbody></table>")
    return "".join(rows)


def _page_html(
    lang: str,
    yield_fig: Figure,
    climate_fig: Figure,
    ranking_html: str,
) -> str:
    """Assemble une page autonome (Plotly via CDN)."""
    yield_div = yield_fig.to_html(include_plotlyjs="cdn", full_html=False)
    climate_div = climate_fig.to_html(include_plotlyjs=False, full_html=False)
    if lang == "fr":
        title = "Explorer — rendements wallons × climat"
        heading = "Rendements agricoles wallons et climat"
        nav_home = "Accueil"
        nav_slides = "Présentation"
        slides_href = "slides/presentation-recruteur-fr.html"
        rank_title = "Classement de sensibilité (Wallonie, série entière)"
        lang_switch = '<a href="explore-en.html">EN</a>'
    else:
        title = "Explore — Walloon yields × climate"
        heading = "Walloon crop yields and climate"
        nav_home = "Home"
        nav_slides = "Slides"
        slides_href = "slides/presentation-recruteur-en.html"
        rank_title = "Sensitivity ranking (Wallonia, full series)"
        lang_switch = '<a href="explore-fr.html">FR</a>'

    disclaimer = html.escape(_DISCLAIMER[lang])
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>
    body {{ font-family: system-ui, sans-serif; max-width: 1100px;
           margin: 1.5rem auto; padding: 0 1rem; color: #1a1a1a; }}
    nav {{ margin-bottom: 1rem; font-size: 0.95rem; }}
    nav a {{ margin-right: 1.1rem; }}
    .note {{ background: #fff8e1; padding: 0.75rem 1rem; border-radius: 6px; }}
    table {{ border-collapse: collapse; width: 100%; margin: 0.5rem 0 2rem; }}
    th, td {{ border-bottom: 1px solid #ddd; padding: 0.4rem 0.5rem; text-align: left; }}
    h1 {{ font-size: 1.6rem; margin-bottom: 0.4rem; }}
  </style>
</head>
<body>
  <nav>
    <a href="index.html">{nav_home}</a>
    <a href="{slides_href}">{nav_slides}</a>
    {lang_switch}
  </nav>
  <h1>{html.escape(heading)}</h1>
  <p class="note">{disclaimer}</p>
  {yield_div}
  {climate_div}
  <h2>{html.escape(rank_title)}</h2>
  {ranking_html}
</body>
</html>
"""


def write_explore_pages(
    processed_root: Path | None = None,
    output_root: Path | None = None,
) -> list[Path]:
    """Écrit ``explore-fr.html`` et ``explore-en.html`` (GitHub Pages).

    Parameters
    ----------
    processed_root
        ``data/processed``.
    output_root
        Dossier de sortie (défaut : ``docs/``).

    Returns
    -------
    list of Path
        Les deux fichiers écrits.

    Raises
    ------
    FileNotFoundError
        Si la table consolidée manque.
    """
    bundle = load_dashboard_bundle(processed_root or processed_dir())
    dest = output_root or docs_dir()
    dest.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for lang in ("fr", "en"):
        page = _page_html(
            lang,
            plot_explore_yields(bundle.table, lang),
            plot_explore_climate(bundle.table, lang),
            _ranking_table_html(bundle.ranking, lang),
        )
        path = dest / f"explore-{lang}.html"
        path.write_text(page, encoding="utf-8")
        logger.info("Écrit %s", path)
        written.append(path)
    return written
