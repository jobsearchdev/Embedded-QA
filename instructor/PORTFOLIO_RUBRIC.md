# Portfolio Rubric — самооцінка

Самооцінка за рубрикою курсу з посиланням на те, що підтверджує оцінку.

| Criterion | Excellent | Good | Weak | Самооцінка | Підстава |
|---|---|---|---|---|---|
| System | Clear architecture/dependencies | Mostly clear | Tool list instead of system | Excellent | [SYSTEM_OVERVIEW](../case_study/SYSTEM_OVERVIEW.md): схема, inputs/outputs, критичні дані, актуатор, залежності |
| Risks | Prioritized by impact | Risks listed | Tests disguised as risks | Excellent | MTP §7: «failure mode → impact», Impact × Probability, P1–P3 з обґрунтуванням |
| Strategy | Traceable to risks | Partial traceability | Random test collection | Excellent | [Test Matrix](../test_matrix/FINAL_TEST_MATRIX.md): кожен із 32 тестів → Risk → Evidence → Status |
| Evidence | Supports claims | Some useful evidence | Screenshots without context | Excellent | [Evidence Index](../evidence/EVIDENCE_INDEX.md): колонка «Claim» для кожного доказу, прогалини описано окремо |
| Scope | Explicit limitations | Some limitations | Claims simulator proves everything | Excellent | MTP §5, §6, §16; колонка «чого не може довести» у §10 |
| Decision | Evidence-based | Reasonable | Based on pass percentage | Excellent | [Release Decision](../templates/RELEASE_DECISION.md): NO-GO попри 82 % PASS, статус EC1–EC11 |

## Слабкі місця, які я знаю

- Модулі тестувалися на окремих навчальних збірках, тому інтеграцію не перевірено (MTP §6).
- Сирі VCD не збережено, є лише декодовані діаграми (Evidence Index → прогалини).
- Fault injection через перемикачі Wokwi не автоматизовано (Case Study §14).
