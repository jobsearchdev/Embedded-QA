"""Перевірка поведінки при timeout (ДЗ п.5, REQ 9)."""
import time
import pytest


def test_timeout_is_finite(clean_device):
    start = time.monotonic()
    with pytest.raises(TimeoutError):
        clean_device.command("NO_RESPONSE")
    assert time.monotonic() - start < 1.5      # не чекає вічно (REQ 9)


def test_device_works_after_timeout(clean_device):
    with pytest.raises(TimeoutError):
        clean_device.command("NO_RESPONSE")
    assert clean_device.command("STATUS")["status"] == "OK"
