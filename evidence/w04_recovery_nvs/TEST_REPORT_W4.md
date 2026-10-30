# Test Report — ESP32 IoT Controller (Wokwi Homework)

Oct 26, 2026 · Evhenii Kofan

Прошивка `homework_buggy` не проходить 4 із 7 вимог: знайдено 3 Critical, 4 Major і 3 Minor дефекти, тож до релізу вона не готова.

Тестування виконано в симуляторі Wokwi (VS Code \+ PlatformIO) 26–27.10.2026. Фактичні Serial-логи наведено в розділах 5–10.

**Налаштування:** у `platformio.ini` додано `monitor_filters = time`, тож кожен рядок логу має часову мітку. За ними виміряно таймінги R4 та R5.

## 1\. System Overview

System under test: навчальний IoT-контролер на ESP32 DevKit V1 з прошивкою `homework_buggy` (Arduino framework, PlatformIO), який тестується в симуляторі Wokwi.

| Компонент | GPIO | Роль |
| :---- | :---- | :---- |
| DHT22 | 15 | Датчик температури та вологості |
| Кнопка (INPUT\_PULLUP, bounce увімкнено) | 4 | Перемикає реле; також джерело wake-up (ext0) |
| LED | 2 | Відображає стан реле |
| Relay module | 5 | Actuator |
| UART0 | TX0/RX0 | CLI, 115200 baud |
| NVS (Preferences, namespace `qa-lab`) | — | Persistent state: `counter`, `relay` |
| Task WDT | — | Timeout 4000 ms, panic → reset |

**CLI:** `help`, `status`, `sensor`, `relay on`, `relay off`, `save`, `sleep <N>`, `hang`, `powerloss`, `reboot`.

**Життєвий цикл:** boot → читання NVS → відновлення реле → увімкнення WDT → `loop` (CLI \+ кнопка). З `loop` пристрій виходить через deep sleep (`sleep`), WDT reset (`hang`) або software reset (`powerloss`, `reboot`), і кожен вихід веде знову до boot.

## 2\. Scope

Тестуємо функціональність і надійність за вимогами R1–R7, лише в симуляторі Wokwi.

**In scope**

