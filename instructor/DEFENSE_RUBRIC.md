# Final Defense Rubric — самооцінка

Самооцінка за рубрикою курсу з посиланням на те, що підтверджує оцінку.

| Criterion | Excellent | Good | Weak | Самооцінка | Підстава |
|---|---|---|---|---|---|
| System | Clear architecture/dependencies | Mostly clear | Tool list instead of system | Excellent | [SYSTEM_OVERVIEW](../case_study/SYSTEM_OVERVIEW.md): схема, inputs/outputs, критичні дані, актуатор, залежності |
| Risks | Prioritized by impact | Risks listed | Tests disguised as risks | Excellent | MTP §7: «failure mode → impact», Impact × Probability, P1–P3 з обґрунтуванням |
| Strategy | Traceable to risks | Partial traceability | Random test collection | Excellent | [Test Matrix](../test_matrix/FINAL_TEST_MATRIX.md): кожен із 32 тестів → Risk → Evidence → Status |
| Evidence | Supports claims | Some useful evidence | Screenshots without context | Excellent | [Evidence Index](../evidence/EVIDENCE_INDEX.md): колонка «Claim» для кожного доказу, прогалини описано окремо |
| Scope | Explicit limitations | Some limitations | Claims simulator proves everything | Excellent | MTP §5, §6, §16; колонка «чого не може довести» у §10 |
| Decision | Evidence-based | Reasonable | Based on pass percentage | Excellent | [Release Decision](../templates/RELEASE_DECISION.md): NO-GO попри 82 % PASS, статус EC1–EC11 |
| Defense | Concise engineering story | Understandable | Tool/technology recital | Good → Excellent після репетиції | [Interview Brief](../templates/INTERVIEW_BRIEF.md): 90-секундна історія, таймінг, відповіді |

## Ваги (Instructor Manual §25)

| Критерій | Вага | Де закрито |
|---|---:|---|
| System understanding | 10 % | SYSTEM_OVERVIEW, MTP §2 |
| Scope / limitations | 10 % | MTP §4–6, §16 |
| Risk prioritization | 15 % | MTP §7 |
| Test Strategy / Matrix | 20 % | MTP §8–10, FINAL_TEST_MATRIX |
| Evidence quality | 15 % | EVIDENCE_INDEX, MTP §14 |
| Regression / Exit Criteria | 10 % | MTP §12–13 |
| Engineering conclusion | 10 % | RELEASE_DECISION |
| Portfolio defense | 10 % | INTERVIEW_BRIEF |

## Слабкі місця, які я знаю

- Модулі тестувалися на окремих навчальних збірках, тому інтеграцію не перевірено (MTP §6).
- Сирі VCD не збережено, є лише декодовані діаграми (Evidence Index → прогалини).
- Fault injection через перемикачі Wokwi не автоматизовано (Case Study §14).
