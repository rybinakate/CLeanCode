"""
Модуль для скачивания геопространственных данных через OSMnx.
Production-стандарт: отказоустойчивость, правильные headers, кэширование и обрезка по границе.
"""

from . import deps as d
from . import config as cfg


def _setup_osmnx() -> None:
    """Настраивает OSMnx согласно конфигурации."""
    d.ox.settings.http_user_agent = cfg.OSM_USER_AGENT
    d.ox.settings.requests_timeout = cfg.OSM_TIMEOUT
    d.ox.settings.use_cache = True
    d.ox.settings.log_console = False


def _download_with_fallback(bbox, tags) -> d.gpd.GeoDataFrame | None:
    """Пытается скачать данные с нескольких серверов по очереди."""
    for base_url in cfg.OVERPASS_URLS:
        d.ox.settings.overpass_url = base_url
        try:
            gdf = d.ox.features_from_polygon(bbox, tags=tags)
            return gdf
        except Exception as e:
            d.logging.warning(f"⚠️ Ошибка ({base_url}): {e}")
            continue
    return None


def _get_city_boundary() -> d.gpd.GeoDataFrame | None:
    """Скачивает административный полигон города из OSM по тегам из config.py."""
    d.logging.info(f"🏙️ Загрузка границы города: {cfg.CITY_NAME}...")
    bbox = d.geom.box(*cfg.QUERY_BBOX)
    
    try:
        boundary_gdf = d.ox.features_from_polygon(bbox, tags=cfg.CITY_BOUNDARY_TAGS)
        if boundary_gdf.empty:
            d.logging.warning(f"⚠️ Не удалось найти полигон {cfg.CITY_NAME}.")
            return None
        return boundary_gdf.iloc[0:1].copy() # Берем первый (крупнейший) полигон
    except Exception as e:
        d.logging.warning(f"⚠️ Ошибка при загрузке границы: {e}.")
        return None

def _clean_and_prepare(gdf: d.gpd.GeoDataFrame, city_boundary: d.gpd.GeoDataFrame | None) -> d.gpd.GeoDataFrame:
   #  """Очистка, расчет площади, ОБРЕЗКА по городу и оптимизация."""
    
    # 1. Убираем объекты без геометрии
    gdf = gdf[~gdf.geometry.is_empty].copy()
    
    # 2. Заполняем пропуски в именах
    gdf["name"] = gdf["name"].fillna(cfg.DEFAULT_FEATURE_NAME) if "name" in gdf.columns else cfg.DEFAULT_FEATURE_NAME
    gdf = gdf[["name", "geometry"]].copy()
    
    # 3. Первичный расчет площади (до обрезки, для справки)
    gdf_proj = gdf.to_crs(crs=cfg.CRS_LOCAL)
    gdf["area_hectares"] = gdf_proj.geometry.area / 10_000
    
    # ============================================================
    # 🚀 ЗДЕСЬ ПРОИСХОДИТ ОБРЕЗКА (CLIP)!
    # ============================================================
    if city_boundary is not None:
        d.logging.info("✂️ Обрезка парков по границе города...")
        # Приводим границу к той же проекции, что и парки (EPSG:4326)
        boundary_matched = city_boundary.to_crs(gdf.crs)
        # Функция clip оставляет только те части парков, которые лежат ВНУТРИ полигона города
        gdf = d.gpd.clip(gdf, boundary_matched)
        d.logging.info(f"✅ Обрезка завершена. (Количество объектов могло измениться, т.к. некоторые парки разделились)")
        
        # 4. ПЕРЕСЧЕТ ПЛОЩАДИ ПОСЛЕ ОБРЕЗКИ (это критически важно!)
        gdf_proj = gdf.to_crs(crs=cfg.CRS_LOCAL)
        gdf["area_hectares"] = gdf_proj.geometry.area / 10_000
    # ============================================================
    
    # 5. Ранняя фильтрация: оставляем только крупные объекты (> 5 га)
    gdf = gdf[gdf['area_hectares'] > 5.0].copy()
    d.logging.info(f"📉 После фильтрации по площади (>5 га) осталось {len(gdf)} объектов.")
    
    # 6. Упрощение геометрии (спасает от зависаний при визуализации)
    gdf["geometry"] = gdf.simplify(tolerance=0.0001, preserve_topology=True)
    d.logging.info("🗜️ Геометрия упрощена для оптимизации памяти.")
    
    # 7. Возвращаем в стандартную географическую проекцию
    return gdf.to_crs(crs=cfg.CRS_GEO)


def fetch_parks(output_path: d.Path = cfg.PARKS_RAW_PATH) -> None:
    """Главная функция: скачивает, обрезает и сохраняет данные."""
    d.logging.basicConfig(level=d.logging.INFO, format="%(levelname)s: %(message)s")
    d.logging.info("🌍 Инициализация OSMnx (production mode)...")
    
    _setup_osmnx()
    
    bbox = d.geom.box(*cfg.QUERY_BBOX)
    
    # 1. Скачиваем сырые парки
    d.logging.info("🌳 Скачивание зеленых зон...")
    gdf = _download_with_fallback(bbox, cfg.OSM_TAGS)
    
    if gdf is None or gdf.empty:
        d.logging.error("❌ Не удалось получить данные ни с одного сервера.")
        d.sys.exit(1)
    
    # 2. Скачиваем границу города
    city_boundary = _get_city_boundary()
    
    # 3. Очищаем, ОБРЕЗАЕМ и оптимизируем
    d.logging.info("🧹 Очистка, обрезка и подготовка данных...")
    gdf = _clean_and_prepare(gdf, city_boundary=city_boundary)
    
    # 4. Сохраняем результат
    output_path.parent.mkdir(parents=True, exist_ok=True)
    gdf.to_file(output_path, driver="GeoJSON")
    d.logging.info(f"✅ Финальный результат: сохранено {len(gdf)} объектов в {output_path}")


if __name__ == "__main__":
    fetch_parks()