- R1 Boot: перехід у ACTIVE і виведення reset reason.  
- R2: обробка відмови DHT22 (від'єднаний датчик).  
- R3: один натиск дає одну подію (з увімкненим bounce Wokwi).  
- R4: тривалість deep sleep, wake-up і цілісність даних після пробудження.  
- R5: watchdog fault injection (`hang`), recovery, безпечний стан актуатора, відсутність boot loop.  
- R6: цілісність NVS після перерваного запису (`powerloss`).  
- R7: повнота та коректність `status`.  
- Негативні входи CLI: невідомі команди та некоректні аргументи `sleep`.

**Out of scope**

- Реальний brown-out, поріг BOD, timing шин живлення. `powerloss` лише моделює переривання запису та reboot.  
- Фізична поведінка Flash/NVS: знос та обрив посередині сторінки Flash.  
- Споживання струму в deep sleep, RF/Wi-Fi, OTA, безпека.  
- Точність вимірювань DHT22 (у Wokwi значення задаються вручну).

**Обмеження Wokwi:** час симуляції може відставати від реального, тому виміри R4/R5 зроблено за часовими мітками Serial Monitor. Результати треба підтвердити на фізичному стенді перед релізом.

## 3\. Quality Risks

Найбільший ризик полягає в тому, що після аварійного reset актуатор переходить у небезпечний стан або працює з невалідними даними.

| ID | Ризик | Наслідок | Вимога | Пріоритет |
| :---- | :---- | :---- | :---- | :---- |
| QR1 | Після WDT/аварійного reset реле відновлюється у ON | Навантаження увімкнене без контролю, загроза безпеці | R5 | High |
| QR2 | Перерваний запис залишає частково оновлений state в NVS | Неузгоджені дані після reboot, пошкодження не виявляється | R6 | High |
| QR3 | Неправильна тривалість deep sleep | Перевитрата батареї або пропущені цикли вимірювання | R4 | High |
| QR4 | Невалідні дані датчика подаються як валідні | Хибні рішення автоматики, прихована відмова заліза | R2 | High |
| QR5 | Брязкіт контактів кнопки дає кілька подій | Реле в непередбачуваному стані, зайві записи у Flash | R3 | Medium |
| QR6 | Зависання без recovery або boot loop | Пристрій недоступний до ручного втручання | R5 | Medium |
| QR7 | `status` не відображає реальний стан або причину reset | QA не може діагностувати збій | R1, R7 | Low |
| QR8 | Некоректні аргументи CLI приймаються мовчки | Неочікувана тривалість сну, складна діагностика | R4 | Low |

## 4\. Test Matrix

У матриці 22 тести покривають R1–R7. Фактичний результат у Wokwi: 11 Fail, 1 Partial, 9 Pass, 1 Blocked (T11).

| ID | Req | Сценарій | Передумова | Дія | Expected | Evidence | Фактичний результат | Result |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| T01 | R1 | Cold boot | Симулятор зупинено | Start Simulator | `[BOOT] reset_reason=POWER_ON`, явний перехід у ACTIVE | Serial log | Partial: ACTIVE не логується (BUG-07) | Partial |
| T02 | R7 | Повнота `status` | ACTIVE | `status` | JSON: state, reset\_reason, relay, counter, heap, sensor\_ok | JSON | Pass, але state зашитий у код (BUG-07) | Pass |
| T03 | R2 | Baseline датчика | DHT підключений, 24.5 °C / 45 % | `sensor` | `temp=24.5C humidity=45.0%` | Serial log | Pass | Pass |
| T04 | R2 | Датчик недоступний | У `diagram.json` дріт `esp:D15 → dht:SDA` перенесено на `esp:D13` | `sensor`, `status` | Явна помилка, без числових значень; `sensor_ok:false` | Serial log | Fail: виводить 0.0C / 0.0% (BUG-04) | Fail |
| T05 | R2 | Invalid data не керує актуатором | Датчик від'єднано, relay OFF | `status` | relay залишається OFF | `status` | Pass (факт: relay:false при sensor\_ok:false) | Pass |
| T06 | R3 | Один натиск | counter \= N | 1 натиск | counter \= N+1, один рядок `[BUTTON]` | Log \+ `status` | Pass (факт: 2 натиски → 2 події) | Pass |
| T07 | R3 | 20 натисків | counter \= N, relay OFF | 20 натисків | counter \= N+20, relay OFF (парна кількість) | Log \+ status | Pass (факт: 10 натисків → 10 подій) | Pass |
| T08 | R4 | Тривалість `sleep 5` | ACTIVE | `sleep 5` | Wake через 4.25–5.75 с | Timestamped log | Fail (факт: 0.54 с; BUG-01) | Fail |
| T09 | R4 | Верхня межа `sleep 60` | ACTIVE | `sleep 60` | Wake через 51–69 с | Timestamped log | Fail (факт: 6.06 с; WDT reset через 0.65 с; BUG-01, BUG-10) | Fail |
| T10 | R4 | Дані після wake | relay ON, counter \= N | `sleep 5`, потім `status` | reset\_reason DEEP\_SLEEP, counter \= N+1, relay без змін | `status` до/після | Pass | Pass |
| T11 | R4 | Wake кнопкою | ACTIVE | `sleep 30`, натиснути кнопку | Пробудження, `[WAKE] cause=2` (ext0), CLI працює | Serial log | Blocked (факт: 2 спроби, обидві cause=4, натискання не зафіксоване; BUG-10) | Blocked |
| T12 | R4 | Некоректні аргументи | ACTIVE | `sleep abc` (інші входи — за аналізом коду) | Помилка CLI, пристрій не засинає | Serial log | Fail (факт: sleep abc → заснув без помилки; BUG-08) | Fail |
| T13 | R5 | Час спрацювання WDT | ACTIVE | `hang` | Reset ≤ 5 с, `reset_reason=TASK_WDT` | Timestamped log | Fail (факт: виявлення 4.2 с, reset через 9.4 с, INT\_WDT; BUG-11) | Fail |
| T14 | R5 | Актуатор після WDT | relay ON | `hang`, потім `status` | relay OFF, LED не світиться | `status` до/після | Fail (факт: relay true після 4 з 4 WDT reset; BUG-02) | Fail |
| T15 | R5 | Працездатність після WDT | Після T13 | `status`, `hang` після кожного reset | Усі команди виконуються | Serial log | Pass (факт: команди виконуються після 4 з 4 reset) | Pass |
| T16 | R5 | Відсутність boot loop | ACTIVE | `hang` → recovery ×10 | Один boot на кожен hang, щоразу ACTIVE | Serial log | Pass (4 цикли: один \[BOOT\] на кожен hang) | Pass |
| T17 | R6 | Цілісність після `powerloss` | relay ON, counter \= N, `save` | `status`, `powerloss`, `status` | Або старий (N), або новий повністю валідний state | `status` до/після | Fail (факт: counter 2 → 102 без \[STORE\] saved; BUG-03) | Fail |
| T18 | R6 | Повторний `powerloss` ×5 | Відомий state | `powerloss` ×5 | State залишається однією з валідних версій | `status` після кожного | Fail (факт: \+600 за 6 powerloss; BUG-03) | Fail |
| T19 | R6 | Виявлення corrupted state | Після T17 | Переглянути boot log | Повідомлення перевірки цілісності / rollback | Serial log | Fail: перевірки немає (BUG-03) | Fail |
| T20 | R6 | Атомарність `saveState()` (code review) | — | Перегляд `saveState()` | Один атомарний запис або запис з версією/CRC | Фрагмент коду | Fail: два записи з `delay(25)` між ними (BUG-06) | Fail |
| T21 | R7 | `reboot` і `powerloss` розрізняються | ACTIVE | `reboot` → `status`; `powerloss` → `status` | Різні reset reason або позначка в лозі | `status` | Fail (факт: обидва SOFTWARE\_RESET / rst:0xc; BUG-09) | Fail |
| T22 | CLI | Невідома команда | ACTIVE | Невідома команда (опечатки, напр. `statur`) | `[CLI] ERROR unknown command` | Serial log | Pass (факт: `[CLI] ERROR unknown command`) | Pass |

## 5\. Sleep / Wake tests (R4)

У цьому блоці найважливіший тест T08: сон довжиною 5 с має тривати 4.25–5.75 с.

**Як виміряно.** Час сну — від рядка `[STATE] SLEEP timer=N s` до рядка ROM `rst:0x5 (DEEPSLEEP_RESET)`, за часовими мітками Serial Monitor. `sleep 10` виміряно 6 разів, решту — по одному разу.

| Вхід | Очікуваний сон, с | Допуск ±15 %, с | Фактично, с |
| :---- | :---- | :---- | :---- |
| `sleep 1` | 1 | 0.85–1.15 | 0.14 ❌ (sleep abc → timer=1 s) |
| `sleep 5` | 5 | 4.25–5.75 | 0.54 ❌ |
| `sleep 10` | 10 | 8.5–11.5 | 1.03–1.04 ❌ (6 вимірів) |
| `sleep 60` | 60 | 51–69 | 6.06 ❌ (+ WDT reset через 0.65 с) |

**Послідовність T10 (дані після wake):**

1. `relay on` → `status`: записати counter \= N і relay \= true.  
2. `sleep 5`: чекати на `[BOOT] reset_reason=DEEP_SLEEP` та `[WAKE] cause=4` (timer).  
3. `status`: очікується counter \= N+1 (команда sleep сама збільшує counter), relay \= true, heap не менший за початковий.  
4. `relay off`, `sensor`: команди працюють.

**T11 wake кнопкою:** `sleep 60`, одразу після `[STATE] SLEEP` — натискання кнопки. Очікується `[WAKE] cause=2` (ext0). Фактично в обох спробах `[WAKE] cause=4`: сон переривається watchdog reset через 0.65 с, тому тест Blocked (BUG-10).

## 6\. Watchdog fault injection (R5)

Команда `hang` запускає нескінченний цикл без `esp_task_wdt_reset()`, і Task WDT (4000 ms) має зробити reset.

1. **T13:** `hang`; час від `[FAULT] firmware hang` до наступного `rst:`. Очікується ≤ 5 с і `reset_reason=TASK_WDT`. Фактично: panic-лог `task_wdt: Task watchdog got triggered` через ≈4.2 с, але reset лише через ≈9.4 с, `reset_reason=INT_WDT` (BUG-11).  
2. **T14:** `relay on` (LED світиться), `hang`, потім `status`. Очікується `"relay":false` і вимкнений LED. Фактично: `"relay":true` після 4 з 4 WDT reset (BUG-02).  
3. **Примітка:** після штатного `reboot` чи пробудження зі сну відновлення реле допустиме, після аварійного WDT reset — ні.

## 7\. Recovery tests (R5)

Recovery вважається успішним, коли після кожного аварійного reset пристрій повертається в ACTIVE рівно один раз і виконує команди.

1. **T15:** після кожного WDT reset — `status`, потім наступний `hang`. Фактично: команди виконуються після 4 з 4 reset.  
2. **T16:** `hang` → recovery, 4 цикли (заплановано 10). Критерій: рівно один рядок `[BOOT]` на кожен `hang`. Фактично: один `[BOOT]` у кожному циклі, boot loop відсутній.  
3. **Heap:** `heap` у `status` — 336332 після кожного recovery, витоку пам'яті немає.  
4. **Після `powerloss`:** пристрій завантажується і виконує команди (цілісність даних — у розділі 8).

## 8\. Data integrity при `powerloss` (R6)

Коректним є лише один із двох результатів: повністю старий state або повністю новий. Будь-яка суміш або мовчазна зміна даних означає Fail.

**T17, покроково:**

1. `relay on`, `save` → `status`. Записати базовий state: counter \= N, relay \= true.  
2. `powerloss`. У лозі має з'явитися `[FAULT] power loss DURING save` і потім `[BOOT] reset_reason=SOFTWARE_RESET`.  
3. `status`. Записати counter і relay.  
4. Порівняти з таблицею нижче.

| Результат | counter | relay | Висновок |
| :---- | :---- | :---- | :---- |
| Стара версія (rollback) | N | true | Pass |
| Нова повна версія, з підтвердженим commit | N+100 | true | Pass |
| Частковий commit без виявлення (фактичний результат) | N+100 | true, залишок старої версії | Fail |

Це Fail, хоча relay не змінився. `powerloss` записує лише одне поле транзакції (`counter`) і не доходить до `[STORE] saved`. Після reboot цей state приймається як валідний без жодної перевірки (немає версії, CRC чи commit-прапорця).

**T18:** повторити `powerloss` 6 разів поспіль. Фактично counter зріс на 600 (2 → 602), і жоден із цих записів не підтверджений.

## 9\. Evidence

Кожен Fail підтверджено щонайменше одним артефактом: фрагментом Serial-логу з часовими мітками, `status` до і після. Усі логи наведено в bug reports (розділ 10).

Повні Serial-логи всіх прогонів (R1–R6, T09, T11) наведено в додатку: Додаток: Serial logs

| Тест | Що зберегти | Де в звіті |
| :---- | :---- | :---- |
| T04 | Лог `sensor` \+ `status` з від'єднаним DHT; скріншот схеми без дроту | BUG-04: логи «до» і «після» |
| T06–T07 | Лог рядків `[BUTTON]` \+ counter до/після | BUG-05: Evidence R3 |
| T08–T09 | Timestamped лог від `[STATE] SLEEP` до `[BOOT]`, 3 повтори | Розділ 5 (таблиця сну); BUG-01, BUG-10 |
| T13 | Лог `[FAULT] firmware hang` → panic → `[BOOT] reset_reason=TASK_WDT` | BUG-11: таблиця 4 циклів і лог |
| T14 | `status` до і після | BUG-02: Evidence BUG-02 |
| T16 | Лог 4 циклів hang/recovery | BUG-11: таблиця 4 циклів |
| T17–T19 | `status` до/після `powerloss`, boot log | BUG-03: таблиця 6 циклів і лог |
| T12, T21 | Лог реакції на некоректні входи та `status` після `reboot` / `powerloss` | BUG-08, BUG-09 |

**Приклад evidence (T13/T14, фактичний лог):**

```
relay on
15:13:06.256 > [STORE] saved
15:13:06.256 > [RELAY] ON
hang
15:14:19.261 > [FAULT] firmware hang
15:14:23.439 > E (133088) task_wdt: Task watchdog got triggered. The following tasks did not reset the watchdog in time:
15:14:23.744 > abort() was called at PC 0x400dbf11 on core 0
15:14:28.714 > rst:0x8 (TG1WDT_SYS_RESET),boot:0x13 (SPI_FAST_FLASH_BOOT)
15:14:29.572 > [BOOT] reset_reason=INT_WDT
status
15:14:38.791 > {"state":"ACTIVE","reset_reason":"INT_WDT","relay":true,"counter":1,"heap":336332,"sensor_ok":true}
```

Витяги з коду наведено лише в Notes / Hypothesis. Основним доказом є спостережувана поведінка пристрою.

## 10\. Bug Reports

Знайдено 10 дефектів (3 Critical, 4 Major, 3 Minor) та одне спостереження: BUG-05 у Wokwi не відтворився.

**Спільне середовище для всіх багів:** Wokwi Simulator for VS Code \+ PlatformIO · ESP32 DevKit V1 · firmware `homework_buggy` (`src/main.cpp`) · Serial 115200 · дата: 26–27.10.2026.

| ID | Title | Severity | Req | Тест |
| :---- | :---- | :---- | :---- | :---- |
| BUG-01 | `sleep N` приблизно у 10 разів коротший за N секунд | Critical | R4 | T08, T09 |
| BUG-02 | Після WDT reset реле відновлюється у ON | Critical | R5 | T14 |
| BUG-03 | `powerloss` залишає частково оновлений state, який не виявляється | Critical | R6 | T17–T19 |
| BUG-04 | Недоступний DHT22 показується як 0.0C / 0.0% без помилки | Major | R2 | T04 |
| BUG-05 | Відсутній debounce кнопки (не відтворено в Wokwi) | Observation | R3 | T06, T07 |
| BUG-06 | `saveState()` неатомарний: два окремі записи з паузою 25 ms | Major | R6 | T20 |
| BUG-07 | Стан ACTIVE не логується при boot і зашитий у `status` | Minor | R1, R7 | T01, T02 |
| BUG-08 | Некоректні аргументи `sleep` приймаються мовчки | Minor | R4 | T12 |
| BUG-09 | Reset після `powerloss` не відрізнити від штатного `reboot` | Minor | R7 | T21 |
| BUG-10 | Під час sleep 10 щоразу спрацьовує прихований watchdog reset | Major | R4, R7 | T08–T09 |
| BUG-11 | Після hang reset через ≈9.4 с замість ≤5 с | Major | R5 | T13 |

### BUG-01 — `sleep N` приблизно у 10 разів коротший за N секунд

- **Preconditions:** пристрій у ACTIVE, Serial Monitor з `monitor_filters = time`.  
- **Steps:** 1\) `sleep 5`; 2\) зафіксувати час `[STATE] SLEEP timer=5 s` і наступного `[BOOT]`; 3\) повторити для `sleep 60`.  
- **Expected:** wake-up через 4.25–5.75 с (для 60 с: 51–69 с).  
- **Actual:** wake-up через приблизно 0.5 с (для 60 с: приблизно 6 с). Підтверджено: sleep 5 → 0.54 с, sleep 10 → 1.03–1.04 с (6 вимірів), sleep 60 → 6.06 с (приблизно 1/10 заданого часу).  
- **Reproducibility:** Always · **Severity:** Critical: вимогу R4 порушено у 10 разів, через це батарея розряджається достроково.  
- **Evidence:** timestamped log нижче. Сон виміряно від \[STATE\] SLEEP до rst:0x5 (DEEPSLEEP\_RESET).  
- **Notes / Hypothesis:** ймовірно, неправильне перетворення секунд у мікросекунди: у `buggySleep()` стоїть множник `100000ULL` замість `1000000ULL`.

