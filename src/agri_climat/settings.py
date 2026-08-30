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

# Libellés anglais : figures du README et pages d'exploration.
CROP_LABELS_EN: dict[str, str] = {
    "C1110": "Wheat and spelt",
    "C1300": "Barley",
    "C1310": "Winter barley",
    "C1500": "Grain maize",
    "G3000": "Fodder maize",
    "R1000": "Potato",
    "R2000": "Sugar beet",
    "I1110": "Rapeseed",
}

# Site GitHub Pages (dossier ``docs/`` sur ``main``).
PAGES_BASE_URL = "https://dimiphoton.github.io/agriculture-climat-wallonie"

CLIMATE_LABELS_EN: dict[str, str] = {
    "température saison": "seasonal temperature",
    "précipitations saison": "seasonal rainfall",
    "ET0 saison": "seasonal ET0",
}

GEO_LABELS_FR: dict[str, str] = {
    "BE3": "Wallonie",
    "BE31": "Brabant wallon",
    "BE32": "Hainaut",
    "BE33": "Liège",
    "BE34": "Luxembourg",
    "BE35": "Namur",
}

# Libellés courts pour la carte README (anglais).
GEO_LABELS_EN: dict[str, str] = {
    "BE3": "Wallonia",
    "BE31": "W. Brabant",
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

# Seuils journaliers (doivent rester alignés avec sql/schema.sql).
HOT_DAY_TMAX_C = 25.0
WET_DAY_MM = 10.0
DRY_DAY_MM = 1.0

# Variables climatiques annuelles (hors identifiants) pour anomalies / z-scores.
# Référence = moyenne 2000–2024 calculée séparément pour chaque ``geo``.
CLIMATE_ANNUAL_VALUE_COLS: tuple[str, ...] = (
    "temp_mean_c",
    "precip_mm",
    "et0_mm",
    "temp_mean_growing_c",
    "precip_growing_mm",
    "et0_growing_mm",
)

# Feature 3 : z-scores de saison (avril–septembre) utilisés pour les corrélations.
GROWING_SEASON_Z_COLS: tuple[tuple[str, str], ...] = (
    ("temp_mean_growing_c_z", "température saison"),
    ("precip_growing_mm_z", "précipitations saison"),
    ("et0_growing_mm_z", "ET0 saison"),
)
FOCUS_CROP_CODE = "C1110"  # froment et épeautre
MIN_OBS_CORR = 8
# Feature 6 : 3 prédicteurs climatiques ; n trop petit → coefficients instables.
MIN_OBS_ML = 10
# Carte : année atypique déjà mise en avant dans l'analyse (Feature 3–4).
MAP_FOCUS_YEAR = 2024
MAP_FOCUS_CLIMATE_VAR = "precip_growing_mm_z"
# Polygones NUTS 2, 1:10 million, WGS84 — source Eurostat GISCO.
GISCO_NUTS2_URL = (
    "https://gisco-services.ec.europa.eu/distribution/v2/nuts/geojson/"
    "NUTS_RG_10M_2021_4326_LEVL_2.geojson"
)
# Année atypique : résidu de rendement ≤ −1 σ et au moins un |z| climatique ≥ 1.
YIELD_RESID_Z_MAX = -1.0
CLIMATE_EXTREME_ABS_Z = 1.0

HTTP_TIMEOUT_S = 60
HTTP_USER_AGENT = "agriculture-climat-wallonie/0.1 (portfolio; duckdb pipeline)"


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
