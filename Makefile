# ============================================================
# Makefile для проекта Hello GIS
# Использование: make <цель> (например: make run, make check)
# ============================================================

# --- ПЕРЕМЕННЫЕ ---
# Короткие имена для часто используемых команд и путей
PYTHON := uv run python
SRC := src
DATA_RAW := data/raw
DATA_PROCESSED := data/processed
OUTPUTS := outputs

# Все Python-файлы в папке src/
SOURCES := $(wildcard $(SRC)/*.py)

# --- ЦЕЛИ, КОТОРЫЕ НЕ ЯВЛЯЮТСЯ ФАЙЛАМИ ---
.PHONY: all help install check format run test clean download_data process_data

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
	@echo "  make run           - Запустить основной скрипт"
	@echo "  make test          - Запустить тесты"
	@echo "  make download_data - Скачать данные (заглушка)"
	@echo "  make process_data  - Обработать данные (заглушка)"
	@echo "  make clean         - Очистить кэш и временные файлы"

# --- УСТАНОВКА ЗАВИСИМОСТЕЙ ---
install:
	uv sync
	@echo "✅ Зависимости установлены"

# --- ПРОВЕРКА КОДА ---
# Зависит от всех исходных файлов: если код изменился — проверка запустится
check: $(SOURCES)
	@echo "🔍 Проверяем типы (mypy)..."
	$(PYTHON) -m mypy $(SRC)/
	@echo "🎨 Проверяем стиль (ruff)..."
	ruff check $(SRC)/
	@echo "✅ Все проверки пройдены!"

# --- ФОРМАТИРОВАНИЕ КОДА ---
format:
	@echo "🎨 Форматируем код..."
	ruff format $(SRC)/
	ruff check --fix $(SRC)/
	@echo "✅ Код отформатирован!"

# --- ЗАПУСК ПРОГРАММЫ ---
run: $(SOURCES)
	@echo "🚀 Запускаем программу..."
	$(PYTHON) $(SRC)/main.py

# --- ТЕСТЫ ---
test:
	@echo "🧪 Запускаем тесты..."
	$(PYTHON) -m pytest tests/ -v
	@echo "✅ Тесты пройдены!"

# --- РАБОТА С ДАННЫМИ (заглушки для будущего) ---
download_data:
	@echo "📥 Скачиваем данные..."
	@mkdir -p $(DATA_RAW)
	@echo "   Здесь будет скрипт скачивания данных из OSM/API"
	@echo "✅ Данные 'скачаны' в $(DATA_RAW)"

process_data: download_data
	@echo "⚙️  Обрабатываем данные..."
	@mkdir -p $(DATA_PROCESSED) $(OUTPUTS)
	@echo "   Здесь будет скрипт обработки данных"
	@echo "✅ Результаты сохранены в $(OUTPUTS)"

# --- ОЧИСТКА ---
clean:
	@echo "🧹 Очищаем кэш..."
	rm -rf .mypy_cache .ruff_cache __pycache__
	rm -rf .pytest_cache
	@echo "✅ Очистка завершена!"
