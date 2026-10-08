# Python ERSE

A Python package for Portuguese energy tariffs and ERSE information. Requires Python 3.11 or newer.

This follows ERSE information such as https://www.erse.pt/atividade/regulacao/tarifas-e-precos-eletricidade/#periodos-horarios

## Installation

```sh
python -m pip install pyerse
```

## Development

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
ruff check .
ruff format --check .
python -m pytest
python -m pytest --cov=pyerse --cov-branch --cov-report=term-missing --cov-fail-under=90
python -m build
python -m twine check --strict dist/*
```

Use `ruff format .` to format code. CI checks Python 3.11–3.14 and builds both
a source distribution and a wheel, then tests the installed wheel outside the
source tree. Package metadata and tool configuration live in `pyproject.toml`;
`VERSION` remains the single source of the package version.
