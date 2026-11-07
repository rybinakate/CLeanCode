"""
Модуль визуализации геопространственных данных.
Использует geopandas, contextily и matplotlib.
"""

import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as ctx
from shapely.geometry import Point
import pandas as pd


def create_sample_parks_madrid() -> gpd.GeoDataFrame:
    """
    Создает тестовые данные: несколько парков в Мадриде.
    В реальном проекте здесь будет загрузка из файла или API.
    """
    # Координаты реальных парков Мадрида (широта, долгота)
    parks_data = {
        'name': [
            'Retiro Park',
            'Casa de Campo',
            'Juan Carlos I Park',
            'West Park (Oeste)',
            'El Capricho'
        ],
        'area_hectares': [125, 1750, 220, 98, 14],
        'geometry': [
            Point(-3.6825, 40.4138),      # Retiro
            Point(-3.7475, 40.4195),      # Casa de Campo
            Point(-3.5795, 40.4595),      # Juan Carlos I
            Point(-3.7245, 40.4285),      # Oeste
            Point(-3.6045, 40.4565),      # El Capricho
        ]
    }
    
    # Создаем GeoDataFrame
    gdf = gpd.GeoDataFrame(parks_data, crs='EPSG:4326')
    
    # Добавляем буферы вокруг точек (имитация реальных полигонов парков)
    # 0.01 градуса ≈ 1 км
    gdf['geometry'] = gdf.buffer([0.008, 0.025, 0.012, 0.007, 0.005])
    
    return gdf


def plot_parks_with_basemap(gdf: gpd.GeoDataFrame, output_path: str = 'outputs/parks_map.png') -> None:
    """
    Рисует карту парков с подложкой, градусной сеткой и четкой рамкой.
    """
    from shapely.geometry import Point, LineString, box
    from matplotlib.patches import Rectangle

    # 1. Создаем холст (более квадратный, чтобы карта не растягивалась)
    fig, ax = plt.subplots(figsize=(8, 8))

    # 2. АВТОМАТИЧЕСКИ рассчитываем границы на основе парков + буфер 20%
    minx, miny, maxx, maxy = gdf.total_bounds # в градусах (EPSG:4326)
    x_buf = (maxx - minx) * 0.20
    y_buf = (maxy - miny) * 0.20
    minx, miny = minx - x_buf, miny - y_buf
    maxx, maxy = maxx + x_buf, maxy + y_buf

    # Переводим границы в метры (Web Mercator)
    bbox_gdf = gpd.GeoDataFrame(geometry=[box(minx, miny, maxx, maxy)], crs="EPSG:4326")
    bbox_web = bbox_gdf.to_crs(epsg=3857)
    minx_w, miny_w, maxx_w, maxy_w = bbox_web.total_bounds

    # Жестко задаем эти границы
    ax.set_xlim(minx_w, maxx_w)
    ax.set_ylim(miny_w, maxy_w)

    # 3. Добавляем подложку
    ctx.add_basemap(
        ax,
        source=ctx.providers.Esri.WorldGrayCanvas,
        crs="EPSG:3857",
        zoom=13,
    )
    # 3.5. "ОТКЛЕИВАЕМ" ПОДПИСЬ ИСТОЧНИКА (ESRI) ОТ КРАЯ КАРТЫ
    for text in ax.texts:
        # Ищем текст, который содержит название нашего источника
        if "Esri" in text.get_text() or "OpenStreetMap" in text.get_text():
            x, y = text.get_position() # Получаем координаты (y=0 - это самый низ)
            
            # Сдвигаем текст чуть вверх (на 2% от высоты карты)
            text.set_position((x+ 0.02, y + 0.02)) 
            
            # Делаем его красивым водяным знаком:
            text.set_bbox(dict(facecolor='white', alpha=0.85, edgecolor='none', pad=1.5))
            text.set_fontsize(7)       # Уменьшаем шрифт
            text.set_color('#555555')  # Делаем цвет темно-серым (не черным)

    # 4. Рисуем парки
    gdf_web = gdf.to_crs(epsg=3857)
    gdf_web.plot(
        ax=ax,
        color="#6fda9c",
        edgecolor="#3acd77",
        linewidth=1,
        alpha=0.8,
        label='Parks',
        zorder=3
    )

    # 5. Создаем линии сетки (только те, что попадают в наши границы)
    grid_lines = []
    grid_labels = []

    for lon in [-3.8, -3.7, -3.6, -3.5]:
        if minx <= lon <= maxx:
            pt_b = gpd.GeoSeries([Point(lon, miny)], crs="EPSG:4326").to_crs(3857).iloc[0]
            pt_t = gpd.GeoSeries([Point(lon, maxy)], crs="EPSG:4326").to_crs(3857).iloc[0]
            grid_lines.append(LineString([pt_b, pt_t]))
            grid_labels.append(f"{abs(lon)}° {'W' if lon < 0 else 'E'}")

    for lat in [40.3, 40.4, 40.5]:
        if miny <= lat <= maxy:
            pt_l = gpd.GeoSeries([Point(minx, lat)], crs="EPSG:4326").to_crs(3857).iloc[0]
            pt_r = gpd.GeoSeries([Point(maxx, lat)], crs="EPSG:4326").to_crs(3857).iloc[0]
            grid_lines.append(LineString([pt_l, pt_r]))
            grid_labels.append(f"{lat}° N")

    grid_gdf = gpd.GeoDataFrame({'label': grid_labels, 'geometry': grid_lines}, crs="EPSG:3857")
    grid_gdf.plot(
        ax=ax,
        color='black',
        linestyle='--',
        linewidth=0.7,
        alpha=0.4,
        zorder=2
    )

    # 6. РИСУЕМ ЧЕРНУЮ РАМКУ ВРУЧНУЮ (без включения осей!)
    rect = Rectangle(
        (minx_w, miny_w), maxx_w - minx_w, maxy_w - miny_w,
        transform=ax.transData,
        fill=False,
        edgecolor='black',
        linewidth=1.5,
        zorder=4
    )
    ax.add_patch(rect)

    # 7. ПОЛНОСТЬЮ ОТКЛЮЧАЕМ ОСИ (метки в метрах больше никогда не появятся)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.axis('off') 

    # 8. Размещаем метки снаружи рамки
    offset_x = (maxx_w - minx_w) * 0.03
    offset_y = (maxy_w - miny_w) * 0.03

    for idx, row in grid_gdf.iterrows():
        label = row['label']
        geom = row['geometry']
        
        if 'N' in label:  # Параллель -> метка слева
            x, y = geom.coords[0]
            ax.text(
                x - offset_x, y, f" {label}",
                ha='right', va='center', fontsize=9, color='gray', fontweight='regular',
                bbox=dict(facecolor='white', alpha=0.9, edgecolor='none', pad=2),
                clip_on=False
            )
        else:  # Меридиан -> метка снизу
            x, y = geom.coords[0]
            ax.text(
                x, y - offset_y, f"{label} ",
                ha='center', va='top', fontsize=9, color='gray', fontweight='regular',
                bbox=dict(facecolor='white', alpha=0.9, edgecolor='none', pad=2),
                clip_on=False
            )

    # 9. Заголовок и легенда
    ax.set_title('Parks of Madrid', fontsize=16, fontweight='bold', pad=15)
    ax.legend(loc='upper left', framealpha=0.95, edgecolor='gray')

    # 10. Сохранение
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"✅ Карта сохранена: {output_path}")


