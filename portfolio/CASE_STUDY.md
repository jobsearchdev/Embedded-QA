# Embedded QA Portfolio Case Study — ESP32 IoT Sensor/Actuator Node

## 1. Project

IoT-вузол на ESP32: вимірює температуру й вологість (DHT22), керує реле, зберігає стан у NVS, має watchdog, deep sleep і передає телеметрію через Wi-Fi/MQTT з офлайн-буфером. Керується через UART CLI з JSON-відповідями.

Протягом курсу Embedded QA (IoT / DefTech, вересень–жовтень 2026) я тестував прошивку black-box методом у симуляторі Wokwi: шість buggy-збірок, кожна з яких відповідає окремій підсистемі.

## 2. My QA Goal

Відповісти команді: **чи можна ставити цю прошивку на пілот, а якщо ні, то що саме блокує реліз і що треба перевірити на реальному залізі.**

Тобто моє завдання — не «знайти якомога більше багів», а дати достатньо інформації для інженерного рішення.

## 3. System Overview

```
 DHT22 ─┐                                        ┌─▶ Relay (actuator)
 Button ┼─▶ ESP32: main loop / CLI / NVS / WDT ──┼─▶ LED
 I2C ───┘        │                               └─▶ Wi-Fi/MQTT ─▶ Broker
                 └── UART 115200 ◀──▶ Host (Serial monitor, Pytest)
```

