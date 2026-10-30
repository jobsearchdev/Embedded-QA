# Bug Reports — ESP32 IoT Sensor/Actuator Node

У тижневих звітах дефекти мали локальні ID (BUG-01 тощо), які повторюються між тижнями. Тут вони зведені в єдиний реєстр з ID `D-xx`, а колонка **Source** вказує оригінальний ID.

Середовище для всіх: Wokwi for VS Code + PlatformIO, ESP32 DevKit V1, buggy-збірки курсу, Serial 115200, macOS / Apple M3 ([E01](../evidence/EVIDENCE_INDEX.md)).

## 1. Defect Register

**Разом: 9 Critical · 14 Major · 7 Minor · 1 Observation · 2 питання до вимог.**

| ID | Title | Severity | Risk | Repro | Source | Evidence |
|---|---|---|---|---|---|---|
| **D-01** | Після WDT reset реле відновлюється у ON | Critical | R01 | 4/4 | W4 BUG-02 | E04 |
| **D-02** | `RESET` не повертає безпечний стан (`pwm:255`) | Critical | R01 | 4 прогони | W5 BUG-04 | E02, E13 |
| **D-03** | Перерваний запис NVS дає змішаний state, який приймається як валідний | Critical | R02 | 6/6 | W4 BUG-03 | E06 |
| **D-04** | Витік heap ≈ 80 B на кожне повідомлення | Critical | R03 | 10/10 | W6 BUG-03 | E07, E12 |
| **D-05** | Overflow буфера без DROP_OLDEST: count > capacity, втрати без обліку | Critical | R04 | 3/3 | W6 BUG-04 | E08, E12 |
| **D-06** | Після I2C NACK система зависає назавжди | Critical | R05 | 3/3 | W3.2 | E05 |
| **D-07** | Рядок ≥ 41 символ викликає SYSTEM FAULT і reboot | Critical | R06 | 100 % | W3.1 BUG-01 | E03 |
| **D-08** | `set` у стані CONFIG=DIRTY викликає SYSTEM FAULT і втрату налаштувань | Critical | R06 | 100 % | W3.1 BUG-02 | E03 |
| **D-09** | `sleep N` триває ≈ N/10 секунд | Critical | R08 | Always | W4 BUG-01 | E09 |
| D-10 | `saveState()` неатомарний: два записи з `delay(25)` між ними | Major | R02 | static | W4 BUG-06 | E06 |
| D-11 | Після reconnect кожне буферизоване повідомлення публікується двічі | Major | R04 | 5/5 | W6 BUG-02 | E08, E12 |
| D-12 | Reconnect storm: retry кожні ~50 мс замість backoff | Major | R09 | 3/3 | W6 BUG-01 | E11, E12 |
| D-13 | Недоступний DHT22 показується як 0.0C / 0.0 % | Major | R07 | Always | W4 BUG-04 | E09 |
| D-14 | Reset після hang через ≈ 9.4 с замість ≤ 5 с, `INT_WDT` замість `TASK_WDT` | Major | R05 | 4/4 | W4 BUG-11 | E04 |
| D-15 | Під час `sleep` спрацьовує прихований WDT reset; wake кнопкою заблоковано | Major | R08 | Always | W4 BUG-10 | E09 |
| D-16 | Одиночний імпульс NOISE приймається як натискання (вікно ≈ 1 мс замість 30 мс) | Major | R10 | — | W2 BUG-01 | E10 |
| D-17 | NOISE під час critical operation створює зайву ACTION і перезапускає операцію | Major | R10 | 5/5 | W2 BUG-02 | E10 |
| D-18 | `GET TEMP` повертає невалідний JSON (без `}`) | Major | R06 | 4 прогони | W5 BUG-02 | E02 |
| D-19 | `SET PWM 100` відхиляється (off-by-one) | Major | R06 | 3 прогони | W5 BUG-03 | E02 |
| D-20 | `PING` відповідає за 1.35 с при timeout клієнта 1.0 с | Major | R06 | стабільно | W5 BUG-01 | E02 |
| D-21 | `set speed 256` мовчки обрізається до 255 | Major | R06 | 100 % | W3.1 BUG-03 | E03 |
| D-22 | `set timeout 0` приймається (діапазон 1..60) | Major | R06 | 100 % | W3.1 BUG-04 | E03 |
| D-23 | При швидкому потоці команд частина вводу губиться | Major | R06 | — | W3.1 BUG-07 | E03 |
| D-24 | Лог overflow вводить в оману: `dropped_total=0` | Minor | R04 | 3/3 | W6 BUG-05 | E08 |
| D-25 | Команда виконується по таймауту 1 с без Enter; ввід блокує мережевий цикл | Minor | R09 | 3/3 | W6 BUG-06 | E11 |
| D-26 | Ввід лише зі спецсимволів повертає `OK` | Minor (Medium у W3.1) | R06 | 100 % | W3.1 BUG-05 | E03 |
| D-27 | `STATUS` у верхньому регістрі приймається | Minor | R06 | 100 % | W3.1 BUG-06 | E03 |
| D-28 | Стан ACTIVE не логується при boot і записаний у `status` константою | Minor | R01 | Always | W4 BUG-07 | E04 |
| D-29 | Некоректні аргументи `sleep` приймаються мовчки | Minor | R08 | Always | W4 BUG-08 | E09 |
| D-30 | Reset після `powerloss` не відрізнити від штатного `reboot` | Minor | R01 | Always | W4 BUG-09 | E04 |
| O-01 | Debounce кнопки відсутній у коді, але в Wokwi не відтворився (0/12) | Observation | R10 | 0/12 | W4 BUG-05 | E09 |

