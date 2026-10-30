# ESP32 IoT Sensor/Actuator Node — Embedded QA Case Study

## What this repository demonstrates

Risk-based тестування IoT-вузла на ESP32, який керує реле й передає телеметрію. Головне питання: чи безпечно поводиться пристрій після збоїв (hang, power loss, втрата мережі, збій периферії) і чи можна його випускати.
**Висновок: NO-GO.** Після збою реле вмикається само, persistent data пошкоджуються непомітно, а heap закінчиться приблизно за 9 годин роботи.

## System

Детально: [case_study/SYSTEM_OVERVIEW.md](case_study/SYSTEM_OVERVIEW.md)


ESP32 DevKit V1 · DHT22 · кнопка · реле + LED · I2C-периферія · UART CLI (JSON) · NVS · Task WDT · deep sleep · Wi-Fi/MQTT з офлайн-буфером (capacity 8).
Тестування black-box у Wokwi (VS Code + PlatformIO), Logic Analyzer + PulseView, Python/Pytest.

## Main quality risks

- **R01** — після аварійного reset реле стає ON (небезпечний стан актуатора)
- **R02** — перерваний запис NVS залишає змішаний state, який приймається як валідний
- **R03** — heap деградує з кожним повідомленням → відмова вузла
- **R04** — телеметрія губиться або дублюється після reconnect без обліку
- **R05** — hang або збій I2C без самовідновлення

## Test strategy

- [Master Test Plan](master_test_plan/MASTER_TEST_PLAN.md): scope, out of scope, 10 ризиків, рівні, середовища, Entry/Exit Criteria, regression, residual risks
- [Final Test Matrix](test_matrix/FINAL_TEST_MATRIX.md): 32 тести, кожен прив'язаний до ризику й evidence
- [Case Study](portfolio/CASE_STUDY.md): повна історія Problem → Risk → Test → Evidence → Finding → Decision

## Key evidence

| | Що доводить |
|---|---|
| [E04 WDT reset log](evidence/w04_recovery_nvs/TEST_REPORT_W4.md) | `hang → rst:0x8 → INT_WDT → "relay":true`, 4/4 |
| [E05 I2C trace](evidence/w03_i2c/i2c_last_ack_first_nack_test1.png) | NACK на 0x69 → шина й main loop мовчать назавжди |
| [E07 Memory log](evidence/w06_network/full-261030-143015.log) | heap −8000 B на кожні 100 повідомлень, 10/10 |
| [E12 Log checks](evidence/w06_network/log_checks_result.txt) | автоматична перевірка: 37 ID дубльовано, retry кожні 50 мс |
| [E02 Pytest](evidence/w05_pytest/06_final_run.txt) | 39 тестів: 32 PASS / 7 FAIL / 0 ERROR |

Повний перелік — [Evidence Index](evidence/EVIDENCE_INDEX.md).

## Key findings

**9 Critical · 14 Major · 7 Minor** — [Bug Reports](portfolio/BUG_REPORTS.md).

1. **D-01** Реле відновлюється у ON після WDT reset (4/4)
2. **D-03** Power loss під час save: counter 2 → 602 за 6 циклів без жодного підтвердженого запису
3. **D-04** Витік heap 80 B / повідомлення → відмова через ≈ 9 год
4. **D-05** Буфер переповнюється (`12/8`), втрати не облікуються, ID дублюються до ×6
5. **D-06** Один I2C NACK зупиняє систему до ручного перезапуску

## Automation

**Pytest suite** (тиждень 5): [`automation/pytest_device/`](automation/pytest_device) — 39 тестів CLI через UART
```bash
cd automation/pytest_device
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# запустити симуляцію Wokwi (RFC2217 на порту 4000)
DEVICE_PORT=rfc2217://localhost:4000 pytest -v --junitxml=evidence/report.xml
```

**Log checks** (тиждень 7): [`automation/log_checks/`](automation/log_checks) — перевірка вимог по збереженому Serial-логу, без пристрою.
```bash
pip install pytest
pytest -v automation/log_checks/                          # лог тижня 6
NET_LOG=path/to/new.log pytest -v automation/log_checks/  # новий прогін
python automation/log_checks/network_log.py evidence/w06_network/full-261030-143015.log
```
На buggy build очікувано 1 PASS / 5 FAIL. Після виправлення прошивки ті самі перевірки мають пройти.

## Limitations

Усе перевірено в симуляції. Потребують реального заліза: brown-out під час запису NVS, bounce реальної кнопки, Wi-Fi/MQTT QoS, heap за 24–72 год, знос Flash. Модулі тестувалися на окремих навчальних збірках, тому інтеграцію між ними не перевірено. Деталі — [MTP §5, §16](master_test_plan/MASTER_TEST_PLAN.md#5-out-of-scope).

## Conclusion

**NO-GO** — [Release Decision](templates/RELEASE_DECISION.md). Відкриті дефекти зачіпають усі п'ять P1-ризиків, і жоден із них не можна обійти в полі. Для повторної оцінки потрібно: виправити D-01…D-09, пройти Pytest 39/39 і log checks 6/6 тричі поспіль, а перед production — перевірити на реальному стенді.

## Repository structure

```
case_study/        SYSTEM_OVERVIEW.md
evidence/          EVIDENCE_INDEX.md + артефакти w01…w06
homework/          HOMEWORK.md — статус виконання вимог
instructor/        DEFENSE_RUBRIC.md (самооцінка), INSTRUCTOR_GUIDE.md (як перевірити)
master_test_plan/  MASTER_TEST_PLAN.md
portfolio/         CASE_STUDY.md, BUG_REPORTS.md
templates/         RELEASE_DECISION.md
test_matrix/       FINAL_TEST_MATRIX.md
automation/        pytest_device/ (39 тестів CLI), log_checks/ (перевірка Serial-логів)
```

---

 Автор: Evhenii Kofan · Курс Embedded QA (IoT / DefTech), 2026
