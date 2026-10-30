# Master Test Plan — ESP32 IoT Sensor/Actuator Node

| | |
|---|---|
| Автор | Evhenii Kofan |
| Версія | 1.0, 30.10.2026 |
| Build під тестом | `homework_buggy` (навчальні buggy-збірки курсу Embedded QA, тижні 2–6) |
| Пов'язані документи | [FINAL_TEST_MATRIX](../test_matrix/FINAL_TEST_MATRIX.md) · [EVIDENCE_INDEX](../evidence/EVIDENCE_INDEX.md) · [BUG_REPORTS](../portfolio/BUG_REPORTS.md) · [RELEASE_DECISION](../templates/RELEASE_DECISION.md) |

## 1. Document Purpose

Пристрій: IoT-вузол на ESP32. Він вимірює температуру й вологість (DHT22), керує реле, зберігає стан у NVS і передає телеметрію через Wi-Fi/MQTT з офлайн-буфером.

План має відповісти на одне питання: **чи можна випустити поточну прошивку на пілотну інсталяцію, і якщо ні, то що блокує реліз.**

План пов'язує ризики продукту з тестами, середовищами, доказами й критеріями виходу. Він не вимагає «перевірити все».

## 2. System Overview

```
             ┌──────────── ESP32 DevKit V1 ─────────────┐
 DHT22 ──GPIO15──▶ sensor read ─┐                       │
 Button ─GPIO4 ──▶ debounce ────┼─▶ main loop / state ──┼──GPIO5──▶ Relay (actuator)
 I2C dev ─GPIO21/22─▶ Wire ─────┘     │       │         ├──GPIO2──▶ LED (relay / NET)
                                       │       │         │
 Host PC ◀──UART0 115200──▶ CLI (JSON) │       ▼         │
                                       │   NVS: counter, relay
                                       ▼                 │
                          Task WDT 4 s → reset → boot    │
                          deep sleep (timer / ext0)      │
                                       │                 │
                          NET state machine ──Wi-Fi/MQTT──▶ Broker
                          offline buffer (capacity 8)    │
             └───────────────────────────────────────────┘
```

| Шар | Склад |
|---|---|
| Hardware | ESP32 DevKit V1, DHT22 (GPIO15), кнопка INPUT_PULLUP (GPIO4), реле (GPIO5), LED (GPIO2), I2C-периферія (SDA 21 / SCL 22) |
| Firmware | Arduino framework / PlatformIO; main loop, CLI parser, NVS (`Preferences`, namespace `qa-lab`), Task WDT 4000 ms, deep sleep, NET state machine (`CONNECTED → DISCONNECTED → BACKOFF ⇄ CONNECTING`), offline buffer |
| Interfaces | UART CLI 115200 (текстові команди, відповіді JSON); I2C; GPIO; Wi-Fi/MQTT (у симуляції — керування `NET DOWN/UP`) |
| External dependencies | MQTT-брокер / точка доступу; живлення; хост для логування та автоматизації |
| Critical data | `counter`, `relay` у NVS; телеметрія (message ID); лічильники `sent / dropped / duplicates` |
| Critical actuator | Реле: керує навантаженням, тому неконтрольоване ввімкнення є ризиком безпеки |

Життєвий цикл: boot → читання NVS → відновлення реле → WDT → loop (CLI, кнопка, мережа). З loop пристрій виходить через deep sleep, WDT reset або software reset, і кожен такий вихід веде знову до boot.

## 3. Quality Objectives

У порядку пріоритету:

1. **Safety.** Після будь-якого аварійного reset актуатор переходить у безпечний стан (OFF).
2. **Data integrity.** Persistent state є або старою, або новою повною версією; телеметрія не губиться й не дублюється без обліку.
3. **Recovery.** Пристрій сам виходить зі збою (hang, I2C fault, втрата мережі) без ручного перезапуску.
4. **Long-run stability.** Heap не деградує систематично під навантаженням.
5. **Robustness of interfaces.** Некоректний ввід CLI дає контрольовану помилку, а не reset чи зміну конфігурації.
6. **Observability.** `status` і логи правдиво відображають стан, щоб QA міг діагностувати збій.