Питання до вимог: **REQ-Q1** — максимальний час відповіді CLI не визначено (пропозиція: ≤ 500 мс). **REQ-Q2** — у яких одиницях `STATUS` повертає `pwm` (0..100 чи 0..255).

---

## 2. Детальні bug reports

Нижче — 4 Critical-дефекти, які найбільше впливають на release decision.

### D-01 — Після WDT reset реле відновлюється у ON

| Поле | Значення |
|---|---|
| Severity / Priority | **Critical / P1**: після збою прошивки навантаження вмикається без участі користувача |
| Risk | R01 Actuator unsafe after reset |
| Source | W4 BUG-02 (тест T14 → matrix T01) |
| Preconditions | ACTIVE; `relay on` виконано (`[STORE] saved`, LED світиться) |
| Steps | 1. `status` 2. `hang` 3. дочекатися `[BOOT] reset_reason=INT_WDT` 4. `status` 5. повторити 1–4 ще 3 рази |
| Expected | Після аварійного reset `"relay":false`, LED не світиться. Відновлення реле допустиме лише після штатного `reboot` чи wake. |
| Actual | `"relay":true`, LED світиться одразу після boot, 4 з 4 циклів |
| Reproducibility | 4/4 (Always) |
| Evidence | E04 |
| Hypothesis | `setup()` викликає `applyRelay(relayState)` зі значенням з NVS і не перевіряє reset reason |

```
15:12:58.663 > {"state":"ACTIVE","reset_reason":"POWER_ON","relay":false,"counter":0,...}
relay on
15:13:06.256 > [STORE] saved
15:13:06.256 > [RELAY] ON
hang
15:14:19.261 > [FAULT] firmware hang
15:14:23.439 > E (133088) task_wdt: Task watchdog got triggered. ...
15:14:28.714 > rst:0x8 (TG1WDT_SYS_RESET),boot:0x13 (SPI_FAST_FLASH_BOOT)
15:14:29.572 > [BOOT] reset_reason=INT_WDT
status
15:14:38.791 > {"state":"ACTIVE","reset_reason":"INT_WDT","relay":true,"counter":1,"heap":336332,"sensor_ok":true}
```

Пов'язані: D-02 (той самий клас помилки через CLI `RESET`), D-14 (довгий час до reset), D-30 (аварійний reset не відрізняється від штатного).

Retest після fix: T01 ×10, T02, T03; regression — Pytest suite.

### D-03 — Перерваний запис NVS дає змішаний state, який приймається як валідний

| Поле | Значення |
|---|---|
| Severity / Priority | **Critical / P1**: пошкоджені persistent data приймаються як валідні й накопичуються |
| Risk | R02 NVS corruption |
| Source | W4 BUG-03 (T17–T19 → matrix T04) |
| Preconditions | `relay on`, `save`; `status` показує counter = 2, relay = true |
| Steps | 1. `powerloss` 2. дочекатися boot 3. `status` 4. повторити 1–3 ще 5 разів |
| Expected | state = стара версія (N) або нова повністю записана; перерваний запис виявляється при boot і логується |
| Actual | counter = N+100 без `[STORE] saved` у кожному циклі; у boot log немає перевірки цілісності |
| Reproducibility | 6/6 |
| Evidence | E06 |
| Hypothesis | `simulateInterruptedSave()` фіксує лише `counter`; `setup()` читає NVS без версії, CRC чи commit-прапорця. Вікно для реального обриву — `delay(25)` між двома записами (D-10). |

