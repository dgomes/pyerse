# ERSE time-of-use cycle audit

Retrieved: 2026-10-08. Page updated: 2026-10-01.

Source page: https://www.erse.pt/atividade/regulacao/tarifas-e-precos-eletricidade/#periodos-horarios

Chart data: https://www.erse.pt/media/rvsffyvv/horarios.json

The JSON snapshot preserves all 34 records exactly as retrieved. These are the current chart schedules, not the announced 2027 schedules. Times are local clock times; intervals include the start and exclude the end. `24:00` means the end of the day. A null day selector means all days.

## Full extraction

| Region | Season | Cycle | Days | Super vazio | Vazio normal | Cheias | Ponta |
|---|---|---|---|---|---|---|---|
| continental | verão | semanal | segunda_a_sexta | 02:00–06:00 | 00:00–02:00, 06:00–07:00 | 07:00–09:15, 12:15–24:00 | 09:15–12:15 |
| continental | verão | semanal | sábado | 02:00–06:00 | 00:00–02:00, 06:00–09:00, 14:00–20:00, 22:00–24:00 | 09:00–14:00, 20:00–22:00 | — |
| continental | verão | semanal | domingo | 02:00–06:00 | 00:00–02:00, 06:00–24:00 | — | — |
| continental | inverno | semanal | segunda_a_sexta | 02:00–06:00 | 00:00–02:00, 06:00–07:00 | 07:00–09:30, 12:00–18:30, 21:00–24:00 | 09:30–12:00, 18:30–21:00 |
| continental | inverno | semanal | sábado | 02:00–06:00 | 00:00–02:00, 06:00–09:30, 13:00–18:30, 22:00–24:00 | 09:30–13:00, 18:30–22:00 | — |
| continental | inverno | semanal | domingo | 02:00–06:00 | 00:00–02:00, 06:00–24:00 | — | — |
| continental | verão | diário | all days | 02:00–06:00 | 00:00–02:00, 06:00–08:00, 22:00–24:00 | 08:00–10:30, 13:00–19:30, 21:00–22:00 | 10:30–13:00, 19:30–21:00 |
| continental | inverno | diário | all days | 02:00–06:00 | 00:00–02:00, 06:00–08:00, 22:00–24:00 | 08:00–09:00, 10:30–18:00, 20:30–22:00 | 09:00–10:30, 18:00–20:30 |
| continental | verão | semanal_opcional | segunda_a_sexta | 02:00–06:00 | 00:30–02:00, 06:00–07:30 | 00:00–00:30, 07:30–14:00, 17:00–24:00 | 14:00–17:00 |
| continental | verão | semanal_opcional | sábado | 03:30–07:30 | 00:00–03:30, 07:30–10:00, 13:30–19:30, 23:00–24:00 | 10:00–13:30, 19:30–23:00 | — |
| continental | verão | semanal_opcional | domingo | 04:00–08:00 | 00:00–04:00, 08:00–24:00 | — | — |
| continental | inverno | semanal_opcional | segunda_a_sexta | 02:00–06:00 | 00:30–02:00, 06:00–07:30 | 00:00–00:30, 07:30–17:00, 22:00–24:00 | 17:00–22:00 |
| continental | inverno | semanal_opcional | sábado | 03:00–07:00 | 00:00–03:00, 07:00–10:30, 12:30–17:30, 22:30–24:00 | 10:30–12:30, 17:30–22:30 | — |
| continental | inverno | semanal_opcional | domingo | 04:00–08:00 | 00:00–04:00, 08:00–24:00 | — | — |
| ra_açores | verão | diário | all days | 01:30–05:30 | 00:00–01:30, 05:30–08:00, 22:00–24:00 | 08:00–09:00, 11:30–19:30, 21:00–22:00 | 09:00–11:30, 19:30–21:00 |
| ra_açores | inverno | diário | all days | 01:30–05:30 | 00:00–01:30, 05:30–08:00, 22:00–24:00 | 08:00–09:30, 11:00–17:30, 20:00–22:00 | 09:30–11:00, 17:30–20:00 |
| ra_açores | verão | diário_opcional | all days | 01:30–05:30 | 00:00–01:30, 05:30–08:00, 22:00–24:00 | 08:00–09:00, 11:30–19:30, 21:00–22:00 | 09:00–11:30, 19:30–21:00 |
| ra_açores | inverno | diário_opcional | all days | 01:30–05:30 | 00:00–01:30, 05:30–08:00, 22:00–24:00 | 08:00–17:00, 21:00–22:00 | 17:00–21:00 |
| ra_açores | junho_outubro | semanal | segunda_a_sexta | — | 00:00–07:00 | 07:00–10:30, 15:30–24:00 | 10:30–15:30 |
| ra_açores | junho_outubro | semanal | sábado | — | 00:00–11:00, 14:30–19:30, 23:00–24:00 | 11:00–14:30, 19:30–23:00 | — |
| ra_açores | junho_outubro | semanal | domingo | — | 00:00–24:00 | — | — |
| ra_açores | novembro_maio | semanal | segunda_a_sexta | — | 00:00–07:00 | 07:00–18:30, 21:30–24:00 | 18:30–21:30 |
| ra_açores | novembro_maio | semanal | sábado | — | 00:00–11:30, 13:30–18:00, 23:00–24:00 | 11:30–13:30, 18:00–23:00 | — |
| ra_açores | novembro_maio | semanal | domingo | — | 00:00–24:00 | — | — |
| ra_madeira | verão | diário | all days | 02:00–06:00 | 00:00–02:00, 06:00–09:00, 23:00–24:00 | 09:00–10:30, 13:00–20:30, 22:00–23:00 | 10:30–13:00, 20:30–22:00 |
| ra_madeira | inverno | diário | all days | 02:00–06:00 | 00:00–02:00, 06:00–09:00, 23:00–24:00 | 09:00–10:30, 12:00–18:30, 21:00–23:00 | 10:30–12:00, 18:30–21:00 |
| ra_madeira | verão | diário_opcional | all days | 02:00–06:00 | 00:00–02:00, 06:00–09:00, 23:00–24:00 | 09:00–10:30, 13:00–20:30, 22:00–23:00 | 10:30–13:00, 20:30–22:00 |
| ra_madeira | inverno | diário_opcional | all days | 02:00–06:00 | 00:00–02:00, 06:00–09:00, 23:00–24:00 | 09:00–18:00, 22:00–23:00 | 18:00–22:00 |
| ra_madeira | junho_outubro | semanal | segunda_a_sexta | — | 00:00–07:00 | 07:00–11:00, 14:00–20:00, 22:00–24:00 | 11:00–14:00, 20:00–22:00 |
| ra_madeira | junho_outubro | semanal | sábado | — | 00:00–11:00, 14:30–19:30, 23:00–24:00 | 11:00–14:30, 19:30–23:00 | — |
| ra_madeira | junho_outubro | semanal | domingo | — | 00:00–24:00 | — | — |
| ra_madeira | novembro_maio | semanal | segunda_a_sexta | — | 00:00–07:00 | 07:00–19:00, 22:00–24:00 | 19:00–22:00 |
| ra_madeira | novembro_maio | semanal | sábado | — | 00:00–11:30, 14:00–18:00, 22:30–24:00 | 11:30–14:00, 18:00–22:30 | — |
| ra_madeira | novembro_maio | semanal | domingo | — | 00:00–24:00 | — | — |