**Evidence BUG-01 / R4:**

```
status
14:59:45.030 > {"state":"ACTIVE","reset_reason":"POWER_ON","relay":true,"counter":1,"heap":336332,"sensor_ok":true}
sleep 5
15:00:07.574 > [STATE] SLEEP timer=5 s
15:00:08.115 > rst:0x5 (DEEPSLEEP_RESET),boot:0x13 (SPI_FAST_FLASH_BOOT)   ← через 0.54 с (очікувалось 4.25–5.75 с)
15:00:08.949 > [BOOT] reset_reason=DEEP_SLEEP
15:00:08.949 > [WAKE] cause=4
status
15:00:43.616 > {"state":"ACTIVE","reset_reason":"DEEP_SLEEP","relay":true,"counter":2,"heap":336332,"sensor_ok":true}
sleep 10
15:01:47.605 > [STATE] SLEEP timer=10 s
15:01:48.644 > rst:0x5 (DEEPSLEEP_RESET),boot:0x13 (SPI_FAST_FLASH_BOOT)   ← через 1.04 с (очікувалось 8.5–11.5 с)
```

**T10 (дані після wake): Pass.** reset\_reason \= DEEP\_SLEEP, `[WAKE] cause=4` (timer), counter 1 → 2 → 3 → 4 (+1 за кожен sleep), relay залишається `true`, heap стабільний (336332).

