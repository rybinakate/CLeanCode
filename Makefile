.PHONY: check format run clean

# Проверка кода (типы + стиль)
check:
	uv run mypy src/
	ruff check src/

# Автоматическое форматирование кода
format:
	ruff format src/
	ruff check --fix src/

# Запуск основного скрипта
run:
	uv run python src/main.py

# Очистка кэша
clean:
	rm -rf .mypy_cache .ruff_cache __pycache__