## 4. Scope

| Область | Що перевіряємо | Рівень |
|---|---|---|
| Input / GPIO | debounce кнопки, шум під час critical operation | component, system |
| UART CLI | positive/negative, BVA, довжина рядка, формат JSON | interface |
| I2C | поведінка при NACK, recovery після зняття fault | protocol, recovery |
| Sensor | валідні дані, відмова датчика | system |
| Actuator safety | стан реле після WDT reset, `RESET`, `reboot` | recovery |
| Watchdog | час спрацювання, recovery, відсутність boot loop | recovery / fault injection |
| Persistence | цілісність NVS після перерваного запису | reliability |
| Power mode | тривалість deep sleep, wake-up, дані після wake | system |
| Network | state model, backoff, offline buffer, overflow, duplicates | network |
| Memory | heap trend під навантаженням | reliability |
| Automation | Pytest-регресія CLI; автоматична перевірка логів | regression |

## 5. Out of Scope

| Що не тестуємо | Чому | Де закрити |
|---|---|---|
| RF / реальна якість Wi-Fi, RSSI, втрати пакетів | Wokwi моделює мережу перемикачем `NET DOWN/UP` | real network bench |
| Brown-out, поріг BOD, справжній обрив живлення | `powerloss` лише імітує перерваний запис | стенд із керованим живленням |
| Знос Flash, обрив посередині сторінки | у симуляції немає фізики Flash | real hardware, endurance |
| Споживання струму в deep sleep | симулятор не вимірює струм | power analyzer |
| EMI/EMC, температурна кваліфікація | потребує лабораторії | сертифікаційна лабораторія |
| Точність DHT22 | у Wokwi значення задаються вручну | calibration bench |
| Справжній MQTT (QoS, ACK, брокер) | у симуляції брокер — модель | integration environment |
| OTA, безпека, автентифікація | не входить у вимоги навчального продукту | окремий план |

Out of Scope — свідоме обмеження стратегії. Кожен пункт переходить у Residual Risks (розділ 16).

## 6. Assumptions / Constraints

- **Один продукт, кілька навчальних збірок.** Модулі перевірялися на окремих buggy-збірках курсу: input (тиж. 2), UART CLI (3.1), I2C (3.2), core controller (4), CLI JSON + Pytest (5), network node (6). У цьому плані вони розглядаються як підсистеми одного вузла. Інтеграційні ризики між модулями (наприклад, мережевий цикл + запис NVS) не перевірялися.
- **Black-box.** Висновки зроблено зі спостережуваної поведінки (Serial, `status`, LED, трейси). Код переглядався лише для гіпотез і code review атомарності запису (T20).
- **Симуляція.** Wokwi for VS Code 4.1.0 + PlatformIO 6.2.0, macOS / Apple M3. Час симуляції може відставати від реального, тому таймінги виміряно за мітками Serial Monitor (`monitor_filters = time`).
- **Logic analyzer.** Wokwi Logic Analyzer → VCD → PulseView (декодер I2C).
- **Нестабільність середовища.** Wokwi RFC2217 періодично «підвисає» (тиж. 5: прогони 2, 4, 5 без відповідей). Через це перед кожним прогоном потрібен smoke-тест `STATUS`.
- **Реального заліза немає.** Усі «PASS» означають «PASS у симуляції».

## 7. Quality Risks

Формула ризику: **failure mode → impact**. Probability оцінено за фактичною відтворюваністю в тестах. Priority = Impact × Probability.

