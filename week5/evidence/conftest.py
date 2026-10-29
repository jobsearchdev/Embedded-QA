import os
import pytest
from device import Device


@pytest.fixture
def device():
    port = os.getenv("DEVICE_PORT")
    if not port:
        pytest.skip("Set DEVICE_PORT, e.g. COM5, /dev/ttyUSB0 or rfc2217://localhost:4000 (Wokwi)")
    dev = Device(port, timeout=1.0)
    yield dev
    try:
        dev.command("RESET")
    finally:
        dev.close()


@pytest.fixture
def clean_device(device):
    """Контрольований precondition і cleanup (ДЗ п.6).

    PRECONDITION: тест стартує з безпечного стану LED OFF / PWM 0.
    RESET має дефект (BUG-04), тому стан перевіряємо через STATUS
    і за потреби скидаємо вручну через SET LED OFF (fallback).
    """
    device.command("RESET")
    st = device.command("STATUS")
    if st["pwm"] != 0 or st["led"] is not False:
        print(f"\nWARNING: RESET не спрацював: {st} -> fallback SET LED OFF")
        device.command("SET LED OFF")
        st = device.command("STATUS")
    assert st["pwm"] == 0 and st["led"] is False, f"Precondition failed: {st}"

    yield device

    # CLEANUP: прибрати після тесту (не покладаємось на RESET)
    device.command("SET LED OFF")