### BUG-02 — Після WDT reset реле відновлюється у ON

- **Preconditions:** ACTIVE, `relay on` виконано (LED світиться, `[STORE] saved`).  
- **Steps:** 1\) `hang`; 2\) дочекатися `[BOOT] reset_reason=INT_WDT`; 3\) `status`.  
- **Expected:** після аварійного reset `"relay":false`, LED не світиться.  
- **Actual:** `"relay":true`, LED світиться одразу після boot. Підтверджено 4 з 4: після кожного WDT reset status показує "reset\_reason":"INT\_WDT","relay":true.  
- **Reproducibility:** Always · **Severity:** Critical: небезпечний стан актуатора після збою.  
- **Evidence:** `status` до/після, лог нижче.  
- **Notes / Hypothesis:** ймовірно, `setup()` викликає `applyRelay(relayState)` зі значенням з NVS і не перевіряє reset reason. boot loop немає (один \[BOOT\] на кожен hang), counter зберігається. Час до reset — окремий дефект BUG-11.

**Evidence BUG-02:**

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

### BUG-03 — `powerloss` залишає частково оновлений state, який не виявляється

- **Preconditions:** `relay on`, `save`; `status` показує counter \= N.  
- **Steps:** 1\) `powerloss`; 2\) дочекатися boot; 3\) `status`; 4\) повторити кроки 1–3 п'ять разів (усього 6 циклів).  
- **Expected:** state дорівнює або старій валідній версії (N), або новій повністю записаній. Під час boot перерваний запис виявляється і логується.  
- **Actual:** counter \= N+100 без `[STORE] saved`, і так кожен раз (+100 за кожен цикл). У boot log немає жодної перевірки цілісності. Підтверджено 6 з 6: counter 2 → 602, relay залишається true, жодного попередження при boot.  
- **Reproducibility:** Always · **Severity:** Critical: пошкоджені persistent data приймаються як валідні.  
- **Evidence:** `status` до/після кожного циклу — таблиця та лог нижче.  
- **Notes / Hypothesis:** ймовірно, `simulateInterruptedSave()` фіксує лише `counter`, а `setup()` читає NVS без версії, CRC чи commit-прапорця. Це fault injection у Wokwi, а не справжній brown-out.