## Verification results

- Standard mainland daily and weekly schedules match every official interval in both seasons.
- The source-backed tests check period labels and exact interval bounds for every minute of all seven weekdays, across both seasons and all eight supported cycles: 161,280 minute checks.
- Full test suite: 120 passed; branch-inclusive coverage 92.98%. Ruff checks and formatting passed. Wheel and source distribution build and strict metadata validation passed using installed build dependencies.
- Super vazio and vazio normal are combined as vazio by `Plano` for BTN bi/tri-hourly tariffs.

## Limits and findings

- Regional support added: all Azores/Madeira daily, optional daily, and weekly schedules in the extraction are implemented. Mainland optional weekly cycles remain unsupported.
- Mainland timezone-aware timestamps are interpreted using their supplied clock fields, without conversion to Europe/Lisbon. At `2026-07-06 07:30 UTC`, the daily cycle returns vazio normal; the same instant in Lisbon (`08:30 WEST`) returns cheias. Callers must supply mainland local time. Default mainland calls use the host's local time. Regional cycles convert aware timestamps to Atlantic/Azores or Atlantic/Madeira; regional plan defaults use that regional timezone.
- Seasonal selection switches at midnight on the last Sundays of March and October. The chart JSON does not specify the precise switch instant, so the source-backed tests do not certify behavior during the clock-change hours.
- ERSE announces new mainland schedules from 1 April 2027 for BTE/MT/AT/MAT, and migration between 1 July and 31 December 2027 for BTN bi/tri-hourly installations. The current implementation has no effective-date or meter-migration selection for these future schedules.
- This audit covers time-of-use cycles and their classification, not prices, taxes, or invoice calculation. The regional extension adds six cycle classes and plan integration.
