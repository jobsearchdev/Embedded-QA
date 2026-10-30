# Evidence Package Index

Кожен запис відповідає на питання: **яке твердження доводить цей артефакт і чи може інша людина його перевірити.**
Усі файли лежать у [`evidence/`](.). Шляхи відносні до кореня репозиторію.

| Evidence ID | Risk / Test | Type | Claim (що доводить) | File / Link |
|---|---|---|---|---|
| E01 | усі | Environment | Середовище відтворюване: macOS 26.6.2, Apple M3, VS Code 1.142.0, PlatformIO 6.2.0, Wokwi 4.1.0, 115200, `monitor_filters = time, log2file` | [`w06_network/00_environment.txt`](w06_network/00_environment.txt), [`environment_capture.png`](w06_network/environment_capture.png) |
| E02 | R01, R06 / T02, T18–T21 | Pytest output + JUnit XML | Фінальний прогін: 39 тестів, 32 PASS / 7 FAIL / 0 ERROR; 7 FAIL = 4 дефекти прошивки + 3 кейси REQ-Q2 | [`w05_pytest/06_final_run.txt`](w05_pytest/06_final_run.txt), [`report_final.xml`](w05_pytest/report_final.xml), [`TEST_SUMMARY_Wokwi.md`](w05_pytest/TEST_SUMMARY_Wokwi.md) |
| E03 | R06 / T15–T17 | Serial log (UART CLI) | 41-й символ викликає `SYSTEM FAULT` і `rst:0xc`; `set` у DIRTY скидає конфігурацію; `set speed 256` і `set timeout 0` приймаються | [`w03_uart_cli/SerialLog.md`](w03_uart_cli/SerialLog.md), [`Firmware_Test_Report.docx`](w03_uart_cli/Firmware_Test_Report.docx) |
| E04 | R01, R05 / T01, T03, T07, T12, T13 | Timestamped reset log + `status` до/після | Після 4/4 WDT reset `"relay":true`; reset через ≈ 9.4 с, `INT_WDT`; boot loop немає; heap 336332 стабільний | [`w04_recovery_nvs/TEST_REPORT_W4.md` §6–7, BUG-02, BUG-11](w04_recovery_nvs/TEST_REPORT_W4.md), [`serial_logs_W4.pdf`](w04_recovery_nvs/serial_logs_W4.pdf) |
| E05 | R05 / T11 | Logic trace (VCD → PulseView) + UART | Після NACK на 0x69 шина I2C idle, UART мовчить; після FAULT OFF відновлення немає (3/3 прогони) | [`w03_i2c/i2c_trace_overview_test1.png`](w03_i2c/i2c_trace_overview_test1.png), [`i2c_last_ack_first_nack_test1.png`](w03_i2c/i2c_last_ack_first_nack_test1.png), [`uart_fault_on_hang.png`](w03_i2c/uart_fault_on_hang.png), [`uart_after_fault_off_no_recovery.png`](w03_i2c/uart_after_fault_off_no_recovery.png), [`I2C_Blackbox_Report.docx`](w03_i2c/I2C_Blackbox_Report.docx) |
| E06 | R02 / T04, T05 | Before/after table + boot log | 6/6 `powerloss`: counter 2 → 102 → … → 602 без `[STORE] saved`, перевірки цілісності при boot немає | [`TEST_REPORT_W4.md` §8, BUG-03, BUG-06](w04_recovery_nvs/TEST_REPORT_W4.md) |
| E07 | R03 / T06 | Memory Stability Log (metrics trend) | Heap −8000 ± 12 B на кожні 100 повідомлень (10/10), 350868 → 266280 (−24 %) за сесію; ≈ 9 год до вичерпання при 1 повідомленні / 10 с | [`w06_network/full-261030-143015.log`](w06_network/full-261030-143015.log) (15:00:04–15:01:37), [`Week6_IoT_Network_Testing_Report.docx` §3 D](w06_network/Week6_IoT_Network_Testing_Report.docx) |
| E08 | R04 / T08–T10 | Message IDs / counters | Кожен буферизований ID публікується ×2 (до ×6 з overflow); `count=12/8`, `dropped=0`; ID 6–9, 26, 1035–1046 зникли без обліку | [`full-261030-143015.log`](w06_network/full-261030-143015.log) (14:41–14:54, 15:01), Week 6 report §3 B–C |
| E09 | R07, R08, R10 / T22–T26, T32 | Timestamped Serial log | DHT22 від'єднано → `temp=0.0C` при `sensor_ok:false`; `sleep 5` → 0.54 с, `sleep 10` → 1.03–1.04 с (6 вимірів), `sleep 60` → 6.06 с | [`TEST_REPORT_W4.md` §5, BUG-01, BUG-04, BUG-05, BUG-08](w04_recovery_nvs/TEST_REPORT_W4.md) |
| E10 | R10 / T29–T31 | Logic analyzer (RAW D0 vs LOGICAL D1) + лічильники | Bounce 103/195 фронтів дає 1 logical event (PASS); NOISE під час critical operation дає зайву ACTION 5/5 | [`w02_debounce/logic_analyzer_TC-02_bounce.png`](w02_debounce/logic_analyzer_TC-02_bounce.png), [`TC-06_evidence.png`](w02_debounce/TC-06_evidence.png), [`serial.md`](w02_debounce/serial.md), [`Debounce_Homework.docx`](w02_debounce/Debounce_Homework.docx) |
| E11 | R05, R09 / T14, T27, T28 | Network log + скріншоти | State model `CONNECTED → DISCONNECTED → BACKOFF ⇄ CONNECTING → CONNECTED`; retry кожні ~50 мс (180 спроб за 9.4 с); після `NET UP` — `reconnect=SUCCESS`, LED ON | [`device-monitor-261030-134738.log`](w06_network/device-monitor-261030-134738.log), [`net_down_backoff_50ms_led_off.png`](w06_network/net_down_backoff_50ms_led_off.png), [`net_up_reconnect_success_led_on.png`](w06_network/net_up_reconnect_success_led_on.png) |
| E12 | R03, R04, R09 / T06, T09, T10, T27, T28 | Automated log analysis (pytest) | Незалежна автоматична перевірка логу тижня 6: 1 PASS (R1), 5 FAIL (R2, R4 ×2, R6, R7); 37 ID дубльовано; медіана retry 50 мс | [`w06_network/log_checks_result.txt`](w06_network/log_checks_result.txt), код: [`automation/log_checks/`](../automation/log_checks) |
| E13 | R01 / T02 | Pytest fixture log | `RESET` не повертає безпечний стан: фікстура `clean_device` фіксує `pwm:127` після `RESET` і вмикає fallback | [`w05_pytest/05_clean_device_fallback.txt`](w05_pytest/05_clean_device_fallback.txt), [`BUG-04_reset.txt`](w05_pytest/BUG-04_reset.txt) |
| E14 | методологія | Test sheet + bug report (окремий продукт) | Тиждень 1, Smart Gate Controller (Arduino Uno): black-box state machine, 4 дефекти. Не входить у SUT, показує підхід до тестування актуатора | [`w01_gate/Hardware_Test_Sheet_Test_Log.docx`](w01_gate/Hardware_Test_Sheet_Test_Log.docx), [`Bug_Report.xlsx`](w01_gate/Bug_Report.xlsx) |

## Код автоматизації

- Pytest suite (тиж. 5): [`automation/pytest_device/`](../automation/pytest_device) — `tests/`, `conftest.py`, `device.py`
- Log checks (тиж. 7): [`automation/log_checks/`](../automation/log_checks)

## Відомі прогалини в evidence

| Прогалина | Вплив | Компенсація |
|---|---|---|
| Сирі VCD-файли I2C (`wokwi1–3.vcd`) не збережено | трейс не можна перекодувати повторно | є декодовані діаграми з тих самих VCD + UART + таблиця часу NACK для 3 прогонів |
| VCD тижня 2 не збережено | так само | скріншот LA з лічильниками фронтів + відео (поза репозиторієм) |
| Сирий Serial-лог тижня 4 лише у PDF | незручно для автоматичного аналізу | повні фрагменти з мітками часу у звіті й bug reports |
| Memory evidence лише за хвилини роботи | лінійний тренд доведено, поведінку за 24–72 год — ні | Residual risk у MTP §16 |

## Правило

Evidence має дозволяти іншій людині перевірити висновок QA без автора: часова мітка, команда, відповідь, кількість повторів.
