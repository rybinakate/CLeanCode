"""
Модуль сетевого анализа доступности парков.
Рассчитывает метрики покрытия территории, выявляет "парковые пустыни" 
и строит изохроны доступности. Совместим с OSMnx 2.x.
"""

from . import deps as d
from . import config as cfg
import networkx as nx
from shapely.ops import unary_union
from shapely.geometry import box


def get_walk_network() -> d.nx.MultiDiGraph:
    """Скачивает и подготавливает пешеходную сеть."""
    d.ox.settings.use_cache = True
    d.ox.settings.log_console = False
    d.logging.info("🌐 Скачивание пешеходной сети (может занять 1-2 мин)...")

    
    # Скачиваем сеть типа "walk" (тротуары, пешеходные зоны, дорожки в парках)
    G = d.ox.graph_from_bbox(
        bbox=cfg.QUERY_BBOX,
        network_type="walk",
        simplify=True
    )
    
    # ✅ ИСПРАВЛЕНО для OSMnx 2.x: функция перемещена в модуль distance
    G = d.ox.distance.add_edge_lengths(G)
    
    d.logging.info(f"✅ Сеть загружена: {G.number_of_nodes()} узлов, {G.number_of_edges()} ребер")
    return G


def calculate_accessibility_metrics(
    G: d.nx.MultiDiGraph, 
    parks_gdf: d.gpd.GeoDataFrame, 
    max_walk_meters: float = 800
) -> dict:
    """
    Рассчитывает метрики доступности: % покрытия и геометрию "парковых пустынь".
    """
    d.logging.info(f"🚶 Расчет зон доступности ({max_walk_meters} м)...")
    
    # Проецируем всё в локальную метрическую систему для точного расчета площадей
    G_proj = d.ox.project_graph(G, to_crs=cfg.CRS_LOCAL)
    parks_proj = parks_gdf.to_crs(crs=cfg.CRS_LOCAL)
    
    # Создаем полигон общей изучаемой территории (Bounding Box с буфером)
    minx, miny, maxx, maxy = parks_proj.total_bounds
    study_area = box(minx - 1000, miny - 1000, maxx + 1000, maxy + 1000)
    total_area_sq_m = study_area.area
    
    accessible_polygons = []
    
    # Берем топ-7 крупнейших парков для анализа (оптимально для скорости и репрезентативности)
    top_parks = parks_proj.sort_values('area_hectares', ascending=False).head(7)
    
    for idx, row in top_parks.iterrows():
        centroid = row['geometry'].centroid
        
        # Находим ближайший узел сети
        nearest_node = d.ox.distance.nearest_nodes(G_proj, X=centroid.x, Y=centroid.y)
        
        # ✅ ИСПРАВЛЕНО для OSMnx 2.x: функция перемещена в модуль convert
        undirected_G = d.ox.convert.to_undirected(G_proj)
        
        # Находим все узлы, достижимые за max_walk_meters по длине ребер
        nodes_in_range = nx.single_source_dijkstra_path_length(
            undirected_G, 
            source=nearest_node, 
            cutoff=max_walk_meters, 
            weight='length'
        )
        
        # Создаем подграф из достижимых узлов и извлекаем его ребра
        reachable_subgraph = undirected_G.subgraph(nodes_in_range.keys())
        _, edges_gdf = d.ox.convert.graph_to_gdfs(reachable_subgraph)
        
        # Строим полигон доступности: буфер вокруг достижимых улиц (ширина тротуара ~3м = буфер 1.5м)
        # unary_union объединяет все пересекающиеся буферы в один сплошной полигон
        access_poly = edges_gdf.buffer(15).unary_union
        accessible_polygons.append(access_poly)
        
    # Объединяем зоны доступности всех парков в ОДИН полигон
    total_accessible_area = unary_union(accessible_polygons)
    
    # Обрезаем по границам изучаемой территории (чтобы не считать площадь за городом)
    total_accessible_area = total_accessible_area.intersection(study_area)
    accessible_area_sq_m = total_accessible_area.area
    
    # Вычисляем "Парковые пустыни" (разность между всей территорией и доступной)
    park_deserts = study_area.difference(total_accessible_area)
    desert_area_sq_m = park_deserts.area
    
    # Расчет метрик
    metrics = {
        "total_area_ha": total_area_sq_m / 10_000,
        "accessible_area_ha": accessible_area_sq_m / 10_000,
        "desert_area_ha": desert_area_sq_m / 10_000,
        "accessible_pct": (accessible_area_sq_m / total_area_sq_m) * 100,
        "desert_pct": (desert_area_sq_m / total_area_sq_m) * 100,
        "accessibility_index": (accessible_area_sq_m / total_area_sq_m),
        "park_deserts_geometry": park_deserts,
        "accessible_geometry": total_accessible_area
    }
    
    return metrics


def save_park_deserts(metrics: dict, output_path: d.Path) -> None:
    """Сохраняет геометрию парковых пустынь в GeoJSON для дальнейшего анализа."""
    gdf = d.gpd.GeoDataFrame(
        [{"zone": "Park Desert", "area_ha": metrics["desert_area_ha"], "geometry": metrics["park_deserts_geometry"]}],
        crs=cfg.CRS_LOCAL
    ).to_crs(crs=cfg.CRS_GEO)
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    gdf.to_file(output_path, driver="GeoJSON")
    d.logging.info(f"💾 Геометрия 'парковых пустынь' сохранена: {output_path}")

