"""
Точка входа в проект Hello-GIS.
Координирует запуск всех модулей (скачивание и визуализация).
"""

from . import deps as d
from .fetch_data import fetch_parks
from .visualize import main as visualize_main


def calculate_area(geom: d.BaseGeometry) -> float:
    """
    Вычисляет площадь геометрии.
    Демонстрация использования типизированных импортов из deps.py.
    """
    return float(geom.area)


def run_full_pipeline() -> None:
    """
    Запускает полный пайплайн: скачивание данных + создание визуализаций.
    """
    d.logging.basicConfig(level=d.logging.INFO, format="%(levelname)s: %(message)s")
    print("🚀 Запуск полного пайплайна Hello-GIS...\n")
    
    # 1. Скачиваем и подготавливаем данные
    fetch_parks()
    print()
    
    # 2. Создаем карту и графики
    visualize_main()


def main() -> None:
    """Главная точка входа в приложение."""
    # Небольшая демонстрация работы с геометрией (можно удалить, если не нужна)
    test_polygon = d.Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])
    area = calculate_area(test_polygon)
    print(f"📐 Площадь тестового полигона 1x1: {area}\n")
    
    # Запуск основного пайплайна
    run_full_pipeline()


if __name__ == "__main__":
    main()