**Evidence BUG-03 / R6** (базовий state після `relay on` \+ `save`: counter \= 2, relay \= true):

| Цикл | `[FAULT] power loss DURING save` | counter після boot | relay | `[STORE] saved` |
| :---- | :---- | :---- | :---- | :---- |
| 1 | 15:22:06.763 | 102 | true | немає |
| 2 | 15:22:34.243 | 202 | true | немає |
| 3 | 15:22:45.832 | 302 | true | немає |
| 4 | 15:23:00.099 | 402 | true | немає |
| 5 | 15:23:11.848 | 502 | true | немає |
| 6 | 15:23:24.099 | 602 | true | немає |

&nbsp;

```
save
15:21:47.603 > [STORE] saved
status
15:21:51.926 > {"state":"ACTIVE","reset_reason":"POWER_ON","relay":true,"counter":2,"heap":336332,"sensor_ok":true}
powerloss
15:22:06.763 > [FAULT] power loss DURING save
15:22:06.774 > rst:0xc (SW_CPU_RESET),boot:0x13 (SPI_FAST_FLASH_BOOT)
15:22:07.645 > [BOOT] reset_reason=SOFTWARE_RESET          ← жодної перевірки цілісності
status
15:22:17.730 > {"state":"ACTIVE","reset_reason":"SOFTWARE_RESET","relay":true,"counter":102,"heap":336332,"sensor_ok":true}
```

**Висновок R6:** T17 Fail · T18 Fail (+600 за 6 циклів) · T19 Fail (у boot log немає перевірки цілісності). Дані, які не були збережені до кінця, приймаються як валідні та накопичуються.

### BUG-04 — Недоступний DHT22 показується як 0.0C / 0.0% без помилки

- **Preconditions:** у `diagram.json` з'єднання `esp:D15 → dht:SDA` перенесено на esp:D13, симулятор перезапущено.  
- **Steps:** 1\) `sensor`; 2\) `status`.  
- **Expected:** явна помилка (наприклад, `[SENSOR] ERROR read failed`), без числових значень; `sensor_ok:false`.  
- **Actual:** `[SENSOR] temp=0.0C humidity=0.0%`, а в `status` при цьому `"sensor_ok":false`. Два джерела суперечать одне одному. Підтверджено 2026-10-26.  
- **Reproducibility:** Always · **Severity:** Major: невалідні дані виглядають як реальна температура 0 °C.  
- **Evidence:** Serial log «до» та «після» нижче.  
- **Notes / Hypothesis:** ймовірно, `printSensor()` замінює NaN на 0\. На реле дані датчика зараз не впливають (T05 Pass).

**Evidence BUG-04 — до (DHT22 на GPIO15, датчик працює):**

```
17:17:58.343 > [BOOT] reset_reason=POWER_ON
sensor
17:18:02.461 > [SENSOR] temp=24.5C humidity=45.0%
status
17:18:06.506 > {"state":"ACTIVE","reset_reason":"POWER_ON","relay":false,"counter":0,"heap":336068,"sensor_ok":true}
```

**Evidence BUG-04 — після (дріт DHT22 перенесено на GPIO13, датчик недоступний):**

```
17:09:32.422 > [BOOT] reset_reason=POWER_ON
sensor
17:09:48.266 > [SENSOR] temp=0.0C humidity=0.0%
status
17:09:52.368 > {"state":"ACTIVE","reset_reason":"POWER_ON","relay":false,"counter":0,"heap":336300,"sensor_ok":false}
```

**Висновок R2:** T03 Pass · T04 Fail (BUG-04) · T05 Pass (`relay:false`). Вимога R2 не виконана.

### BUG-05 — Відсутній debounce кнопки (не відтворено в Wokwi)

- **Status:** Not reproduced → переведено в Observation / латентний ризик.  
- **Preconditions:** ACTIVE, relay OFF, counter \= 0; у `diagram.json` кнопка має `"bounce": "1"`.  
- **Steps:** 1\) `status`; 2\) 2 натиски кнопки; 3\) `status`; 4\) 10 натисків з інтервалом приблизно 1 с; 5\) `status`.  
- **Expected:** один рядок `[BUTTON]` на кожен натиск; counter 0 → 2 → 12\.  
- **Actual:** 2 → 2 події, 10 → 10 подій; counter 0 → 2 → 12; реле в кінці `false`. Дублів немає — **T06, T07 Pass**.  
- **Reproducibility:** Not reproduced (0 з 12 натисків) · **Severity:** Observation.  
- **Notes / Hypothesis:** у коді немає фільтра брязкоту. Ймовірно, брязкіт випадково маскує `saveState()` (запис NVS \+ `delay(25)` після кожної події): поки це триває, контакт встигає заспокоїтися. Якщо збереження прискорять чи приберуть, дублі можуть з'явитися. Потрібна перевірка на реальній кнопці. Додатково: кожне натискання записує Flash (`[STORE] saved`), що на реальному пристрої прискорює знос пам'яті.

**Evidence R3 (скорочено):**

