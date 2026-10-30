# System Overview — ESP32 IoT Sensor/Actuator Node

IoT-вузол вимірює температуру й вологість, керує реле і передає телеметрію в мережу. Після збою він має сам повертатися в безпечний робочий стан.

## Architecture

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

## Components

| Компонент | Деталі | Перевірено в |
|---|---|---|
| ESP32 firmware | Arduino / PlatformIO, buggy-збірки `homework_buggy` | тиж. 2–6 |
| DHT22 | GPIO15, температура / вологість | тиж. 4, 5, 6 |
| Кнопка / digital input | GPIO4 (INPUT_PULLUP) / GPIO18, bounce, шум | тиж. 2, 4 |
| Actuator | реле GPIO5, LED GPIO2, PWM | тиж. 4, 5 |
| UART CLI | 115200, текстові команди, відповіді JSON | тиж. 3.1, 5 |
| I2C peripheral | MPU6050 @ 0x68, SDA 21 / SCL 22 | тиж. 3.2 |
| Persistent storage | NVS `qa-lab`: `counter`, `relay` | тиж. 4 |
| Watchdog / recovery | Task WDT 4000 ms, reset reason | тиж. 4 |
| Power mode | deep sleep, wake timer / ext0 | тиж. 4 |
| Wi-Fi / MQTT | state machine `CONNECTED → DISCONNECTED → BACKOFF ⇄ CONNECTING` | тиж. 6 |
| Offline buffer | capacity 8, політика DROP_OLDEST | тиж. 6 |
| Automation | Python / Pytest через RFC2217; log checks | тиж. 5, 7 |

## Inputs / Outputs

| Inputs | Outputs |
|---|---|
| DHT22, кнопка, I2C-датчик, CLI-команди, стан мережі | реле, LED, телеметрія MQTT, JSON-відповіді, Serial-лог |

## Critical functions

1. Sensor data acquisition: невалідні дані не подаються як валідні.
2. Local actuator control: реле в безпечному стані після будь-якого аварійного reset.
3. Communication over UART and network: контрольована помилка на некоректний ввід, телеметрія без втрат і дублікатів.
4. Recovery after firmware / network / peripheral fault: без ручного перезапуску.
5. Preservation of critical state: NVS завжди містить або стару, або нову повну версію.
6. Safe behavior after abnormal reset.
7. Stable long-running operation: без деградації heap.

## Critical data / actuators

- **Actuator:** реле. Неконтрольоване ввімкнення — ризик безпеки.
- **Data:** `counter` і `relay` у NVS; message ID телеметрії; лічильники `sent / dropped / duplicates`.

## Dependencies

MQTT-брокер / точка доступу, джерело живлення, хост для логування та автоматизації.

## Product goal

Пристрій має передбачувано працювати не лише в happy path, а й при шумі на входах, збоях протоколу, зависаннях, втраті живлення чи мережі та повторних recovery.

Далі: ризики та стратегія — [Master Test Plan](../master_test_plan/MASTER_TEST_PLAN.md).
