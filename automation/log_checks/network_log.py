"""Парсер Serial-логу IoT-ноди (Week 6) для автоматичної перевірки evidence.

Читає лог PlatformIO Serial Monitor (monitor_filters = time) і витягує
факти, на яких базуються висновки QA: стани мережі, інтервали retry,
publish ID, розмір буфера, heap до/після STRESS.

Запуск як CLI:  python network_log.py ../evidence/w06_network/full-261030-143015.log
"""
from __future__ import annotations

import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime

TS = re.compile(r"(\d{2}:\d{2}:\d{2}\.\d{3}) > (.*)$")


@dataclass
class NetworkLog:
    states: list[str] = field(default_factory=list)
    attempt_times: list[datetime] = field(default_factory=list)
    publish_ids: Counter = field(default_factory=Counter)
    buffer_counts: list[tuple[int, int]] = field(default_factory=list)  # (count, capacity)
    stress_heap: list[tuple[int, int]] = field(default_factory=list)  # (start, end)
    dropped_values: list[int] = field(default_factory=list)


def parse(path: str) -> NetworkLog:
    log = NetworkLog()
    stress_start = None
    with open(path, encoding="utf-8", errors="replace") as fh:
        for raw in fh:
            m = TS.search(raw)
            if not m:
                continue
            ts, msg = m.groups()
            if (s := re.search(r"\[NET\] state=(\w+)", msg)):
                log.states.append(s.group(1))
                if s.group(1) == "CONNECTING":
                    log.attempt_times.append(datetime.strptime(ts, "%H:%M:%S.%f"))
            elif (p := re.search(r"\[MQTT\] publish id=(\d+)", msg)):
                log.publish_ids[int(p.group(1))] += 1
            elif (b := re.search(r"count=(\d+)(?:/| capacity=)(\d+)", msg)):
                log.buffer_counts.append((int(b.group(1)), int(b.group(2))))
            if (st := re.search(r"\[STRESS\] start .*heap=(\d+)", msg)):
                stress_start = int(st.group(1))
            elif (en := re.search(r"\[STRESS\] end heap=(\d+)", msg)) and stress_start:
                log.stress_heap.append((stress_start, int(en.group(1))))
                stress_start = None
            if (d := re.search(r'"dropped":(\d+)', msg)):
                log.dropped_values.append(int(d.group(1)))
    return log


def retry_intervals_ms(log: NetworkLog) -> list[float]:
    """Інтервали між сусідніми спробами CONNECTING (лише в межах одного outage, < 5 с)."""
    t = log.attempt_times
    out = [(b - a).total_seconds() * 1000 for a, b in zip(t, t[1:])]
    return [x for x in out if x < 5000]


def summary(path: str) -> str:
    log = parse(path)
    iv = sorted(retry_intervals_ms(log))
    dups = {i: n for i, n in log.publish_ids.items() if n > 1}
    leak = [s - e for s, e in log.stress_heap]
    over = [c for c in log.buffer_counts if c[0] > c[1]]
    lines = [
        f"States seen: {sorted(set(log.states))}",
        f"Retry intervals: n={len(iv)}, median={iv[len(iv)//2] if iv else '-'} ms",
        f"Publish IDs: {len(log.publish_ids)} unique, {len(dups)} duplicated, max x{max(log.publish_ids.values(), default=0)}",
        f"Buffer over capacity: {len(over)} records, max {max(over, default='-')}",
        f"STRESS heap delta per run: {leak}",
        f"Max 'dropped' in STATUS: {max(log.dropped_values, default=0)}",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    print(summary(sys.argv[1]))