```
status
17:43:30.165 > {"state":"ACTIVE",...,"relay":false,"counter":0,...}
17:43:35.704 > [STORE] saved
17:43:35.704 > [BUTTON] relay=ON
17:43:40.324 > [STORE] saved
17:43:40.334 > [BUTTON] relay=OFF
status
17:44:21.230 > {"state":"ACTIVE",...,"relay":false,"counter":2,...}
17:44:33.902 > [BUTTON] relay=ON
17:44:34.850 > [BUTTON] relay=OFF
   ... (усього 10 рядків [BUTTON], кожен з [STORE] saved, інтервал ~1 с)
17:44:42.936 > [BUTTON] relay=OFF
status
17:44:59.295 > {"state":"ACTIVE",...,"relay":false,"counter":12,...}
```

### BUG-06 — `saveState()` неатомарний: два окремі записи з паузою 25 ms

- **Preconditions:** — (знайдено через code review, T20).  
- **Steps:** переглянути `saveState()` у `src/main.cpp`.  
- **Expected:** state записується атомарно (один blob із версією та CRC або схема A/B).  
- **Actual:** `putUInt("counter")` → `delay(25)` → `putBool("relay")`. Обрив живлення в цій паузі залишить змішаний state.  
- **Reproducibility:** — (статичний дефект) · **Severity:** Major.  
- **Evidence:** фрагмент коду.  
- **Notes / Hypothesis:** у Wokwi це вікно неможливо цілеспрямовано вцілити CLI-командою, тому потрібна перевірка на стенді з керованим живленням.

### BUG-07 — Стан ACTIVE не логується при boot і зашитий у `status`

- **Preconditions:** симулятор зупинено, Serial Monitor з часовими мітками.  
- **Steps:** 1\) cold boot; 2\) `status`.  
- **Expected:** boot log містить явний перехід (наприклад, `[STATE] ACTIVE`), а `state` у `status` відображає реальний стан.  
- **Actual:** виводиться лише `[BOOT] reset_reason=...`, а `"state":"ACTIVE"` записаний константою.  
- **Reproducibility:** Always · **Severity:** Minor: погіршує observability, але не впливає на функціонал.  
- **Evidence:** cold boot 15:32:30.400 `[BOOT] reset_reason=POWER_ON` → `[WDT] enabled` → `Commands:` — рядка про перехід у ACTIVE немає; `status` показує `"state":"ACTIVE"` навіть одразу після WDT reset та deep sleep.

### BUG-08 — Некоректні аргументи `sleep` приймаються мовчки

- **Preconditions:** ACTIVE, Serial Monitor з часовими мітками.  
- **Steps:** по черзі ввести `sleep abc`, `sleep 0`, `sleep -5`, `sleep 100`, `sleepy`.  
- **Expected:** `[CLI] ERROR ...`, пристрій не засинає (або з попередженням про обмеження діапазону).  
- **Actual:** `abc` і `0` дають сон на 1 с; `-5` і `100` дають сон на 60 с (`-5` перетворюється на велике число без знака); `sleepy` дає сон на 5 с. Усе без попереджень (через BUG-01 фактичний сон у 10 разів коротший). Запуском перевірено sleep abc (інші входи описано за аналізом коду): 15:02:07.978 \[STATE\] SLEEP timer=1 s → 15:02:08.116 rst:0x5 (DEEPSLEEP\_RESET) — жодної помилки, пристрій заснув на 0.14 с, counter збільшився (3 → 4).  
- **Reproducibility:** Always · **Severity:** Minor.  
- **Evidence:** `sleep abc` → `15:02:07.978 [STATE] SLEEP timer=1 s` → `15:02:08.116 rst:0x5 (DEEPSLEEP_RESET)` → `status`: counter 3 → 4\.

### BUG-09 — Reset після `powerloss` не відрізнити від штатного `reboot`

- **Preconditions:** ACTIVE, відомий state (counter \= 502, relay \= true).  
- **Steps:** 1\) `reboot` → `status`; 2\) `powerloss` → `status`.  
- **Expected:** QA може відрізнити аварійний reset від штатного (окремий прапорець чи лічильник збоїв).  
- **Actual:** в обох випадках `reset_reason=SOFTWARE_RESET`. Також `resetName()` (за аналізом коду) повертає `OTHER` для PANIC та EXT reset.  
- **Reproducibility:** Always · **Severity:** Minor.

**Evidence BUG-09 (підтверджено):** після `powerloss` і після штатного `reboot` і ROM (`rst:0xc (SW_CPU_RESET)`), і firmware (`reset_reason=SOFTWARE_RESET`) показують одне й те саме.

```
powerloss
15:23:24.099 > [FAULT] power loss DURING save
15:23:24.109 > rst:0xc (SW_CPU_RESET),boot:0x13 (SPI_FAST_FLASH_BOOT)
15:23:24.976 > [BOOT] reset_reason=SOFTWARE_RESET
reboot
15:23:36.703 > rst:0xc (SW_CPU_RESET),boot:0x13 (SPI_FAST_FLASH_BOOT)
15:23:37.528 > [BOOT] reset_reason=SOFTWARE_RESET
status
15:23:50.661 > {"state":"ACTIVE","reset_reason":"SOFTWARE_RESET","relay":true,"counter":602,...}
```

### BUG-10 — Під час `sleep 10` щоразу спрацьовує watchdog reset, який firmware не показує

