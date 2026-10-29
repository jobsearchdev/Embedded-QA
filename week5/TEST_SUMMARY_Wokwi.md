# Test Summary — Webinar 6: Python/Pytest Embedded Automation

Виконав: Evhenii Kofan   Дата: 29.10.2026

## 1. Об'єкт і середовище
- Прошивка: `homework_buggy` (ESP32 DevKit + DHT22 на GPIO15 + LED на GPIO2), UART 115200
- Вимоги: `requirements/device_requirements.md` (REQ 1–10)
- ПК / ОС: MacBook (Apple M3), macOS
- Python 3.14.8 (Homebrew), venv `.venv`; pytest 9.2.0; pyserial 3.5; pluggy 1.7.0
- Симулятор: Wokwi for VS Code, прошивка зібрана PlatformIO
- Підключення: `DEVICE_PORT=rfc2217://localhost:4000`
- Timeout клієнта (`conftest.py`): 1.0 s; для діагностики тимчасово 1.9 / 2.0 / 2.5 s

## 2. Результати

| Прогін | Timeout | Тестів | PASS | FAIL | ERROR (teardown) | Примітка | Evidence |
|---|---|---|---|---|---|---|---|
| 1 — Baseline | 1.0 s | 14 | 9 | 5 | 1 | валідний | `01_baseline.txt` |
| 2 | 1.0 s | 14 | 1 | 13 | 14 | пристрій не відповідав (environment) | — |
| 3 — діагностика | 1.9 s | 14 | 7 | 7 | 5 | перші 5 тестів без відповіді; `test_ping` PASS | — |
| 4 | 2.0 s | 14 | 1 | 13 | 14 | пристрій не відповідав (environment) | — |
| 5 | 2.5 s | 14 | 1 | 13 | 14 | пристрій не відповідав (environment) | — |
| 6 — власні тести | 1.0 s | 23 | 14 | 9 | 6 | 6 випадкових timeout (environment) + 3 REQ-Q2 | `03_my_negative.txt` |
| 7 — повний | 1.0 s | 37 | 29 | 8 | 1 | 1 хибне падіння через запізнілу відповідь | `02_full_run.txt` |
| 8 — повний, чистий | 1.0 s | 37 | 30 | 7 | 0 | до додавання timeout-тестів і `clean_device` | `report.xml` |
| 9 — timeout-тести | 1.0 s | 2 | 2 | 0 | 0 | `test_my_timeout.py` з `clean_device` | `04_my_timeout.txt` |
| **10 — фінальний** | 1.0 s | **39** | **32** | **7** | **0** | **основний результат**: усі тести, `clean_device` | `06_final_run.txt`, `report_final.xml` |

Діагностичний вимір: `PING` з timeout 3 s → `{"status":"OK","command":"PING"}` за **1.35 s**.

## 3. Аналіз FAIL / ERROR

Категорії: test / environment / communication / requirement / firmware