| Цикл | `[FAULT] power loss DURING save` | counter після boot | relay | `[STORE] saved` |
|---|---|---|---|---|
| 1 | 15:22:06.763 | 102 | true | немає |
| 2 | 15:22:34.243 | 202 | true | немає |
| 3 | 15:22:45.832 | 302 | true | немає |
| 4 | 15:23:00.099 | 402 | true | немає |
| 5 | 15:23:11.848 | 502 | true | немає |
| 6 | 15:23:24.099 | 602 | true | немає |

Обмеження: `powerloss` — це fault injection у Wokwi, а не справжній brown-out. На реальному залізі ризик лише вищий (residual risk, MTP §16).

### D-04 — Витік heap ≈ 80 B на кожне повідомлення

| Поле | Значення |
|---|---|
| Severity / Priority | **Critical / P1**: вузол гарантовано відмовить через час, пропорційний кількості повідомлень |
| Risk | R03 Memory degradation |
| Source | W6 BUG-03 (Scenario D → matrix T06) |
| Preconditions | CONNECTED, `RESET STATS`, baseline heap = 347884 |
| Steps | 1. `STATUS` 2. (`STRESS 100` → `STATUS`) ×10 3. `NET DOWN` → `STRESS 20` → `NET UP` → `STATUS` |
| Expected | heap коливається біля baseline без систематичного падіння |
| Actual | −8000 ± 12 B на кожну ітерацію, між ітераціями пам'ять не повертається; витік є й офлайн (−1600 B за 20 повідомлень) |
| Reproducibility | 10/10 ітерацій + сценарії B, C |
| Evidence | E07, E12 (автоматична перевірка: `heap втрачає 8012 B за STRESS 100`) |
| Impact estimate | 266280 B / 80 B ≈ 3300 повідомлень; при телеметрії раз на 10 с — **≈ 9 годин** до відмови |

| Ітерація | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Free heap, B | 347884 | 339884 | 331884 | 323892 | 315880 | 307880 | 299880 | 291880 | 283880 | 275880 | 267880 |

Чому тренд, а не одне значення: одна точка heap не відрізняє витік від фрагментації чи кешу. 10 рівних кроків по −8000 B — лінійна систематична деградація.

### D-05 — Overflow буфера без DROP_OLDEST: count > capacity, втрати без обліку

| Поле | Значення |
|---|---|
| Severity / Priority | **Critical / P1**: дані втрачаються мовчки, старі дані надсилаються повторно, моніторинг показує неправду |
| Risk | R04 Data loss / duplicates |
| Source | W6 BUG-04 (+ симптоми D-11, D-24) (Scenario C → matrix T09) |
| Preconditions | CONNECTED, `RESET STATS` |
| Steps | 1. `NET DOWN` 2. `SEND` ×12 3. `BUFFER` 4. `STATUS` 5. `NET UP` 6. `STATUS` |
| Expected | count ≤ 8; `dropped=4` + запис у лозі; після flush — 8 найновіших ID (10–17) по одному разу; `sent=8, duplicates=0` |
| Actual | `count=12/8`; `dropped=0`; flush — 24 publish (14–17, 10–13, 14–17, кожен ×2); ID 6–9 зникли без обліку; `sent=24, duplicates=12` |
| Reproducibility | 3/3 (12, 9, STRESS 20 офлайн) |
| Evidence | E08, E12 |

```
14:48:18.014 > [BUFFER] queued id=13 count=8/8
14:48:19.741 > [BUFFER] overflow policy=DROP_OLDEST dropped_total=0
14:48:19.746 > [BUFFER] queued id=14 count=9/8
14:48:24.884 > [BUFFER] queued id=17 count=12/8
14:48:29.982 > [BUFFER] count=12 capacity=8 dropped=0
14:48:44.368 > [BUFFER] flush_start count=12
14:48:44.368 > [MQTT] publish id=14 … 17, 10 … 13, 14 … 17 (кожен ×2)
14:48:51.151 > {"net":"CONNECTED",...,"sent":24,"dropped":0,"duplicates":12,...,"heap":349244}
```

Межа 8 (ID 18–25) — PASS: overflow немає. Межа 9 — FAIL: `count=9/8`, ID 34 публікується ×4, ID 26 зник без обліку.
