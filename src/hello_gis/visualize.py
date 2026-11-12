"""
Модуль визуализации геопространственных данных.
Использует geopandas, contextily и matplotlib.
Агностичен к локации — регион задается в config.py.
"""

from . import deps as d
from . import config as cfg

# --- Тяжёлые/специфичные зависимости только для визуализации ---
import contextily as ctx
import seaborn as sns


def plot_parks_with_basemap(
    gdf: d.gpd.GeoDataFrame, output_path: d.Path = cfg.MAP_OUTPUT
) -> None:
    """Рисует карту парков с подложкой, градусной сеткой и рамкой."""
    
    fig, ax = d.plt.subplots(figsize=cfg.VIZ.map_figsize)

    # Границы с буфером
    minx, miny, maxx, maxy = gdf.total_bounds
    x_buf = (maxx - minx) * cfg.MAP_BUFFER_RATIO
    y_buf = (maxy - miny) * cfg.MAP_BUFFER_RATIO
    minx, miny = minx - x_buf, miny - y_buf
    maxx, maxy = maxx + x_buf, maxy + y_buf

    bbox_gdf = d.gpd.GeoDataFrame(
        geometry=[d.box(minx, miny, maxx, maxy)], crs=cfg.CRS_GEO
    )
    bbox_web = bbox_gdf.to_crs(crs=cfg.CRS_WEB)
    minx_w, miny_w, maxx_w, maxy_w = bbox_web.total_bounds

    ax.set_xlim(minx_w, maxx_w)
    ax.set_ylim(miny_w, maxy_w)

    # Подложка (✅ ctx используется напрямую, не через d.)
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

    # Парки
    gdf_web = gdf.to_crs(crs=cfg.CRS_WEB)
    gdf_web.plot(
        ax=ax,
        color=cfg.VIZ.park_fill,
        edgecolor=cfg.VIZ.park_edge,
        linewidth=cfg.VIZ.park_linewidth,
        alpha=cfg.VIZ.park_alpha,
        label="Parks",
        zorder=3,
    )

    # Сетка
    grid_lines, grid_labels = [], []
    for lon in cfg.GRID_LONS:
        if minx <= lon <= maxx:
            pt_b = d.gpd.GeoSeries([d.Point(lon, miny)], crs=cfg.CRS_GEO).to_crs(crs=cfg.CRS_WEB).iloc[0]
            pt_t = d.gpd.GeoSeries([d.Point(lon, maxy)], crs=cfg.CRS_GEO).to_crs(crs=cfg.CRS_WEB).iloc[0]
            grid_lines.append(d.LineString([pt_b, pt_t]))
            grid_labels.append(f"{abs(lon)}° {'W' if lon < 0 else 'E'}")

    for lat in cfg.GRID_LATS:
        if miny <= lat <= maxy:
            pt_l = d.gpd.GeoSeries([d.Point(minx, lat)], crs=cfg.CRS_GEO).to_crs(crs=cfg.CRS_WEB).iloc[0]
            pt_r = d.gpd.GeoSeries([d.Point(maxx, lat)], crs=cfg.CRS_GEO).to_crs(crs=cfg.CRS_WEB).iloc[0]
            grid_lines.append(d.LineString([pt_l, pt_r]))
            grid_labels.append(f"{lat}° N")

    grid_gdf = d.gpd.GeoDataFrame({"label": grid_labels, "geometry": grid_lines}, crs=cfg.CRS_WEB)
    grid_gdf.plot(
        ax=ax, color=cfg.VIZ.grid_color, linestyle=cfg.VIZ.grid_linestyle,
        linewidth=cfg.VIZ.grid_linewidth, alpha=cfg.VIZ.grid_alpha, zorder=2,
    )

    # Рамка
    rect = d.Rectangle(
        (minx_w, miny_w), maxx_w - minx_w, maxy_w - miny_w,
        transform=ax.transData, fill=False,
        edgecolor=cfg.VIZ.frame_color, linewidth=cfg.VIZ.frame_linewidth, zorder=4,
    )
    ax.add_patch(rect)

    ax.set_xticks([])
    ax.set_yticks([])
    ax.axis("off")

    # Метки сетки
    offset_x = (maxx_w - minx_w) * 0.03
    offset_y = (maxy_w - miny_w) * 0.03
    for _, row in grid_gdf.iterrows():
        label, geom = row["label"], row["geometry"]
        x, y = geom.coords[0]
        if "N" in label:
            ax.text(x - offset_x, y, f" {label}", ha="right", va="center",
                    fontsize=cfg.VIZ.label_fontsize, color=cfg.VIZ.label_color,
                    bbox=dict(facecolor="white", alpha=0.9, edgecolor="none", pad=2), clip_on=False)
        else:
            ax.text(x, y - offset_y, f"{label} ", ha="center", va="top",
                    fontsize=cfg.VIZ.label_fontsize, color=cfg.VIZ.label_color,
                    bbox=dict(facecolor="white", alpha=0.9, edgecolor="none", pad=2), clip_on=False)

    ax.set_title("Parks", fontsize=cfg.VIZ.title_fontsize, fontweight="bold", pad=15)
    ax.legend(loc="upper left", framealpha=0.95, edgecolor="gray")

    d.plt.savefig(output_path, dpi=cfg.VIZ.dpi, bbox_inches="tight", facecolor=cfg.VIZ.map_bg_color)
    d.plt.close()
    print(f"✅ Карта сохранена: {output_path}")