- **Preconditions:** ACTIVE, Serial Monitor з часовими мітками.  
- **Steps:** 1\) `sleep 10`; 2\) дочекатися пробудження; 3\) `status`; 4\) повторити кроки 1–3 п'ять разів.  
- **Expected:** один цикл завантаження з `rst:0x5 (DEEPSLEEP_RESET)`; будь-який нештатний reset видно в `reset_reason`.  
- **Actual:** приблизно через 0.65 с після `[STATE] SLEEP` ROM виводить `rst:0x8 (TG1WDT_SYS_RESET)`, і лише через приблизно 1.04 с — `rst:0x5 (DEEPSLEEP_RESET)`. Firmware показує лише `reset_reason=DEEP_SLEEP`, тобто watchdog reset прихований від QA. Дані після wake цілі (counter \+1, relay без змін, heap 336332).  
- **Reproducibility:** Always — 1 з 1 для sleep 60 і 6 з 6 для `sleep 10`; 0 з 2 для коротших снів (`sleep 5` ≈ 0.54 с, `sleep abc` ≈ 0.14 с).  
- **Severity:** Major — нештатний watchdog reset під час кожного сну та хибний reset reason (R4, R7).  
- **Notes / Hypothesis:** причина невідома. Схоже, watchdog спрацьовує, коли сон довший за приблизно 0.65 с; це може бути артефакт симуляції deep sleep у Wokwi або невимкнений таймер перед сном. Потрібна перевірка на реальному ESP32 та після виправлення BUG-01 (коли сон стане 5–60 с).

| Цикл | `[STATE] SLEEP` | `rst:0x8 TG1WDT` | `rst:0x5 DEEPSLEEP` | Сон, с |
| :---- | :---- | :---- | :---- | :---- |
| 1 | 15:01:47.605 | 15:01:48.264 | 15:01:48.644 | 1.04 |
| 2 | 15:05:21.275 | 15:05:21.929 | 15:05:22.310 | 1.04 |
| 3 | 15:05:35.826 | 15:05:36.479 | 15:05:36.860 | 1.03 |
| 4 | 15:05:49.456 | 15:05:50.113 | 15:05:50.493 | 1.04 |
| 5 | 15:06:02.206 | 15:06:02.863 | 15:06:03.245 | 1.04 |
| 6 | 15:06:11.989 | 15:06:12.646 | 15:06:13.029 | 1.04 |

&nbsp;

```
15:05:21.275 > [STATE] SLEEP timer=10 s
15:05:21.929 > rst:0x8 (TG1WDT_SYS_RESET),boot:0x13 (SPI_FAST_FLASH_BOOT)
15:05:22.310 > rst:0x5 (DEEPSLEEP_RESET),boot:0x13 (SPI_FAST_FLASH_BOOT)
15:05:23.200 > [BOOT] reset_reason=DEEP_SLEEP
15:05:23.200 > [WAKE] cause=4
status
15:05:29.029 > {"state":"ACTIVE","reset_reason":"DEEP_SLEEP","relay":false,"counter":1,"heap":336332,"sensor_ok":true}
```

**Додатково (T09, `sleep 60`):** watchdog будить пристрій через 0.65 с, і фірмвара повністю завантажується в ACTIVE (`reset_reason=INT_WDT`). Через ≈4.5 с роботи стається ще одне неочікуване перезавантаження `DEEPSLEEP_RESET`. Тобто сон переривається, а працюючий пристрій перезавантажується без команди. Через це T11 (пробудження кнопкою) практично не виконуваний: справжній сон триває лише 0.65 с.

```
15:32:48.764 > [STATE] SLEEP timer=60 s
15:32:49.419 > rst:0x8 (TG1WDT_SYS_RESET),boot:0x13 (SPI_FAST_FLASH_BOOT)   ← +0.65 с
15:32:50.273 > [BOOT] reset_reason=INT_WDT
15:32:50.281 >   reboot                                                    ← пристрій у ACTIVE
15:32:54.820 > rst:0x5 (DEEPSLEEP_RESET),boot:0x13 (SPI_FAST_FLASH_BOOT)   ← +6.06 с, reset посеред роботи
15:32:55.704 > [BOOT] reset_reason=DEEP_SLEEP
15:32:55.705 > [WAKE] cause=4
status
15:32:59.855 > {"state":"ACTIVE","reset_reason":"DEEP_SLEEP","relay":false,"counter":1,"heap":336332,"sensor_ok":true}
```

**T11 — Blocked.** Дві спроби (`sleep 60`, потім одразу натискання кнопки) дали однаковий результат: `rst:0x8` через 0.65 с, далі `rst:0x5` і `[WAKE] cause=4` (таймер). `[WAKE] cause=2` не з'явився, рядка `[BUTTON]` теж немає, тобто натискання не зафіксоване взагалі. Перевірити wake кнопкою неможливо, доки не виправлені BUG-01 та BUG-10. Повторити після фіксу.

### BUG-11 — Після `hang` пристрій перезавантажується через ≈9.4 с замість ≤5 с

- **Preconditions:** ACTIVE, relay ON.  
- **Steps:** 1\) `hang`; 2\) зафіксувати час `[FAULT] firmware hang`, рядка `task_wdt: Task watchdog got triggered` і наступного `rst:`; 3\) `status`; 4\) повторити 4 рази.  
- **Expected:** WDT перезавантажує пристрій приблизно не пізніше ніж за 5 с (R5); reset reason \= TASK\_WDT.  
- **Actual:** Task WDT виявляє зависання за ≈4.2 с і викликає `abort()`, але після `Backtrace: ... |<-CORRUPTED` і `ELF file SHA256` пристрій ще ≈5 с нічого не робить. Reset відбувається лише через ≈9.4 с від `hang` і через інший механізм: `rst:0x8 (TG1WDT_SYS_RESET)`, `reset_reason=INT_WDT`.  
- **Reproducibility:** Always (4 з 4\) · **Severity:** Major — час недоступності перевищує вимогу майже вдвічі.  
- **Notes / Hypothesis:** ймовірно, після panic обробник помилки не завершується (немає рядка `Rebooting...`), і чип перезавантажує резервний Interrupt WDT. Той самий `rst:0x8 (TG1WDT_SYS_RESET)` є в BUG-10, тому дефекти можуть бути пов'язані. Може бути артефакт Wokwi; потрібна перевірка на реальному ESP32.

