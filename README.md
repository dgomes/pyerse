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
python -m build
python -m twine check --strict dist/*
```

Use `ruff format .` to format code. CI checks Python 3.11–3.14 and builds both
a source distribution and a wheel, then tests the installed wheel outside the
source tree. Package metadata and tool configuration live in `pyproject.toml`;
`VERSION` remains the single source of the package version.

## Releases to PyPI

One-time setup:

1. Create a GitHub environment named `pypi` in `dgomes/pyerse`.
2. In the PyPI project's Publishing settings, add a GitHub Trusted Publisher:
   owner `dgomes`, repository `pyerse`, workflow `python-publish.yml`,
   environment `pypi`. See the [PyPI instructions](https://docs.pypi.org/trusted-publishers/adding-a-publisher/).

For each release, update `VERSION` to a new, unused PyPI version and commit it
with the release changes. Tag that commit with the version (for example,
`v0.0.5` for `VERSION` containing `0.0.5`) and publish a GitHub release.
Draft releases do not publish. Published prereleases also upload to PyPI;
use a PEP 440 prerelease version such as `0.0.5rc1` for those.

The release workflow checks the tag against `VERSION`, runs the full CI suite,
and publishes the validated wheel and source distribution through Trusted
Publishing. No PyPI username, password, or API-token secrets are needed.
Any configured GitHub environment approval rules must be satisfied before
publication. PyPI does not allow replacing a previously uploaded version.
