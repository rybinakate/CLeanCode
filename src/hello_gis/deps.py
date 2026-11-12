"""
Централизованные импорты сторонних зависимостей.
Только общие зависимости — специфичные импортируются локально.
"""

# --- Геопространственные ---
import osmnx as ox
import geopandas as gpd
from shapely.geometry import Point, LineString, box, Polygon
from shapely.geometry.base import BaseGeometry
import shapely.geometry as geom

# --- Визуализация ---
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.patches import Rectangle

# --- Данные ---
import pandas as pd
import numpy as np

# --- Стандартная библиотека ---
from pathlib import Path
import logging
import sys
import os

__all__ = [
    # Гео
    "ox", "gpd", "Point", "LineString", "box", "Polygon", "BaseGeometry", "geom",
    # Виз
    "plt", "cm", "Rectangle",
    # Данные
    "pd", "np",
    # Стандарт
    "Path", "logging", "sys", "os",
]