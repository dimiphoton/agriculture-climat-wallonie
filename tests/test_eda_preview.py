"""Test du graphe EDA (backend sans fenêtre)."""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from agri_climat.data.join import join_rendements_climat
from agri_climat.eda_preview import plot_wheat_vs_precip_z
from tests.test_join import _climat, _rendements


def test_graphique_deux_axes_et_png(tmp_path) -> None:
    """Deux panneaux ; savefig écrit un fichier (pas de plt.show)."""
    joined = join_rendements_climat(_rendements(), _climat())
    fig = plot_wheat_vs_precip_z(joined)
    assert len(fig.axes) == 2
    png = tmp_path / "out.png"
    fig.savefig(png, dpi=80)
    plt.close(fig)
    assert png.exists() and png.stat().st_size > 0
