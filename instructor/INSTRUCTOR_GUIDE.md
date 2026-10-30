# Reviewer Guide — як перевірити цю роботу

Маршрут для викладача або техліда: 5 хвилин на огляд, 15 — на перевірку висновків.

## 5 хвилин

1. [README.md](../README.md): продукт, 5 ризиків, ключові знахідки, NO-GO.
2. [templates/RELEASE_DECISION.md](../templates/RELEASE_DECISION.md): статус Exit Criteria та аргументація.
3. [test_matrix/FINAL_TEST_MATRIX.md](../test_matrix/FINAL_TEST_MATRIX.md): підсумок за ризиками внизу.

## 15 хвилин: перевірити ланцюжок Risk → Test → Evidence → Decision

Візьміть будь-який P1-ризик і пройдіть по ньому:

| Крок | R01 (приклад) | Де |
|---|---|---|
| Risk | реле ON після аварійного reset | MTP §7 |
| Test | T01: `relay on` → `hang` → `status`, 4 цикли | Test Matrix |
| Evidence | E04: `rst:0x8` → `INT_WDT` → `"relay":true` | Evidence Index → `evidence/w04_recovery_nvs/TEST_REPORT_W4.md` |
| Finding | D-01, Critical, 4/4 | portfolio/BUG_REPORTS.md |
| Decision | EC4 ❌ → NO-GO | RELEASE_DECISION |

## Відтворити автоматичну перевірку

```bash
pip install pytest
pytest -v automation/log_checks/        # очікувано: 1 passed, 5 failed (buggy build)
```

Вивід має збігатися з `evidence/w06_network/log_checks_result.txt`.

## Структура

| Папка | Вміст |
|---|---|
| `case_study/` | System Overview |
| `master_test_plan/` | Master Test Plan |
| `test_matrix/` | Final Test Matrix |
| `evidence/` | Evidence Index + артефакти за тижнями (`w01`…`w06`) |
| `portfolio/` | Case Study, Bug Reports |
| `templates/` | Release Decision |
| `homework/` | статус виконання вимог |
| `instructor/` | самооцінка за рубрикою, цей гайд |
| `automation/` | `pytest_device/` — Pytest suite CLI (тиж. 5); `log_checks/` — перевірка вимог по Serial-логу |
