"""Власні параметризовані boundary / negative тести (ДЗ п.4).

Кожен тест посилається на вимогу з requirements/device_requirements.md.
Очікуваний результат взято з вимог, а не з поведінки прошивки.
"""
import pytest


# REQ 6: PWM поза 0..100 -> ERROR / INVALID_VALUE
# Межові значення: -100, -1 (нижня межа - 1), 101, 102 (верхня межа + 1/+2),
# 255 (максимум 8-бітного PWM), 1000 (явно завелике)
@pytest.mark.parametrize("value", [-100, -1, 101, 102, 255, 1000])
def test_pwm_out_of_range(clean_device, value):
    r = clean_device.command(f"SET PWM {value}")
    assert r["status"] == "ERROR"
    assert r["code"] == "INVALID_VALUE"


# REQ 5: SET PWM приймає лише цілі числа -> не-цілі / нечислові відхиляються
@pytest.mark.parametrize("text", ["abc", "5.5", "+5", "50%", "0x10"])
def test_pwm_not_integer(clean_device, text):
    r = clean_device.command(f"SET PWM {text}")
    assert r["status"] == "ERROR"
    assert r["code"] == "INVALID_VALUE"


# REQ 6 (негативний): невалідна команда не повинна змінювати поточний стан PWM
@pytest.mark.parametrize("bad", ["-1", "101", "abc"])
def test_invalid_pwm_keeps_state(clean_device, bad):
    assert clean_device.command("SET PWM 40")["status"] == "OK"
    before = clean_device.command("STATUS")
    clean_device.command(f"SET PWM {bad}")
    after = clean_device.command("STATUS")
    assert after["pwm"] == before["pwm"]


# REQ 8: невідомі команди -> структурована помилка UNKNOWN_COMMAND
@pytest.mark.parametrize("cmd", ["", "ping", "HELLO", "SET LED BLINK", "GET HUMIDITY"])
def test_unknown_command(clean_device, cmd):
    r = clean_device.command(cmd)
    assert r["status"] == "ERROR"
    assert r["code"] == "UNKNOWN_COMMAND"


# REQ 2: STATUS містить поточний стан PWM -> те саме значення, що встановили
@pytest.mark.parametrize("value", [0, 1, 50, 99])
def test_status_shows_pwm(clean_device, value):
    assert clean_device.command(f"SET PWM {value}")["status"] == "OK"
    assert clean_device.command("STATUS")["pwm"] == value