Критичні дані: `counter` і `relay` у NVS, message ID телеметрії. Критичний актуатор: реле.
Залежності: брокер, живлення, хост для логування.
Повний опис: [MASTER_TEST_PLAN §2](../master_test_plan/MASTER_TEST_PLAN.md#2-system-overview).

## 4. Critical Risks

Я питав себе: що тут може нашкодити користувачу або непомітно зламати продукт?

| ID | Ризик | Чому критичний |
|---|---|---|
| R01 | Після аварійного reset реле стає ON | фізична небезпека, оператор не знає про це |
| R02 | Перерваний запис NVS дає змішаний state | пошкодження не видно, воно накопичується |
| R03 | Heap деградує з кожним повідомленням | гарантована відмова через години |
| R04 | Дані губляться або дублюються після reconnect | бекенд приймає рішення на неправдивих даних |
| R05 | Hang / збій периферії без recovery | потрібен виїзд для ручного перезапуску |

Ще п'ять ризиків (R06–R10) мають нижчий пріоритет. Усі десять — у [MTP §7](../master_test_plan/MASTER_TEST_PLAN.md#7-quality-risks).

## 5. Test Strategy

Кожен ризик перетворено на рівень, метод, середовище і тип доказу:

| Ризик | Рівень | Метод | Середовище | Evidence |
|---|---|---|---|---|
| R01 | Recovery | WDT fault injection (`hang`), `status` до/після | Wokwi + Serial | timestamped reset log |
| R02 | Reliability | `powerloss` ×6 + code review `saveState()` | Wokwi + Serial | таблиця state до/після |
| R03 | Reliability | `STRESS 100` ×10, тренд heap | Wokwi + Serial | Memory Stability Log |
| R04 | Network / boundary | буфер 8 / 9 / 12, підрахунок ID | Wokwi + Serial + log checks | message ID counts |
| R05 | Protocol / recovery | NACK на I2C, WDT | Wokwi + Logic Analyzer + PulseView | декодований трейс |

32 тести у [FINAL_TEST_MATRIX](../test_matrix/FINAL_TEST_MATRIX.md), кожен прив'язаний до ризику та evidence.

## 6. Key Scenarios

1. **Hang → WDT reset → recovery з увімкненим реле.** Recovery без boot loop працює (4/4), але реле щоразу повертається у ON (D-01).
2. **Power loss під час save, 6 циклів.** counter 2 → 102 → … → 602 без жодного підтвердженого запису і без перевірки цілісності при boot (D-03).
3. **Network stress 1000 повідомлень.** heap −8000 B на кожні 100, лінійно 10/10. Прогноз відмови — ≈ 9 год (D-04).
4. **Офлайн-буфер на межах 8 / 9 / 12.** Межа 8 — PASS; 9 і 12 — `count > capacity`, `dropped=0`, ID ×2…×6 (D-05, D-11).
5. **I2C NACK.** PulseView: одна транзакція 0x69 → NACK, далі шина мовчить 16 с; після зняття fault система не відновлюється (D-06).
6. **UART: рядок 41 символ.** На 41-му символі SYSTEM FAULT і reboot ще до Enter (D-07).

## 7. Automation

**Pytest suite (тиждень 5)** — [`automation/pytest_device/`](../automation/pytest_device): 39 тестів через pyserial / RFC2217: статус, сенсор, межі PWM, реле, негативні входи, timeout.
- Автоматизовано те, що повторюється після кожної зміни: протокол CLI, межі, негативні входи. Ручна перевірка тут повільна й нестабільна.
- Фікстура `clean_device` гарантує безпечний стан перед кожним тестом. Оскільки `RESET` дефектний (D-02), вона перевіряє стан через `STATUS` і вмикає fallback `SET LED OFF`.
- Кожне падіння класифіковано: firmware / requirement / test / communication / environment. Із 10 прогонів 3 повністю відкинуто як environment (Wokwi не відповідав).

**Log checks (тиждень 7)** — [`automation/log_checks/`](../automation/log_checks): pytest-перевірки, які аналізують збережений Serial-лог, а не живий пристрій.
- Перевіряють R1, R2, R4, R6, R7 мережевої ноди: стани, медіану retry, `count ≤ capacity`, облік `dropped`, унікальність ID, heap під STRESS.
- На buggy build результат: 1 PASS / 5 FAIL — збігається з ручним аналізом ([E12](../evidence/EVIDENCE_INDEX.md)).
- Навіщо: мережеві й memory-сценарії тривають хвилини, а висновок залежить від тисяч рядків логу. Перевірка за 0.14 с прибирає ручний підрахунок і дає однаковий критерій для кожного нового прогону.

Не автоматизовано, і це свідомо: fault injection з перемикачами Wokwi (I2C FAULT, кнопка), бо сценарій потребує керування симулятором, а не лише UART. Це наступний крок (див. §14).

## 8. Fault Injection

| Fault | Як введено | Як перевірено recovery |
|---|---|---|
| Firmware hang | CLI `hang` (нескінченний цикл без WDT feed) | час до `rst:`, `reset_reason`, один `[BOOT]` на hang, `status`, стан реле |
| Power loss під час запису | CLI `powerloss` | state до/після, наявність `[STORE] saved`, перевірка цілісності в boot log |
| I2C device failure | перемикач FAULT (GPIO27) → адреса 0x69 | UART heartbeat, активність шини у VCD після FAULT OFF |
| Network loss | `NET DOWN` / `NET UP` | state model, інтервали retry, flush буфера, LED |
| Sensor failure | дріт DHT22 перенесено з GPIO15 на GPIO13 | `sensor`, `sensor_ok`, стан реле |
| Input noise | NOISE через `scenario.yaml` | RAW (D0) vs LOGICAL (D1) у Logic Analyzer |

**Як я довів, що reset означає успішний recovery:** рівно один `[BOOT]` на кожен fault, після нього команди виконуються, heap не змінився, а актуатор у безпечному стані. Останню умову не виконано, тому recovery вважається неповним.

## 9. Evidence

14 артефактів у [EVIDENCE_INDEX](../evidence/EVIDENCE_INDEX.md). Найсильніші:

- **E04**: timestamped лог `hang → rst:0x8 → [BOOT] INT_WDT → "relay":true`
- **E05**: PulseView-трейс I2C, останній ACK і перший NACK
- **E07**: Memory Stability Log, 11 точок heap
- **E12**: автоматична перевірка логу (pytest output)
- **E02**: pytest + JUnit XML, 39 тестів

Відомі прогалини: сирі VCD не збережено, лог тижня 4 — лише у PDF.

## 10. Findings

**9 Critical · 14 Major · 7 Minor · 1 Observation** — [BUG_REPORTS](BUG_REPORTS.md).

| Finding | Impact |
|---|---|
| D-01 Реле ON після WDT reset | навантаження вмикається після збою без контролю |
| D-03 Змішаний state після power loss | пошкоджені дані приймаються як валідні й накопичуються |
| D-04 Витік heap 80 B / повідомлення | відмова вузла через ≈ 9 год |
| D-05 + D-11 Overflow і дублікати | тиха втрата частини даних, повторна відправка іншої, `dropped` завжди 0 |
| D-06 I2C NACK → вічне зависання | одна втрачена відповідь датчика вимагає виїзду |

Що працює: recovery без boot loop, state model мережі, буферизація до межі, базовий debounce, обробка невалідних числових аргументів у Pytest (19/19).

## 11. Regression

| Після зміни | Запускаємо |
|---|---|
| будь-якої | smoke `STATUS` ×3 + Pytest 39 |
| boot / NVS / relay | WDT ×10 з `relay on`, `powerloss` ×20 |
| network stack | сценарії A–D + `log_checks` по новому лозі |
| CLI parser | Pytest negative + довжини 39/40/41 + `set` у DIRTY |
| I2C driver | FAULT ON/OFF ×3 + PulseView |

Деталі — [MTP §13](../master_test_plan/MASTER_TEST_PLAN.md#13-regression-strategy).

## 12. Limitations

Симуляція **не доводить**:
- поведінку при реальному brown-out (`powerloss` моделює лише перерваний запис);
- bounce реальної кнопки (у Wokwi bounce замаскований `delay(25)`, 0/12 відтворень);
- реальний Wi-Fi і MQTT QoS (мережа — перемикач `NET DOWN/UP`);
- стабільність heap за 24–72 год (прогони тривали хвилини);
- точні таймінги (час симуляції ≠ реальний; виміряно за мітками Serial).

Модулі перевірялися на окремих навчальних збірках, тому інтеграційні ризики між ними не перевірені.

## 13. Release / Quality Conclusion

**NO-GO.** Відкрито 9 Critical-дефектів, які покривають усі п'ять P1-ризиків, і Exit Criteria EC2, EC4–EC10 не виконано. Рішення спирається на вплив відмов, а не на 82 % PASS у Pytest. [RELEASE_DECISION](../templates/RELEASE_DECISION.md)

## 14. What I Would Improve Next

1. Автоматизувати fault injection через Wokwi CLI / `scenario.yaml` (hang, powerloss, I2C FAULT) і додати ці сценарії в Pytest-регресію.
2. Прив'язати відповіді CLI до команд (request ID або очищення буфера перед кожною командою), щоб запізніла відповідь не зараховувалася наступному тесту.
3. Зберігати сирі VCD і логи як CI-артефакти, а не лише скріншоти у звітах.
4. Soak test 24 год із моніторингом `heap_caps_get_minimum_free_size`.
5. Стенд із реальним залізом: керований БЖ для brown-out, LA на реальній кнопці, справжній брокер.
