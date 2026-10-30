"""Evidence-based regression: перевірка вимог R1–R7 (Week 6) по Serial-логу.

Тести не підключаються до пристрою — вони аналізують збережений лог.
Ідея: після кожного нового прогону в Wokwi/на стенді зберегти лог і
запустити ці перевірки. На buggy build очікувано FAIL (це і є evidence),
після виправлення прошивки ті самі тести мають стати PASS.

Запуск:
    pytest -v log_checks/                       # лог за замовчуванням
    NET_LOG=path/to/new.log pytest -v log_checks/
"""
import os
import statistics
from pathlib import Path

import pytest

from network_log import parse, retry_intervals_ms

DEFAULT_LOG = Path(__file__).parent.parent.parent / "evidence/w06_network/full-261030-143015.log"
LOG_PATH = os.environ.get("NET_LOG", str(DEFAULT_LOG))

# Пороги — з requirements R2, R4, R6, R7 (Week 6) і Exit Criteria MTP
MIN_BACKOFF_MEDIAN_MS = 500      # R2: backoff не менше першого інтервалу
MAX_HEAP_LOSS_PER_100_MSG = 512  # R7: допуск на фрагментацію, не систематичне падіння


@pytest.fixture(scope="module")
def log():
    return parse(LOG_PATH)


def test_r1_all_network_states_observable(log):
    assert {"CONNECTED", "DISCONNECTED", "BACKOFF", "CONNECTING"} <= set(log.states)


def test_r2_reconnect_uses_backoff_not_storm(log):
    iv = retry_intervals_ms(log)
    assert iv, "у лозі немає спроб reconnect"
    median = statistics.median(iv)
    assert median >= MIN_BACKOFF_MEDIAN_MS, f"reconnect storm: median retry interval {median:.0f} ms"


def test_r4_buffer_never_exceeds_capacity(log):
    over = [c for c in log.buffer_counts if c[0] > c[1]]
    assert not over, f"buffer count > capacity: {sorted(set(over))[:5]}"


def test_r4_overflow_is_accounted(log):
    overflowed = any(c > cap for c, cap in log.buffer_counts)
    if overflowed:
        assert max(log.dropped_values, default=0) > 0, "overflow був, але dropped у STATUS завжди 0"


def test_r6_each_message_published_once(log):
    dups = {i: n for i, n in log.publish_ids.items() if n > 1}
    assert not dups, f"{len(dups)} ID опубліковано більше 1 разу, напр. {list(dups.items())[:5]}"


def test_r7_heap_stable_under_stress(log):
    assert log.stress_heap, "у лозі немає STRESS-прогонів"
    worst = max(start - end for start, end in log.stress_heap)
    assert worst <= MAX_HEAP_LOSS_PER_100_MSG, f"heap втрачає {worst} B за STRESS 100"