| Risk ID | Risk (failure mode → impact) | Impact | Probability | Priority | Mitigation / Test |
|---|---|---|---|---|---|
| R01 | Після аварійного reset або `RESET` реле залишається/стає ON → навантаження ввімкнене без контролю | Critical | High (4/4) | **P1** | WDT fault injection + `status` до/після; Pytest `test_reset_restores_safe_state` |
| R02 | Перерваний запис NVS залишає змішаний state, який приймається як валідний → неузгоджені дані після reboot | Critical | High (6/6) | **P1** | `powerloss` ×6, порівняння state; code review атомарності |
| R03 | Heap систематично зменшується на кожне повідомлення → відмова вузла через години роботи | Critical | High (10/10) | **P1** | Network stress + Memory Stability Log; автоматична перевірка тренду |
| R04 | При overflow / reconnect дані губляться без обліку або дублюються → бекенд отримує неправдиві дані | Critical | High (5/5) | **P1** | Offline buffer B/C, boundary 8/9/12, підрахунок publish ID |
| R05 | Збій периферії або hang без recovery → пристрій недоступний до ручного втручання | Critical | High (3/3) | **P1** | I2C NACK fault injection + PulseView; `hang` → WDT; цикли recovery |
| R06 | Некоректний або задовгий ввід CLI викликає reset чи мовчки змінює конфігурацію | High | High | **P2** | BVA / negative / length N±1; Pytest negative suite |
| R07 | Невалідні дані датчика подаються як валідні → хибні рішення автоматики | High | High | **P2** | Від'єднання DHT22; перевірка `sensor` і `sensor_ok` |
| R08 | Неправильна тривалість deep sleep → розряд батареї, пропущені цикли | High | High | **P2** | `sleep N` з timestamp-вимірами, допуск ±15 % |
| R09 | Reconnect storm (retry без backoff) → навантаження на брокер і батарею, особливо при масовій відмові | Medium | High (3/3) | **P3** | NET DOWN 15 с, інтервали retry, `reconnect_attempts` |
| R10 | Bounce / шум на кнопці створює зайву logical event → зайва дія актуатора, зайві записи Flash | Medium | Medium | **P3** | Logic analyzer RAW vs LOGICAL; 5 прогонів шуму під час critical operation |

Чому R01–R05 мають P1: вони ведуть або до небезпечного фізичного стану, або до тихої втрати чи підміни даних, або до відмови без самовідновлення. Жоден із них не можна компенсувати ручним обходом у полі.

## 8. Test Levels

| Рівень | Що перевіряється | Приклад з проєкту |
|---|---|---|
| Component / firmware function | одна функція у відриві від системи | debounce (RAW vs LOGICAL), парсер CLI, `saveState()` (code review) |
| Interface / protocol | обмін через інтерфейс | UART JSON-відповіді; I2C ACK/NACK у PulseView |
| System | наскрізна поведінка пристрою | sensor → status; sleep → wake → дані |
| Recovery / fault injection | реакція на штучний збій | `hang` (WDT), `powerloss`, FAULT на I2C, `NET DOWN` |
| Network | state machine, буфер, дублікати | сценарії A–D тижня 6 |
| Regression | повторний запуск після змін | Pytest suite (39 тестів) + `log_checks` |

Не кожен ризик потребує всіх рівнів. Наприклад, для R04: component — логіка DROP_OLDEST, network — сценарії overflow, regression — автоматична перевірка `publish id` у лозі.

## 9. Test Types

| Тип | Ризики |
|---|---|
| Functional | R07, R08 |
| Boundary / negative | R04 (буфер 8/9/12), R06 (BVA, N±1), R08 (`sleep 0/-5/abc`) |
| Protocol | R05 (I2C), R06 (формат JSON) |
| Reliability | R02, R03 |
| Recovery | R01, R05, R09 |
| Persistence | R02 |
| Network stress | R03, R04, R09 |
| Memory stability | R03 |
| Automation | R01, R06 (Pytest); R03, R04, R09 (log checks) |

## 10. Test Environment