def plot_accessibility_and_deserts(
    parks_gdf: d.gpd.GeoDataFrame,
    metrics: dict,
    output_path: d.Path = cfg.OUTPUTS_DIR / "park_accessibility_analysis.png"
) -> None:
    """Визуализирует доступность и выделяет парковые пустыни."""
    import contextily as ctx  # Локальный импорт, чтобы не ломать make data
    
    d.logging.info("🎨 Визуализация анализа доступности...")
    
    fig, ax = d.plt.subplots(figsize=(10, 10))
    
    # Проецируем для отображения в Web Mercator
    parks_web = parks_gdf.to_crs(crs=cfg.CRS_WEB)
    accessible_web = d.gpd.GeoSeries([metrics["accessible_geometry"]], crs=cfg.CRS_LOCAL).to_crs(crs=cfg.CRS_WEB).iloc[0]
    deserts_web = d.gpd.GeoSeries([metrics["park_deserts_geometry"]], crs=cfg.CRS_LOCAL).to_crs(crs=cfg.CRS_WEB).iloc[0]
    
    # Устанавливаем границы карты с небольшим буфером
    minx, miny, maxx, maxy = parks_web.total_bounds
    ax.set_xlim(minx - (maxx-minx)*0.1, maxx + (maxx-minx)*0.1)
    ax.set_ylim(miny - (maxy-miny)*0.1, maxy + (maxy-miny)*0.1)
    
    # 1. Подложка (Esri World Gray Canvas)
    ctx.add_basemap(
        ax,
        source=ctx.providers.Esri.WorldGrayCanvas,
        crs=cfg.CRS_WEB,
        zoom=13,
    )
    
    # Сдвигаем подпись источника
    for text in ax.texts:
        if "Esri" in text.get_text() or "OpenStreetMap" in text.get_text():
            x, y = text.get_position()
            text.set_position((x + 0.02, y + 0.02))
            text.set_bbox(dict(facecolor="white", alpha=0.85, edgecolor="none", pad=1.5))
            text.set_fontsize(7)
            text.set_color("#555555")
    
    # 2. Парковые пустыни (красный, полупрозрачный, БЕЗ контура)
    d.gpd.GeoSeries([deserts_web]).plot(
        ax=ax, color="#e5b85e", edgecolor="none", alpha=0.3, zorder=1
    )
    
    # 3. Зоны доступности (зеленый, полупрозрачный, БЕЗ контура)
    d.gpd.GeoSeries([accessible_web]).plot(
        ax=ax, color="#048608", edgecolor="none", alpha=0.3, zorder=2
    )
    
    # 4. Парки (темно-зеленые, с белой обводкой для контраста)
    parks_web.plot(
        ax=ax, color="#043e04",  zorder=3
    )
    
    
    
    # 6. Блок с метриками
    info_text = (
        f"Accessibility Index: {metrics['accessibility_index']:.2f}\n"
        f"Accessible Area: {metrics['accessible_pct']:.1f}%\n"
        f"Park Deserts: {metrics['desert_pct']:.1f}%"
    )
    ax.text(
        0.05, 0.95, info_text, transform=ax.transAxes, fontsize=12, fontweight='bold',
        verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.85, edgecolor='gray')
    )
    
    ax.set_title("Park Accessibility & Park Deserts Analysis", fontsize=16, fontweight="bold", pad=15)
    ax.axis("off")
    
    d.plt.savefig(output_path, dpi=cfg.VIZ.dpi, bbox_inches="tight", facecolor="white")
    d.plt.close()
    d.logging.info(f"✅ Карта анализа сохранена: {output_path}")


def run_network_analysis() -> None:
    """Главная функция пайплайна."""
    d.logging.basicConfig(level=d.logging.INFO, format="%(levelname)s: %(message)s")
    
    if not cfg.PARKS_RAW_PATH.exists():
        d.logging.error("⚠️ Сначала скачайте данные парков: make data")
        return
    
    parks = d.gpd.read_file(cfg.PARKS_RAW_PATH)
    parks = parks[(parks['name'] != cfg.DEFAULT_FEATURE_NAME) & (parks['area_hectares'] > 1.0)]
    
    if parks.empty:
        d.logging.error("⚠️ Не найдено парков для анализа.")
        return
        
    # 1. Сеть
    G = get_walk_network()
    
    # 2. Метрики (800 метров ≈ 10 минут ходьбы)
    metrics = calculate_accessibility_metrics(G, parks, max_walk_meters=800)
    
    # 3. Вывод метрик в консоль
    print("\n" + "="*50)
    print("📊 РЕЗУЛЬТАТЫ АНАЛИЗА ДОСТУПНОСТИ (10 мин ходьбы)")
    print("="*50)
    print(f"📍 Общая площадь анализа: {metrics['total_area_ha']:,.0f} га")
    print(f"✅ Доступная территория:  {metrics['accessible_area_ha']:,.0f} га ({metrics['accessible_pct']:.1f}%)")
    print(f"❌ Парковые пустыни:      {metrics['desert_area_ha']:,.0f} га ({metrics['desert_pct']:.1f}%)")
    print(f"📈 Индекс доступности:    {metrics['accessibility_index']:.2f} (идеал = 1.0)")
    print("="*50 + "\n")
    
    # 4. Сохранение данных пустынь
    desert_path = cfg.DATA_RAW_DIR / "park_deserts.geojson"
    save_park_deserts(metrics, desert_path)
    
    # 5. Визуализация
    plot_accessibility_and_deserts(parks, metrics)
    
    d.logging.info("✨ Сетевой анализ завершен!")


if __name__ == "__main__":
    run_network_analysis()