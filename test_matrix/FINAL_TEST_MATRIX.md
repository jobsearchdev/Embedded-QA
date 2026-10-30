# Final Test Matrix — ESP32 IoT Sensor/Actuator Node

Кожен рядок пов'язує ризик із тестом, середовищем, очікуваним результатом, доказом і фактичним статусом.
Ризики описано в [MASTER_TEST_PLAN.md §7](../master_test_plan/MASTER_TEST_PLAN.md#7-quality-risks), докази — в [EVIDENCE_INDEX.md](../evidence/EVIDENCE_INDEX.md), дефекти — в [BUG_REPORTS.md](../portfolio/BUG_REPORTS.md).

Позначення: **Src** — тиждень курсу, з якого взято виконання. **Reg** — чи входить тест у regression (A — автоматизовано, M — вручну).

| ID | Risk | Pri | Level | Test / Method | Environment | Expected | Evidence | Reg | Status | Src |
|---|---|---|---|---|---|---|---|---|---|---|
| T01 | R01 | P1 | Recovery | `relay on` → `hang` → WDT reset → `status`, 4 цикли | Wokwi + Serial | `relay:false`, LED OFF після кожного аварійного reset | E04 | M | **FAIL** 4/4 → D-01 | W4 T14 |
| T02 | R01 | P1 | Interface | `SET LED ON` → `RESET` → `STATUS` (pytest) | Wokwi + Pytest | `led:false, pwm:0` | E02, E13 | A | **FAIL** → D-02 | W5 |
| T03 | R01 | P1 | Recovery | `reboot` vs `powerloss` → `status` | Wokwi + Serial | аварійний reset відрізняється від штатного | E04 | M | **FAIL** → D-30 | W4 T21 |
| T04 | R02 | P1 | Reliability | `relay on`, `save`, `powerloss` ×6, `status` після кожного | Wokwi + Serial | state = старий (N) або новий повний; перерваний запис виявлено при boot | E06 | M | **FAIL** 6/6, counter 2 → 602 → D-03 | W4 T17–T19 |
| T05 | R02 | P1 | Component | code review `saveState()` | source | один атомарний запис (blob + CRC / A-B) | E06 | — | **FAIL** → D-10 | W4 T20 |
| T06 | R03 | P1 | Reliability | `STRESS 100` ×10 у CONNECTED, heap після кожної ітерації | Wokwi + Serial + log_checks | heap коливається біля baseline, без тренду | E07, E12 | A | **FAIL** −8000 B/ітерацію, 10/10 → D-04 | W6 D |
| T07 | R03 | P1 | Recovery | heap після 4 циклів WDT recovery | Wokwi + Serial | heap стабільний | E04 | M | PASS (336332 після кожного) | W4 |
| T08 | R04 | P1 | Network | `NET DOWN` → `SEND`×5 → `NET UP` | Wokwi + Serial | queued 1..5, flush, кожен ID ×1, `duplicates=0` | E08 | A | буферизація PASS; дублікати **FAIL** → D-11 | W6 B |
| T09 | R04 | P1 | Boundary | `SEND` ×8 / ×9 / ×12 офлайн | Wokwi + Serial + log_checks | count ≤ 8; DROP_OLDEST; `dropped` = кількість відкинутих; 8 найновіших ID ×1 | E08, E12 | A | 8 — PASS; 9 і 12 — **FAIL** (`count=12/8`, `dropped=0`) → D-05, D-24 | W6 C |
| T10 | R04 | P1 | Network | підрахунок `publish id` по всьому логу | log_checks | кожен ID рівно 1 раз | E08, E12 | A | **FAIL**: 37 ID повторено, до ×6 | W6 |
| T11 | R05 | P1 | Protocol / fault injection | FAULT ON (NACK на 0x69) → FAULT OFF, 3 прогони, VCD | Wokwi + LA + PulseView | помилка логується, retry/timeout, main loop живий, обмін відновлюється | E05 | M | **FAIL** 3/3: вічне зависання → D-06 | W3.2 |
| T12 | R05 | P1 | Recovery | `hang` → час до reset, `reset_reason` | Wokwi + Serial | reset ≤ 5 с, `TASK_WDT` | E04 | M | **FAIL** ≈ 9.4 с, `INT_WDT` → D-14 | W4 T13 |
| T13 | R05 | P1 | Recovery | `hang` → recovery, 4 цикли | Wokwi + Serial | один `[BOOT]` на hang, команди працюють | E04 | M | PASS 4/4, boot loop немає | W4 T15–T16 |
| T14 | R05 | P1 | Network / recovery | `NET DOWN` → `NET UP` | Wokwi + Serial | CONNECTED, LED ON, буфер відправлено | E11 | A | PASS | W6 A |
| T15 | R06 | P2 | Interface (length) | рядок 39 / 40 / 41 / 54 / 1000 символів | Wokwi UART | N ≤ 40 — обробка; N+1 — `ERROR: command too long` без reboot | E03 | M | **FAIL** на 41: SYSTEM FAULT → D-07 | W3.1 |
| T16 | R06 | P2 | Interface (state) | `set` у стані CONFIG=DIRTY | Wokwi UART | `ERROR: unknown command`, зміни збережено | E03 | M | **FAIL** 100 %: fault + втрата конфігурації → D-08 | W3.1 |
| T17 | R06 | P2 | Boundary | `set speed` −1/0/255/256/…; `set timeout` −1/0/1/60/61 | Wokwi UART | лише 0..255 / 1..60 | E03 | M | **FAIL** на 256 і 0 → D-21, D-22 | W3.1 |
| T18 | R06 | P2 | Interface | Pytest negative: PWM поза діапазоном, не-число, невідомі команди (19 кейсів) | Wokwi + Pytest | `ERROR` / `INVALID_VALUE` / `UNKNOWN_COMMAND`, стан не змінюється | E02 | A | PASS 19/19 | W5 |
| T19 | R06 | P2 | Boundary | `SET PWM 0..100` (pytest) | Wokwi + Pytest | 0 і 100 приймаються | E02 | A | **FAIL** на 100 → D-19 | W5 |
| T20 | R06 | P2 | Protocol | `GET TEMP` — валідний JSON | Wokwi + Pytest | парситься `json.loads` | E02 | A | **FAIL**: немає `}` → D-18 | W5 |
| T21 | R06 | P2 | Interface | `PING`, timeout клієнта 1.0 с | Wokwi + Pytest | відповідь < 1 с | E02 | A | **FAIL**: 1.35 с → D-20 (REQ-Q1) | W5 |
| T22 | R07 | P2 | System | DHT22 від'єднано (дріт на GPIO13) → `sensor`, `status` | Wokwi + Serial | явна помилка, `sensor_ok:false`, без чисел | E09 | M | **FAIL**: `temp=0.0C` → D-13 | W4 T04 |
| T23 | R07 | P2 | System | датчик недоступний → реле не змінюється | Wokwi + Serial | relay OFF | E09 | M | PASS | W4 T05 |
| T24 | R08 | P2 | System | `sleep 1/5/10/60`, від `[STATE] SLEEP` до `rst:0x5` | Wokwi + Serial | тривалість ±15 % | E09 | M | **FAIL**: ≈ 1/10 від заданого → D-09; WDT під час сну → D-15 | W4 T08–T09 |
| T25 | R08 | P2 | System | дані після wake (`counter`, relay, heap) | Wokwi + Serial | дані збережені | E09 | M | PASS | W4 T10 |
| T26 | R08 | P2 | Negative | `sleep abc / 0 / -5 / 100`, `sleepy` | Wokwi + Serial | `[CLI] ERROR`, пристрій не засинає | E09 | M | **FAIL** → D-29 | W4 T12 |
| T27 | R09 | P3 | Network | `NET DOWN` 15 с, інтервали retry, `reconnect_attempts` | Wokwi + Serial + log_checks | інтервал зростає (експоненційний backoff) | E11, E12 | A | **FAIL**: медіана 50 мс, 192 спроби / 10 с → D-12 | W6 A |
| T28 | R09 | P3 | Network | state model: усі 4 стани досяжні та observable | Wokwi + Serial + log_checks | CONNECTED/DISCONNECTED/BACKOFF/CONNECTING | E11, E12 | A | PASS | W6 R1 |
| T29 | R10 | P3 | Component | 1 натискання з bounce; RAW (D0) vs LOGICAL (D1) | Wokwi + LA | 1 logical event | E10 | M | PASS (103/195 фронтів → 1 подія) | W2 TC-02 |
| T30 | R10 | P3 | System | NOISE під час critical operation, 5 прогонів | Wokwi + LA + Serial | 0 зайвих дій | E10 | M | **FAIL** 5/5 → D-17 | W2 TC-06/07 |
| T31 | R10 | P3 | Component | одиночний короткий імпульс NOISE | Wokwi + LA | не приймається як натискання | E10 | M | **FAIL** → D-16 | W2 TC-05 |
| T32 | R10 | P3 | System | 2 і 10 натискань кнопки, counter до/після | Wokwi + Serial | 1 подія на натиск | E09 | M | PASS (латентний ризик, O-01) | W4 T06–T07 |

## Підсумок за ризиками

| Risk | Pri | Тестів | PASS | FAIL | Висновок |
|---|---|---|---|---|---|
| R01 Actuator unsafe after reset | P1 | 3 | 0 | 3 | **не закритий** |
| R02 NVS corruption | P1 | 2 | 0 | 2 | **не закритий** |
| R03 Memory degradation | P1 | 2 | 1 | 1 | **не закритий** |
| R04 Data loss / duplicates | P1 | 3 | 0 | 3 | **не закритий** |
| R05 Hang without recovery | P1 | 4 | 2 | 2 | **не закритий** |
| R06 CLI robustness | P2 | 7 | 1 | 6 | **не закритий** |
| R07 Invalid sensor data | P2 | 2 | 1 | 1 | **не закритий** |
| R08 Sleep duration | P2 | 3 | 1 | 2 | **не закритий** |
| R09 Reconnect storm | P3 | 2 | 1 | 1 | **не закритий** |
| R10 Bounce / noise | P3 | 4 | 2 | 2 | **не закритий** |

Жоден ризик не закрито повністю. Тести зі статусом PASS показують, що працює (recovery без boot loop, state model, буферизація до межі 8, базовий debounce), і саме їх треба зберегти в регресії після виправлень.
