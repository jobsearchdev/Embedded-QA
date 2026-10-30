# Final Homework — статус виконання

Відповідність вимогам фінального завдання (HOMEWORK.md, Portfolio Review Sheet Webinar 8).

## Deliverables

| # | Вимога | Файл | Статус |
|---|---|---|---|
| 1 | Master Test Plan | [master_test_plan/MASTER_TEST_PLAN.md](../master_test_plan/MASTER_TEST_PLAN.md) | ✅ |
| 2 | Final Test Matrix | [test_matrix/FINAL_TEST_MATRIX.md](../test_matrix/FINAL_TEST_MATRIX.md) | ✅ 32 тести |
| 3 | Evidence Index + Evidence Package | [evidence/EVIDENCE_INDEX.md](../evidence/EVIDENCE_INDEX.md), `evidence/w0x_*` | ✅ E01–E14 |
| 4 | Portfolio README | [README.md](../README.md) | ✅ |
| 5 | Case Study | [portfolio/CASE_STUDY.md](../portfolio/CASE_STUDY.md) | ✅ |
| 6 | Release Decision | [templates/RELEASE_DECISION.md](../templates/RELEASE_DECISION.md) | ✅ NO-GO |
| — | 3+ Bug Reports | [portfolio/BUG_REPORTS.md](../portfolio/BUG_REPORTS.md) | ✅ реєстр 30 + 4 детальні |
| — | Pytest automation | [`automation/pytest_device/`](../automation/pytest_device/), [`automation/log_checks/`](../automation/log_checks/) | ✅ 39 + 6 тестів |
| — | QA Conclusion | README → Conclusion; RELEASE_DECISION → Rationale | ✅ |

## Master Test Plan — мінімальні вимоги

| Розділ | Де |
|---|---|
| System Overview | MTP §2, [case_study/SYSTEM_OVERVIEW.md](../case_study/SYSTEM_OVERVIEW.md) |
| Scope / Out of Scope | MTP §4–5 |
| Critical risks | MTP §7 (10 ризиків, 5 — P1) |
| Test Levels | MTP §8 |
| Test Environment (simulation vs real hardware) | MTP §10 |
| Entry / Exit Criteria | MTP §11–12 (EC1–EC11, вимірювані) |
| Regression Strategy | MTP §13 |
| Evidence Strategy | MTP §14 |
| Residual Risks | MTP §16 |

## Evidence з попередніх вебінарів

| Тип | Є | Evidence ID |
|---|---|---|
| Wokwi | ✅ | усі |
| Serial logs | ✅ | E03, E04, E09, E11 |
| Protocol traces / PulseView | ✅ | E05 (I2C), E10 (GPIO LA) |
| Python / Pytest | ✅ | E02, E12, E13 |
| Recovery logs | ✅ | E04, E06 |
| Network stress | ✅ | E08, E11 |
| Memory stability | ✅ | E07 |

## Практичний чек-лист

- [x] Описати System Overview
- [x] Визначити In Scope / Out of Scope
- [x] Скласти мінімум 5 quality risks (є 10)
- [x] Зв'язати кожен критичний risk із test type та evidence
- [x] Описати test environment і межі simulation vs real hardware
- [x] Визначити Entry / Exit Criteria
- [x] Зібрати evidence package та README Case Study
- [x] Підготувати 2–3 технічні рішення для співбесіди (Case Study §6–8: тренд heap, автоматична перевірка логів, класифікація падінь)