| Environment | Purpose | Tools | Що може довести | Чого не може довести |
|---|---|---|---|---|
| Wokwi | firmware/system simulation, fault injection | Wokwi for VS Code 4.1.0, PlatformIO 6.2.0, ESP32 DevKit V1 | логіку станів, recovery, обробку помилок, формат протоколу | електрику, RF, реальні таймінги, знос Flash |
| Serial logging | timestamped evidence | PlatformIO monitor, `monitor_filters = time, log2file` | послідовність подій і таймінги з точністю до мс (у часі симуляції) | що відбувається між рядками логу |
| Logic analysis | protocol evidence | Wokwi Logic Analyzer → VCD → PulseView | ACK/NACK, адреси, активність шини, RAW-фронти | аналогові рівні, rise time |
| Host automation | regression | Python 3.14, pytest 9.2, pyserial 3.5 (RFC2217) | повторюваність відомих сценаріїв | нові, ще не описані сценарії |
| Log analysis | автоматична перевірка evidence | `automation/log_checks/` (Python + pytest) | що лог відповідає вимогам R1–R7 | коректність самого логування |
| Real hardware | electrical/physical validation | **недоступний** (план: DevKit + реле + DHT22 + керований БЖ) | brown-out, bounce реальної кнопки, Wi-Fi, heap за 24–72 год | — |

## 11. Entry Criteria

Тестування починається, коли виконано всі умови:

1. Збірка компілюється, версія або ідентифікатор build зафіксовані.
2. Вимоги для модуля доступні (REQ/R-list), відкриті питання записані (REQ-Q1, REQ-Q2).
3. Середовище записане: `00_environment.txt` (ОС, IDE, PlatformIO, Wokwi, параметри монітора).
4. Логування з мітками часу ввімкнене (`monitor_filters = time, log2file`).
5. Smoke-тест пройдено: boot → `STATUS` повертає валідний JSON протягом 1 с, і це повторюється 3 рази поспіль.
6. Для автоматизації: пристрій відповідає на `STATUS` до старту pytest, фікстура `clean_device` приводить його в безпечний стан.

Якщо smoke не проходить, прогін вважається **environment failure** і не зараховується до результатів (як прогони 2, 4, 5 тижня 5).

## 12. Exit Criteria

Вимірювані умови, за яких можна говорити про GO:

| # | Criterion | Target |
|---|---|---|
| EC1 | Critical (P1) тести виконано | 100 % |
| EC2 | Відкриті Critical-дефекти | 0 |
| EC3 | Відкриті Major-дефекти без погодженого workaround | 0 |
| EC4 | Actuator safety: реле OFF після WDT reset / `RESET` | 10/10 циклів |
| EC5 | Persistence: після `powerloss` state = старий або новий повний | 20/20 циклів, 0 змішаних |
| EC6 | Recovery після hang / I2C fault без ручного reset | 10/10, reset ≤ 5 с |
| EC7 | Memory: heap після 1000 повідомлень | падіння ≤ 1 % від baseline, без лінійного тренду |
| EC8 | Network: кожен message ID доставлено рівно 1 раз; при overflow `dropped` = фактична кількість відкинутих | 0 дублікатів, 0 неврахованих втрат |
| EC9 | Backoff: медіана інтервалу retry | ≥ 500 мс і зростає |
| EC10 | Регресія (Pytest + log checks) | 100 % PASS, 0 ERROR, 3 прогони поспіль |
| EC11 | Evidence | є для кожного Critical/Major finding і кожного P1-ризику |

## 13. Regression Strategy

Регресія не означає «запустити все». Набір вибирається за тим, що змінилося.

| Зміна в прошивці | Обов'язковий regression | Як |
|---|---|---|
| Будь-яка | Smoke (`STATUS` ×3) + Pytest suite (39 тестів) | автоматично |
| Boot / NVS / relay | R01, R02: WDT ×10 з `relay on`; `powerloss` ×20; `reboot` vs `powerloss` | вручну + Serial log |
| Network stack / буфер | R03, R04, R09: сценарії A–D; `log_checks` по новому лозі | напівавтоматично |
| CLI parser | R06: Pytest negative + довжини 39/40/41 + `set` у стані DIRTY | автоматично + вручну |
| Драйвер I2C / Wire | R05: FAULT ON/OFF ×3 + PulseView | вручну |
| Input / ISR | R10: 5 прогонів шуму під час critical operation + LA | вручну |
| Таймери / sleep | R08: `sleep 5/10/60` із timestamp | вручну |

Пріоритет при обмеженому часі: спочатку P1-ризики, яких стосується зміна, потім smoke + Pytest, потім решта.