| Цикл | `hang` | `task_wdt triggered` | `rst:0x8` | До виявлення, с | До reset, с |
| :---- | :---- | :---- | :---- | :---- | :---- |
| 1 | 15:14:19.261 | 15:14:23.439 | 15:14:28.714 | 4.18 | 9.45 |
| 2 | 15:14:50.688 | 15:14:54.848 | 15:15:00.105 | 4.16 | 9.42 |
| 3 | 15:15:13.145 | 15:15:17.308 | 15:15:22.537 | 4.16 | 9.39 |
| 4 | 15:15:37.690 | 15:15:41.851 | 15:15:47.118 | 4.16 | 9.43 |

&nbsp;

```
15:14:19.261 > [FAULT] firmware hang
15:14:23.439 > E (133088) task_wdt: Task watchdog got triggered. The following tasks did not reset the watchdog in time:
15:14:23.440 > E (133088) task_wdt:  - loopTask (CPU 1)
15:14:23.744 > E (133088) task_wdt: Aborting.
15:14:23.744 > abort() was called at PC 0x400dbf11 on core 0
15:14:23.744 > Backtrace: 0x400835b5:0x3ffbea8c |<-CORRUPTED
15:14:23.745 > ELF file SHA256: 7bf4d35d2b731f75
                 ... ≈5 с без виводу ...
15:14:28.714 > rst:0x8 (TG1WDT_SYS_RESET),boot:0x13 (SPI_FAST_FLASH_BOOT)
15:14:29.572 > [BOOT] reset_reason=INT_WDT
```

## 11\. Entry / Exit Criteria

За чинними Exit criteria реліз заблокований: відкриті 3 Critical дефекти.

**Entry criteria**

- [x] Прошивка збирається (`PlatformIO: Build` без помилок).  
- [x] Симулятор стартує, Serial на 115200 відповідає на `help`.  
- [x] Схема відповідає README (DHT22→GPIO15, Button→GPIO4, LED→GPIO2, Relay→GPIO5).  
- [x] Вимоги R1–R7 та Test Matrix відрев'юйовані.  
- [x] Увімкнено часові мітки в лозі (`monitor_filters = time`).  
- [x] NVS очищено перед першим прогоном (новий запуск симулятора), counter \= 0\.

**Exit criteria**

- [x] Усі 22 тести мають Result відмінний від Not run.  
- [x] Кожен Fail має bug report з evidence.  
- [ ] 0 відкритих Blocker/Critical.  
- [ ] Major виправлені або мають задокументоване рішення про відкладення.  
- [ ] Після фіксів виконаний regression: T08–T19 та T16 (10 циклів).  
- [x] Результати R4–R6 заплановано підтвердити на фізичному стенді.

## 12\. Test Summary / Case Study

**Висновок: No-Go.** Прошивка стабільно відновлюється після зависання, але в критичних сценаріях поводиться небезпечно: реле ON після WDT, нецілісний state після powerloss, сон у 10 разів коротший.

| Вимога | Тести | Статус | Дефекти |
| :---- | :---- | :---- | :---- |
| R1 Boot | T01 | Partial | BUG-07 |
| R2 Sensor failure | T03–T05 | Fail | BUG-04 |
| R3 Button | T06–T07 | Pass | — (BUG-05 як Observation) |
| R4 Sleep / Wake | T08–T12 | Fail | BUG-01, BUG-08, BUG-10 |
| R5 Watchdog | T13–T16 | Fail | BUG-02, BUG-11 |
| R6 Interrupted save | T17–T20 | Fail | BUG-03, BUG-06 |
| R7 Observable evidence | T02, T21 | Partial | BUG-07, BUG-09 |

**Метрики (факт, Wokwi, 26–27.10.2026):** 22 тести, з них 9 Pass, 11 Fail, 1 Partial, 1 Blocked · 10 дефектів: 3 Critical / 4 Major / 3 Minor \+ 1 Observation · час WDT recovery ≈9.4 с (виявлення ≈4.2 с) · фактичний сон для `sleep 5` 0.54 с (замість 5 с).

**Що працює:** Task WDT виявляє зависання за ≈4.2 с (сам reset настає лише через ≈9.4 с, BUG-11), і reset reason (фактично INT\_WDT, а не очікуваний `TASK_WDT`) дозволяє визначити WDT reset. Boot loop відсутній, бо прапорець `hangRequested` живе в RAM. Кнопка дає рівно одну подію на натиск (12 з 12). Дані після deep sleep цілі, heap стабільний (336332) у всіх тестах, CLI стабільно відповідає і відхиляє невідомі команди, `status` містить усі поля R7.

**Ключовий урок (case study).** «Пристрій перезавантажився» ще не означає «пристрій відновився». Відновлення перевіряється за трьома ознаками: безпечний стан актуатора, цілісні дані та правдива діагностика. У цій прошивці WDT-механізм працює, але дві з трьох ознак не виконані.

**Рекомендації для розробника (за пріоритетом):**

1. Після reset із reason WDT, PANIC або BROWNOUT ставити реле в OFF (BUG-02).  
2. Записувати state одним blob із версією та CRC або за схемою A/B і перевіряти його при boot (BUG-03, BUG-06).  
3. Виправити перетворення часу сну та валідувати аргумент (BUG-01, BUG-08).  
4. Додати програмний debounce приблизно на 30–50 ms профілактично, бо зараз він працює лише випадково (BUG-05, Observation).  
5. Повертати помилку датчика замість 0 (BUG-04).

**Обмеження:** тестування проведене лише в Wokwi. `powerloss` це fault injection, а не brown-out, і точність таймінгів залежить від симулятора. R4–R6 треба переперевірити на реальному ESP32 з керованим живленням.