def plot_park_statistics(gdf: gpd.GeoDataFrame, output_path: str = 'outputs/park_stats.png') -> None:
    """
    Рисует статистику: распределение площадей парков.
    Использует словарь цветов для гарантированного совпадения на обоих графиках.
    """
    import seaborn as sns
    
    sns.set_style('whitegrid')
    
    # 1. СОЗДАЕМ СЛОВАРЬ ЦВЕТОВ: Название парка -> HEX-код
    # Теперь цвет жестко привязан к имени, порядок не важен!
    color_map = {
        'Casa de Campo': "#87e7af",         # Изумрудный (самый большой)
        'Juan Carlos I Park': "#66a1c9",    # Голубой
        'Retiro Park': "#f2d45e",           # Желтый
        'West Park (Oeste)': "#e78d3e",     # Оранжевый
        'El Capricho': "#9928c5"            # Фиолетовый (самый маленький)
    }

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.patch.set_facecolor('#f8f9fa') 

    # --- ГРАФИК 1: Горизонтальная гистограмма ---
    sorted_gdf = gdf.sort_values('area_hectares')
    
    # Магия: берем названия парков из отсортированной таблицы и "спрашиваем" у словаря их цвета
    bar_colors = sorted_gdf['name'].map(color_map).tolist()
    
    sns.barplot(
        data=sorted_gdf,
        x='area_hectares',
        y='name',
        ax=axes[0],
        palette=bar_colors, # <-- Передаем точный список цветов для этого порядка
        hue='name',
        legend=False
    )
    axes[0].set_xlabel('Area (hectares)', fontweight='bold', fontsize=12)
    axes[0].set_ylabel('')
    axes[0].set_title('Park Sizes', fontweight='bold', pad=15, fontsize=14)
    axes[0].set_facecolor('white')

    # --- ГРАФИК 2: Donut Chart (Пончик) ---
    # Магия: берем названия парков из исходной таблицы и "спрашиваем" у словаря их цвета
    pie_colors = gdf['name'].map(color_map).tolist()
    
    wedges, texts = axes[1].pie(
        gdf['area_hectares'],
        colors=pie_colors,  # <-- Передаем точный список цветов для этого порядка
        startangle=90,
        wedgeprops=dict(width=0.4, edgecolor='white', linewidth=2)
    )
    
    axes[1].legend(
        wedges, 
        gdf['name'], 
        title="Parks",
        loc="center left", 
        bbox_to_anchor=(1, 0, 0.5, 1),
        fontsize=10,
        title_fontsize=12
    )
    
    axes[1].set_title('Area Distribution', fontweight='bold', pad=15, fontsize=14)
    axes[1].set_facecolor('white')
    
    plt.suptitle('Madrid Parks Statistics', fontsize=18, fontweight='bold', y=1.02)
    
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='#f8f9fa')
    plt.close()
    
    print(f"✅ Статистика сохранена: {output_path}")

    
def main() -> None:
    """Главная функция: создает все визуализации."""
    print("🎨 Начинаем создание визуализаций...")
    
    # Создаем тестовые данные
    parks = create_sample_parks_madrid()
    print(f"📍 Создано {len(parks)} парков")
    
    # Рисуем карту
    plot_parks_with_basemap(parks)
    
    # Рисуем статистику
    plot_park_statistics(parks)
    
    print("✨ Все визуализации готовы!")


if __name__ == "__main__":
    main()