## 14. Evidence Strategy

Evidence добирається під конкретне твердження (claim). Скріншот без контексту — слабкий доказ.

| Тип finding | Достатній evidence | Приклад |
|---|---|---|
| Зміна стану / послідовність подій | timestamped Serial log + `status` до/після | E04: `relay:true` після `INT_WDT` |
| Таймінг | дві мітки часу з одного логу, ≥ 3 виміри | E09: `sleep 10` → 1.03–1.04 с (6 вимірів) |
| Протокол | VCD + декодований трейс PulseView | E05: 0x69 W → NACK, далі шина idle |
| Цілісність даних | таблиця значень до/після для кожного циклу | E06: counter 2 → 102 → … → 602 |
| Втрата / дублікати | підрахунок ID з логу (`grep \| uniq -c` або `log_checks`) | E08: 37 ID опубліковано > 1 разу |
| Деградація пам'яті | тренд ≥ 10 точок, а не одне значення heap | E07: −8000 B на кожні 100 повідомлень |
| Регресія | pytest output + JUnit XML | E02: 39 тестів, 32 PASS / 7 FAIL |
| Шум / bounce | LA: RAW (D0) vs LOGICAL (D1) + лічильники | E10: 103/195 фронтів, D1 змінився 1 раз |

Правило: інша людина має змогу перевірити висновок за evidence без автора.

## 15. Defect Management

| Severity | Визначення | Приклад |
|---|---|---|
| Critical | небезпечний стан актуатора, тиха втрата або підміна даних, відмова без самовідновлення | D-01 реле ON після WDT |
| Major | порушення вимоги з функціональним впливом, є обхідний шлях | D-11 дублікати після reconnect |
| Minor | вплив на діагностику або зручність | D-24 лог overflow вводить в оману |
| Observation | підозра, яка не відтворилася; латентний ризик | debounce у тиж. 4 (0/12) |

Кожен bug report містить: preconditions, steps, expected/actual, reproducibility (N/M), severity з обґрунтуванням впливу, evidence з мітками часу, гіпотезу (окремо від фактів).

Класифікація падіння тесту: firmware / requirement / test / communication / environment (тиж. 5). Тільки firmware і requirement потрапляють у реєстр дефектів.

Retest: виправлений дефект закривається, коли той самий сценарій пройшов 3/3 і відповідний regression-набір з розділу 13 теж пройшов.

## 16. Residual Risks

| Residual risk | Чому залишається | Що потрібно |
|---|---|---|
| Реальний brown-out під час `saveState()` | `powerloss` моделює лише один тип переривання; вікно 25 мс неможливо влучити CLI-командою | стенд із керованим БЖ, ≥ 100 відключень |
| Bounce реальної кнопки | у тиж. 4 bounce маскується `delay(25)` у `saveState()` (0/12 відтворень); коду debounce немає | осцилограф або LA на реальній кнопці |
| Реальна мережа та MQTT QoS | дублікати можуть з'являтися й на рівні протоколу | інтеграційний стенд із брокером |
| Heap за 24–72 год, фрагментація | прогони тривали хвилини | soak test із `heap_caps_get_minimum_free_size` |
| Масова відмова брокера (fleet) | тестувалася одна нода | кілька нод, перевірка jitter у backoff |
| Взаємодія модулів | модулі перевірялися на окремих збірках | інтеграційна збірка + повний regression |
| Знос Flash | кожне натискання кнопки записує NVS | оцінка кількості записів на день × ресурс Flash |

## 17. Release Recommendation

**NO-GO.**

Відкрито 9 Critical-дефектів, і вони зачіпають усі P1-ризики (R01–R05). Exit Criteria EC2, EC4–EC9 не виконано. Повна аргументація — у [RELEASE_DECISION.md](../templates/RELEASE_DECISION.md).

Рішення ґрунтується не на відсотку PASS, а на характері відмов. Навіть 32/39 PASS у Pytest не змінюють висновку, бо серед 7 падінь є `RESET` з `pwm:255`, тобто небезпечний стан актуатора.
