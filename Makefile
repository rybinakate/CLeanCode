# ============================================================
# Makefile для проекта Hello GIS
# Использование: make <цель> (например: make run, make check)
# ============================================================

# --- ПЕРЕМЕННЫЕ ---
PYTHON := uv run python
SRC := src
PACKAGE := $(SRC)/hello_gis
DATA_RAW := data/raw
DATA_PROCESSED := data/processed
OUTPUTS := outputs

# Все Python-файлы в пакете hello_gis/
SOURCES := $(wildcard $(PACKAGE)/*.py)

# --- ЦЕЛИ, КОТОРЫЕ НЕ ЯВЛЯЮТСЯ ФАЙЛАМИ ---
.PHONY: all help install check format run test clean data viz

# --- ГЛАВНАЯ ЦЕЛЬ (выполняется при простом `make`) ---
all: check run
	@echo "✅ Всё готово!"

# --- СПРАВКА ---
help:
	@echo "Доступные команды:"
	@echo "  make help          - Показать эту справку"
	@echo "  make all           - Проверить код и запустить (по умолчанию)"
	@echo "  make install       - Установить зависимости"
	@echo "  make check         - Проверить код (mypy + ruff)"
	@echo "  make format        - Отформатировать код"
	@echo "  make run           - Запустить основной скрипт (main.py)"
	@echo "  make data          - Скачать данные из OSM"
	@echo "  make viz           - Создать визуализации"
	@echo "  make test          - Запустить тесты"
	@echo "  make clean         - Очистить кэш, outputs и временные файлы"

# --- УСТАНОВКА ЗАВИСИМОСТЕЙ ---
install:
	uv sync
	@echo "✅ Зависимости установлены"

# --- СКАЧИВАНИЕ ДАННЫХ ---
data:
	@echo "📥 Скачиваем данные из OSM..."
	$(PYTHON) -m hello_gis.fetch_data
	@echo "✅ Данные готовы!"

# --- ВИЗУАЛИЗАЦИЯ ---
viz:
	@echo "🎨 Создаем визуализации..."
	$(PYTHON) -m hello_gis.visualize
	@echo "✅ Визуализации готовы!"

	# --- СЕТЕВОЙ АНАЛИЗ ---
network:
	@echo "🕸️  Запускаем сетевой анализ доступности парков..."
	$(PYTHON) -m hello_gis.network_analysis
	@echo "✅ Анализ завершен!"

# --- ПРОВЕРКА КОДА ---
check: $(SOURCES)
	@echo "🔍 Проверяем типы (mypy)..."
	$(PYTHON) -m mypy $(PACKAGE)/
	@echo "🎨 Проверяем стиль (ruff)..."
	ruff check $(PACKAGE)/
	@echo "✅ Все проверки пройдены!"

# --- ФОРМАТИРОВАНИЕ КОДА ---
format:
	@echo "🎨 Форматируем код..."
	ruff format $(PACKAGE)/
	ruff check --fix $(PACKAGE)/
	@echo "✅ Код отформатирован!"

# --- ЗАПУСК ПРОГРАММЫ ---
run: $(SOURCES)
	@echo "🚀 Запускаем программу..."
	$(PYTHON) -m hello_gis.main

# --- ТЕСТЫ ---
test:
	@echo "🧪 Запускаем тесты..."
	$(PYTHON) -m pytest tests/ -v
	@echo "✅ Тесты пройдены!"

# --- ОЧИСТКА ---
clean:
	@echo "🧹 Очищаем кэш и временные файлы..."
	rm -rf .mypy_cache .ruff_cache __pycache__
	rm -rf .pytest_cache
	rm -rf $(PACKAGE)/__pycache__
	rm -rf cache/
	rm -rf $(OUTPUTS)/*
	@echo "✅ Очистка завершена!"