| # | Тест | Фактичний результат | Категорія | Обґрунтування |
|---|---|---|---|---|
| 1 | `test_status::test_ping` | `TimeoutError: No response for command: PING` (1.0 s) | **Firmware** | З timeout 3 s відповідь коректна, але за 1.35 s; при timeout 1.9 s (прогін 3) тест PASS. Зв'язок працює (інші команди в тих самих прогонах відповідають). Вимоги не задають максимального часу відповіді (REQ-Q1). |
| 2 | `test_sensor::test_temperature_is_valid_json` | `Invalid JSON from device: '{"status":"OK","temperature":24.5'` | **Firmware** | Порушено REQ 3: у JSON бракує закривної `}`. Відтворюється в прогонах 1, 3, 7, 8. Відповідь прийшла → не communication. |
| 3 | `test_boundaries::test_pwm_valid_boundaries[100]` | `assert 'ERROR' == 'OK'` | **Firmware** | Порушено REQ 5 (0..100 включно). У тих самих прогонах 99 → PASS, 100 → ERROR: помилка на межі (off-by-one). Відтворюється в прогонах 1, 7, 8. |
| 4 | `test_relay::test_reset_restores_safe_state` | `assert 255 == 0` (pwm після RESET) | **Firmware** | Порушено REQ 7: `SET LED ON` → `RESET` → `STATUS` залишає pwm = 255. Відтворюється в прогонах 1, 3, 7, 8. |
| 5 | `test_my_negative::test_status_shows_pwm[1/50/99]` | STATUS `pwm` = 2 / 127 / 252 замість 1 / 50 / 99 | **Requirement** (REQ-Q2) | Значення = N × 255 / 100: STATUS повертає 8-бітний duty (0..255), а `SET PWM` працює в 0..100. Для 0 → PASS. REQ 2 («current PWM state») не визначає одиниць → неоднозначність вимоги, а не підтверджений дефект. Стабільно відтворюється (прогони 6, 7, 8). |
| 6 | `test_boundaries::test_pwm_invalid_boundaries[101]` (лише прогін 7) | `assert 'OK' == 'ERROR'` | **Communication** | Хибне падіння. У попередньому тесті (`[-1]`) teardown `RESET` не дочекався відповіді (ERROR); запізніла відповідь `{"status":"OK",...}` прийшла вже після підключення наступного тесту й була зчитана як відповідь на `SET PWM 101`. Доказ: у прогонах 1 і 8 `[101]` → PASS, а в прогоні 7 `test_pwm_out_of_range[101]` → PASS. Слабке місце helper-а: відповіді не прив'язані до команди. |
| 7 | Прогін 7 — ERROR teardown `test_pwm_invalid_boundaries[-1]` | `TimeoutError: No response for command: RESET` | **Environment** | Одиночний timeout на команду без затримки у прошивці; не відтворюється в прогоні 8. |
| 8 | Прогін 6 — 6 тестів (`out_of_range[-100,-1]`, `keeps_state[abc]`, `unknown_command["",ping,HELLO]`) + 6 ERROR | `TimeoutError` на звичайні команди | **Environment** | Ті самі тести в прогоні 8 → PASS. Падають на командах, які прошивка обробляє миттєво. У `report.xml` частина тестів триває ~6.3 s замість ~1.3 s → симуляція періодично «підвисає» (ймовірно, повільне встановлення RFC2217-з'єднання). |
| 9 | `test_boundaries::test_pwm_valid_boundaries[0]` + ERROR teardown (прогін 1) | `TimeoutError: No response for command: SET PWM 0` | **Environment** | Перший тест сесії; у прогоні 8 → PASS. Пристрій ще не готовий одразу після підключення (helper чекає лише 0.2 s). |
| 10 | Прогони 2, 4, 5 — усі тести (FAIL + ERROR) | `TimeoutError` на всі команди, зокрема `STATUS` | **Environment** | Не відповідає жодна команда; збільшення timeout до 2.0 / 2.5 s не допомогло → симуляція Wokwi не працювала / була на паузі. Єдиний PASS — `test_timeout` (очікує відсутність відповіді). |
| 11 | Прогін 3 — `test_pwm_valid_boundaries[0..100]` | `TimeoutError` на `SET PWM` | **Environment** | Та сама картина, що й п.9: перші тести після старту без відповіді. |

Чому поруч F і E: тест падає без відповіді (F), а teardown фікстури теж не отримує відповіді на `RESET` (E). Причина одна.

Примітка: `DeprecationWarning: setDaemon()/setName()` — попередження pyserial 3.5 на Python 3.14, на результат не впливає.

## 4. Що додано
- Параметризовані тести `tests/test_my_negative.py` — 5 тестів, 23 кейси (з фікстурою `clean_device`). Результат у фінальному прогоні 10: **20 PASS / 3 FAIL** (усі 3 — REQ-Q2).

  | Тест | REQ | Значення | Очікувано | Результат |
  |---|---|---|---|---|
  | `test_pwm_out_of_range` | 6 | -100, -1, 101, 102, 255, 1000 | `ERROR` / `INVALID_VALUE` | 6/6 PASS |
  | `test_pwm_not_integer` | 5 | `abc`, `5.5`, `+5`, `50%`, `0x10` | `ERROR` / `INVALID_VALUE` | 5/5 PASS |
  | `test_invalid_pwm_keeps_state` | 6 | -1, 101, `abc` (після `SET PWM 40`) | `pwm` у STATUS не змінюється | 3/3 PASS |
  | `test_unknown_command` | 8 | `""`, `ping`, `HELLO`, `SET LED BLINK`, `GET HUMIDITY` | `ERROR` / `UNKNOWN_COMMAND` | 5/5 PASS |
  | `test_status_shows_pwm` | 2 | 0, 1, 50, 99 | STATUS `pwm` = встановленому | 1/4 PASS (REQ-Q2) |

- Діагностика PING з timeout 3 s: відповідь коректна, час **1.35 s**.
- Перевірка timeout `tests/test_my_timeout.py` — 2 тести, **2 PASS** (REQ 9), evidence `04_my_timeout.txt`:
  - `test_timeout_is_finite`: `NO_RESPONSE` → `TimeoutError` за **1.06 s** (< 1.5 s) — клієнт не чекає вічно.
  - `test_device_works_after_timeout`: після timeout `STATUS` → `OK` (тест 1.22 s) — пристрій і з'єднання працюють далі.
  - Спостереження: teardown (`RESET`) після цього тесту тривав 5.50 s — ще один прояв підвисань Wokwi (environment).
- Precondition / cleanup — фікстура `clean_device` у `conftest.py` (використовують `test_my_negative.py`, `test_my_timeout.py`; 25 тестів):
  - **Precondition:** `RESET` → `STATUS` → якщо `pwm != 0` або `led != false` — fallback `SET LED OFF` → повторний `STATUS` → `assert pwm == 0 and led is False`. Тест стартує лише з перевіреного безпечного стану.
  - **Cleanup:** після тесту `SET LED OFF`.
  - **Чому fallback:** RESET дефектний (BUG-04) — покладатися на нього не можна, інакше стан «протікає» між тестами (напр. після `test_pwm_valid_boundaries[99]` pwm лишається 252).
  - У прогоні `05_clean_device.txt` fallback спрацював 0 разів: пристрій уже був у безпечному стані, а cleanup кожного тесту (`SET LED OFF`) не давав стану «забруднитися».
  - **Перевірка fallback** (`05_clean_device_fallback.txt`): вручну `SET PWM 50` → `{"status":"OK","pwm":50}`, потім `test_pwm_out_of_range[101]` → **PASS**. Фікстура зафіксувала `WARNING: RESET не спрацював: {'led': True, 'pwm': 127, ...} -> fallback SET LED OFF` і повернула пристрій у безпечний стан до початку тесту. Це водночас додаткове підтвердження BUG-04.
  - Оригінальні тести викладача не змінювались і використовують базову фікстуру `device`.

## 5. Підтверджені дефекти прошивки

| ID | Severity | Опис | Кроки | Очікувано | Фактично | Evidence |
|---|---|---|---|---|---|---|
| BUG-01 | Major | PING відповідає повільніше за timeout клієнта | `PING` | відповідь < 1.0 s, `{"status":"OK","command":"PING"}` | `TimeoutError` при 1.0 s; з timeout 3 s відповідь за 1.35 s | `report.xml`, `02_full_run.txt`; `BUG-01_ping.txt` |
| BUG-02 | Major | Невалідний JSON у `GET TEMP` (REQ 3) | `GET TEMP` (DHT22 = 24.5 °C) | `{"status":"OK","temperature":24.5}` | `{"status":"OK","temperature":24.5` (без `}`) | `report.xml`, `01_baseline.txt`; `BUG-02_temp.txt` |
| BUG-03 | Major | `SET PWM 100` відхиляється (REQ 5) | `SET PWM 100` | `{"status":"OK","pwm":100}` | `{"status":"ERROR","code":"INVALID_VALUE"}` | `report.xml`, `01_baseline.txt`; `BUG-03_pwm100.txt` |
| BUG-04 | Critical | RESET не повертає безпечний стан (REQ 7) | `SET LED ON` → `RESET` → `STATUS` | `led:false, pwm:0` | `pwm:255` | `report.xml`, `01_baseline.txt`; `BUG-04_reset.txt` |

Питання до вимог:
- **REQ-Q1:** вимоги не задають максимального часу відповіді. Пропозиція: ≤ 500 ms (зараз PING — 1.35 s).
- **REQ-Q2:** у яких одиницях STATUS має повертати `pwm`? `SET PWM 50` відповідає `pwm:50`, а STATUS показує `pwm:127` (0..255). Пропозиція: ті самі одиниці, що й `SET PWM` (0..100); якщо вимогу уточнять так, поведінка стане дефектом прошивки. Додатково: у STATUS `led:true` при будь-якому PWM > 0 без `SET LED ON` — чи це очікувано?

Ризики автоматизації (не дефекти прошивки):
- Запізніла відповідь може приписатися наступній команді (п.6 розділу 3). Рекомендація: перед кожною командою вичитувати «залишки» з буфера, а відповіді звіряти з командою.
- Нестабільність середовища Wokwi (п.7–11). Рекомендація: перед прогоном smoke-перевірка `STATUS`, у helper — очікування готовності пристрою після підключення.

## 6. Висновок
Прошивка **не готова до релізу**: підтверджено 4 дефекти (1 Critical, 3 Major), стабільно відтворені в кількох прогонах, і 2 питання до вимог (REQ-Q1, REQ-Q2).
Решта падінь спричинена середовищем або зв'язком і не відтворюється у фінальному прогоні 10 (39 тестів: 32 PASS / 7 FAIL, 0 ERROR): усі 7 FAIL — це 4 дефекти прошивки + 3 кейси REQ-Q2.
Рекомендації: виправити BUG-01…04, уточнити REQ 2, додати вимогу щодо часу відповіді, підвищити стабільність helper-а (очищення буфера, очікування готовності), повторити повний прогін.