def plot_park_statistics(
    gdf: d.gpd.GeoDataFrame, output_path: d.Path = cfg.STATS_OUTPUT
) -> None:
    """Рисует статистику: распределение площадей парков."""
    
    sns.set_style("whitegrid")  # ✅ sns напрямую

    fig, axes = d.plt.subplots(1, 2, figsize=cfg.VIZ.stats_figsize)
    fig.patch.set_facecolor(cfg.VIZ.stats_bg_color)

    # Динамическая палитра
    unique_parks = gdf["name"].unique()
    cmap = d.plt.get_cmap(cfg.VIZ.stat_colormap)
    colors = [cmap(i) for i in d.np.linspace(0, 1, len(unique_parks))]
    color_map = dict(zip(unique_parks, colors))

    # Гистограмма
    sorted_gdf = gdf.sort_values("area_hectares")
    bar_colors = sorted_gdf["name"].map(color_map).tolist()
    sns.barplot(  # ✅ sns напрямую
        data=sorted_gdf, x="area_hectares", y="name",
        ax=axes[0], palette=bar_colors, hue="name", legend=False,
    )
    axes[0].set_xlabel("Area (hectares)", fontweight="bold", fontsize=12)
    axes[0].set_ylabel("")
    axes[0].set_title("Top Parks by Size", fontweight="bold", pad=15, fontsize=14)
    axes[0].set_facecolor("white")

     # ✅ ДОБАВЛЕНО: Подписи значений площадей на каждом баре
    for i, (idx, row) in enumerate(sorted_gdf.iterrows()):
        area = row["area_hectares"]
        # Позиционируем текст чуть правее конца бара
        # i - это индекс бара (0, 1, 2, ...)
        # Добавляем небольшой отступ (0.5% от максимального значения)
        max_area = sorted_gdf["area_hectares"].max()
        offset = max_area * 0.01
        
        axes[0].text(
            area + offset,  # x-координата (чуть правее бара)
            i,              # y-координата (центр бара)
            f"{area:.0f} ha",  # текст с округлением до целых
            va="center",    # вертикальное выравнивание по центру
            ha="left",      # горизонтальное выравнивание слева
            fontsize=10,
            fontweight="bold",
            color="#333333"
        )

    # Пончик
    pie_colors = gdf["name"].map(color_map).tolist()
    wedges, _ = axes[1].pie(
        gdf["area_hectares"], colors=pie_colors, startangle=90,
        wedgeprops=dict(width=0.4, edgecolor="white", linewidth=2),
    )
    axes[1].legend(wedges, gdf["name"], title="Parks",
                   loc="center left", bbox_to_anchor=(1, 0, 0.5, 1),
                   fontsize=10, title_fontsize=12)
    axes[1].set_title("Area Distribution", fontweight="bold", pad=15, fontsize=14)
    axes[1].set_facecolor("white")

    d.plt.suptitle("Parks Statistics", fontsize=18, fontweight="bold", y=1.02)
    d.plt.savefig(output_path, dpi=cfg.VIZ.dpi, bbox_inches="tight", facecolor=cfg.VIZ.stats_bg_color)
    d.plt.close()
    print(f"✅ Статистика сохранена: {output_path}")


def main() -> None:
    """Главная функция: загружает данные и создает визуализации."""
    d.logging.basicConfig(level=d.logging.INFO, format="%(levelname)s: %(message)s")

    if not cfg.PARKS_RAW_PATH.exists():
        print(f"⚠️ Файл {cfg.PARKS_RAW_PATH} не найден!")
        print("💡 Сначала выполните команду: make data")
        return

    print("🎨 Загрузка данных из OSM...")
    parks = d.gpd.read_file(cfg.PARKS_RAW_PATH)
    parks = parks[
        (parks["name"] != cfg.DEFAULT_FEATURE_NAME)
        & (parks["area_hectares"] > cfg.MIN_FEATURE_AREA_HA)
    ].sort_values("area_hectares", ascending=False).head(cfg.TOP_N_FEATURES)

    print(f"📍 Визуализируем {len(parks)} крупнейших объектов")
    plot_parks_with_basemap(parks)
    plot_park_statistics(parks)
    print("✨ Все визуализации готовы!")


if __name__ == "__main__":
    main()