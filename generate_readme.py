bt = "```"

content = f"""# Hello GIS

A modern, type-checked Python project template for geospatial analysis.

## 🚀 Features

- **Modern Dependency Management**: Built with `uv` for blazing fast package resolution.
- **Code Quality**: Enforced with `ruff` (linting & formatting).
- **Type Safety**: Strict type checking with `mypy`.
- **Geospatial Stack**: Ready for `geopandas`, `shapely`, and `matplotlib`.

## 🛠️ Installation

1. Clone the repository:
{bt}bash
git clone <your-repo-url>
cd hello-gis
{bt}

2. Install dependencies using `uv`:
{bt}bash
uv sync
{bt}

## 💻 Usage

Run the main script:
{bt}bash
make run
{bt}

Run linting and type checking:
{bt}bash
make check
{bt}

Format the code:
{bt}bash
make format
{bt}

## 📂 Project Structure

{bt}text
hello-gis/
├── src/                 # Source code (production-ready)
│   └── main.py          # Main entry point
├── tests/               # Unit tests (to be added)
├── data/                # Data files (IGNORED by Git)
│   ├── raw/             # Raw, unmodified data
│   └── processed/       # Cleaned, transformed data
├── outputs/             # Generated results, maps, reports (IGNORED by Git)
├── Makefile             # Automation commands (make run, make check, etc.)
├── pyproject.toml       # Project metadata and dependencies
├── mypy.ini             # Type checking configuration
├── .gitignore           # Rules for files to exclude from Git
└── README.md            # This file
{bt}

*Note: The `data/` and `outputs/` directories are intentionally excluded from Git to keep the repository lightweight. They are created locally or via data download scripts.*

## 📄 License

MIT
"""

with open("README.md", "w", encoding="utf-8") as f:
    f.write(content)

print("✅ README.md успешно создан!")
