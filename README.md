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
pre-commit install
pre-commit run --all-files
ruff check .
ruff format --check .
python -m pytest
python -m pytest --cov=pyerse --cov-branch --cov-report=term-missing --cov-fail-under=90
python -m build
python -m twine check --strict dist/*
```

The installed pre-commit hook runs Ruff lint fixes and formatting before each
commit. Run `pre-commit run --all-files` to check the whole tracked repository;
Ruff and its hooks use the same pinned version as CI. Hooks may edit files;
review and stage those edits before committing. New files must be staged to be
included in pre-commit checks.

Use `ruff format .` to format code. CI checks Python 3.11–3.14 and builds both
a source distribution and a wheel, then tests the installed wheel outside the
source tree. Package metadata and tool configuration live in `pyproject.toml`;
`VERSION` remains the single source of the package version.

## Regional time-of-use cycles

The standard mainland classes remain `Ciclo_Diario` and `Ciclo_Semanal`.
Azores and Madeira each provide daily, optional daily, and weekly cycles:

| Region | Daily | Optional daily | Weekly |
|---|---|---|---|
| Azores | `Ciclo_Diario_Acores` | `Ciclo_Diario_Opcional_Acores` | `Ciclo_Semanal_Acores` |
| Madeira | `Ciclo_Diario_Madeira` | `Ciclo_Diario_Opcional_Madeira` | `Ciclo_Semanal_Madeira` |

```python
from datetime import datetime, timezone
from pyerse.ciclos import Ciclo_Semanal_Acores
from pyerse.comercializador import Plano, Opcao_Horaria

plan = Plano(6.9, Opcao_Horaria.TRI_HORARIA, Ciclo_Semanal_Acores)
tariff = plan.tarifa_actual(datetime.now(timezone.utc))
```

Regional cycles convert aware timestamps to `Atlantic/Azores` or
`Atlantic/Madeira`. Naive timestamps are interpreted as regional local time;
plan methods called without a timestamp use the region's clock.
Returned regional interval bounds use the regional timezone for aware inputs.
Weekly regional seasons run June–October and November–May; daily cycles use
summer/winter legal-hour seasons.

Cycle names are also accepted, such as `"Ciclo Semanal Açores"` and
`"Ciclo Diário Opcional Madeira"`. `Comercializador.opcao_ciclo()` lists all
supported names. These schedules come from ERSE's chart retrieved on
8 October 2026; see [the extraction and audit](docs/erse-cycle-audit.md).
Prices and taxes are not regionalized by selecting a cycle.

## Consumption VAT (January 2025 rules)

Consumption costs use mainland VAT: 6% on up to 200 kWh per 30 billed days
(300 kWh with `familia_numerosa=True`) for power up to 6.9 kVA, and 23% on
the remainder. Above 6.9 kVA, the entire consumption has 23% VAT.
`custo_kWh_final` also adds electricity excise duty, taxed at 23%.

For multi-tariff plans, pass `total_kwh` as the combined consumption of all
periods so the allowance is allocated proportionally. `dias` defaults to 30.
Without `total_kwh`, the supplied tariff consumption is treated as the total;
that default is appropriate for single-tariff plans.

```python
cost = plan.custo_kWh_final(tariff, kwh_consumidos=98, total_kwh=350, dias=30)
```

The same keyword arguments are accepted by `custo_kWh` and
`custo_kWh_actual`. Prices supplied with `definir_custo_kWh` exclude taxes.
These methods apply current rules and do not calculate historical VAT.
See [ERSE's explanation](https://www.erse.pt/media/0eydrnj1/ersexplica_iva-fatura_2025.pdf).
