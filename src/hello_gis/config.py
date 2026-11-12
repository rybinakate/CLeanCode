"""
Централизованная конфигурация проекта Hello-GIS.
Все магические числа, пути и параметры — только здесь.

💡 Чтобы сменить регион исследования, измените только:
   - QUERY_BBOX (координаты области)
   - OSM_TAGS (тип фич для поиска)
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Final


# ============================================================
# 📂 ПУТИ К ДАННЫМ И ВЫХОДАМ
# ============================================================
BASE_DIR: Final[Path] = Path(__file__).parent.parent.parent  # корень проекта hello-gis/
DATA_RAW_DIR: Final[Path] = BASE_DIR / "data" / "raw"
OUTPUTS_DIR: Final[Path] = BASE_DIR / "outputs"

PARKS_RAW_PATH: Final[Path] = DATA_RAW_DIR / "parks.geojson"  # было madrid_parks.geojson
MAP_OUTPUT: Final[Path] = OUTPUTS_DIR / "parks_map.png"
STATS_OUTPUT: Final[Path] = OUTPUTS_DIR / "parks_stats.png"


# ============================================================
# 🌍 ГЕОПРОСТРАНСТВЕННЫЕ ПАРАМЕТРЫ
# ============================================================
# ⚠️ Измените эти координаты для другого региона!
QUERY_BBOX: Final[tuple[float, float, float, float]] = (-3.89, 40.31, -3.52, 40.64)

OSM_TAGS: Final[dict] = {
    "leisure": ["park", "nature_reserve", "recreation_ground"],
    "landuse": ["forest", "recreation_ground", "grass", "meadow"],
}

CRS_GEO: Final[str] = "EPSG:4326"
CRS_WEB: Final[str] = "EPSG:3857"
CRS_LOCAL: Final[str] = "EPSG:25830"  # UTM zone 30N (для Испании). Для другого региона — своя зона

MAP_BUFFER_RATIO: Final[float] = 0.20
GRID_LONS: Final[list[float]] = [-3.8, -3.7, -3.6, -3.5]
GRID_LATS: Final[list[float]] = [40.3, 40.4, 40.5]

 #============================================================
# 🏙️ ПАРАМЕТРЫ ГРАНИЦЫ ГОРОДА (для обрезки / Clip)
# ============================================================
CITY_NAME: Final[str] = "Madrid"
CITY_BOUNDARY_TAGS: Final[dict[str, str]] = {
    "boundary": "administrative",
    "name": "Madrid",
    "admin_level": "8"  # Уровень муниципалитета в Испании
}


# ============================================================
# 📡 OSMnx / OVERPASS API
# ============================================================
OVERPASS_URLS: Final[list[str]] = [
    "https://maps.mail.ru/osm/tools/overpass/api",
    "https://overpass.openstreetmap.ru/api",
    "https://overpass-api.de/api",
]
OSM_USER_AGENT: Final[str] = (
    "Hello-GIS-Project/1.0 (Educational Project; contact: student@example.com)"
)
OSM_TIMEOUT: Final[int] = 180


# ============================================================
# 🎨 ВИЗУАЛИЗАЦИЯ
# ============================================================
@dataclass(frozen=True)
class VizConfig:
    """Параметры визуализации."""
    dpi: int = 300
    map_figsize: tuple[int, int] = (8, 8)
    stats_figsize: tuple[int, int] = (14, 6)
    stats_bg_color: str = "#f8f9fa"
    map_bg_color: str = "white"
    
    park_fill: str = "#6fda9c"
    park_edge: str = "#3acd77"
    park_alpha: float = 0.8
    park_linewidth: float = 1.0
    
    grid_color: str = "black"
    grid_alpha: float = 0.4
    grid_linewidth: float = 0.7
    grid_linestyle: str = "--"
    
    frame_color: str = "black"
    frame_linewidth: float = 1.5
    
    title_fontsize: int = 16
    label_fontsize: int = 9
    label_color: str = "gray"
    
    stat_colormap: str = "tab20"


VIZ: Final[VizConfig] = VizConfig()


# ============================================================
# 🔍 ФИЛЬТРАЦИЯ ДАННЫХ
# ============================================================
MIN_FEATURE_AREA_HA: Final[float] = 1.0   # было MIN_PARK_AREA_HA
TOP_N_FEATURES: Final[int] = 15            # было TOP_N_PARKS
DEFAULT_FEATURE_NAME: Final[str] = "Unnamed"  # было DEFAULT_PARK_NAME