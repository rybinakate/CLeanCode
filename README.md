# Hello GIS

A modern, type-checked Python project template for geospatial analysis.

## 🚀 Features

- **Modern Dependency Management**: Built with `uv` for blazing fast package 
resolution.
- **Code Quality**: Enforced with `ruff` (linting & formatting).
- **Type Safety**: Strict type checking with `mypy`.
- **Geospatial Stack**: Ready for `geopandas`, `shapely`, and `matplotlib`.

## 🛠️ Installation

1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd hello-gis

Install dependencies using uv:
uv sync

 Usage
make run


Run linting and type checking:
make check


Format the code:
make format


📂 Project Structure
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


Note: The data/ and outputs/ directories are intentionally excluded from Git to 
keep the repository lightweight. They are created locally or via data download 
scripts.
📄 License
MI

