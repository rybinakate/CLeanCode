from shapely.geometry import Polygon
from shapely.geometry.base import BaseGeometry


def calculate_area(geom: BaseGeometry) -> float:
    """Calculate the area of a given geometry."""
    return float(geom.area)


def main() -> None:
    """Run a small example with a test polygon."""
    test_polygon = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])

    area = calculate_area(test_polygon)

    print(f"Площадь полигона: {area}")


if __name__ == "__main__":
    main()
