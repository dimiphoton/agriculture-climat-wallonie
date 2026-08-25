"""Paramètres du pipeline d'acquisition (pas de secrets, tout est public)."""

from dataclasses import dataclass

# Période commune rendements × climat (Eurostat régional s'arrête en 2024).
START_YEAR = 2000
END_YEAR = 2024

EUROSTAT_DATASET = "apro_cpshr"
EUROSTAT_SDMX_URL = (
    "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/"
    "{dataset}/{key}?format=TSV"
)

# Codes cultures Eurostat (humidité standard UE). C1111 (froment d'hiver) est
# volontairement omis : série plus courte et doublon partiel de C1110.
CROP_LABELS_FR: dict[str, str] = {
    "C1110": "Froment et épeautre",
    "C1300": "Orge",
    "C1310": "Orge d'hiver",
    "C1500": "Maïs grain",
    "G3000": "Maïs fourrager",
    "R1000": "Pomme de terre",
    "R2000": "Betterave sucrière",
    "I1110": "Colza",
}

GEO_LABELS_FR: dict[str, str] = {
    "BE3": "Wallonie",
    "BE31": "Brabant wallon",
    "BE32": "Hainaut",
    "BE33": "Liège",
    "BE34": "Luxembourg",
    "BE35": "Namur",
}

WALLONIA_NUTS1 = "BE3"
PROVINCE_CODES: tuple[str, ...] = ("BE31", "BE32", "BE33", "BE34", "BE35")

# Bornes généreuses (t/ha) pour détecter les ruptures d'unité Eurostat
# (ex. production wallonne 2011 du froment à 1,17 kt au lieu de ~1 100 kt).
YIELD_BOUNDS_T_HA: dict[str, tuple[float, float]] = {
    "C1110": (2.0, 15.0),
    "C1300": (2.0, 12.0),
    "C1310": (2.0, 12.0),
    "C1500": (3.0, 16.0),
    "G3000": (20.0, 70.0),
    "R1000": (15.0, 80.0),
    "R2000": (40.0, 130.0),
    "I1110": (1.0, 8.0),
}

OPEN_METEO_ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
OPEN_METEO_DAILY_VARS = (
    "temperature_2m_mean",
    "temperature_2m_max",
    "precipitation_sum",
    "et0_fao_evapotranspiration",
)
GROWING_SEASON_MONTHS: tuple[int, ...] = (4, 5, 6, 7, 8, 9)

HTTP_TIMEOUT_S = 60
HTTP_USER_AGENT = "agriculture-climat-wallonie/0.1 (portfolio; pandas pipeline)"


@dataclass(frozen=True)
class ClimatePoint:
    """Point représentatif d'une province wallonne (centroïde approximatif)."""

    code: str
    label: str
    latitude: float
    longitude: float


CLIMATE_POINTS: tuple[ClimatePoint, ...] = (
    ClimatePoint("BE31", "Brabant wallon", 50.67, 4.53),
    ClimatePoint("BE32", "Hainaut", 50.45, 3.95),
    ClimatePoint("BE33", "Liège", 50.63, 5.57),
    ClimatePoint("BE34", "Luxembourg", 49.93, 5.53),
    ClimatePoint("BE35", "Namur", 50.47, 4.87),
)
