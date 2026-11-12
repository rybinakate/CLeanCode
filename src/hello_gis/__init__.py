"""
Hello-GIS: пакет для работы с геопространственными данными.
Агностичен к локации — регион задается в config.py.
"""

from .config import (
    PARKS_RAW_PATH, MAP_OUTPUT, STATS_OUTPUT,
    QUERY_BBOX, OSM_TAGS, VIZ,
    MIN_FEATURE_AREA_HA, TOP_N_FEATURES,
)

__all__ = [
    "PARKS_RAW_PATH", "MAP_OUTPUT", "STATS_OUTPUT",
    "QUERY_BBOX", "OSM_TAGS", "VIZ",
    "MIN_FEATURE_AREA_HA", "TOP_N_FEATURES",
]