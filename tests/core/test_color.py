from __future__ import annotations

import pytest

from ringlight_overlay.core.color import apply_brightness, kelvin_to_rgb


@pytest.mark.parametrize("kelvin", [1000, 2700, 5600, 6500, 40000])
def test_kelvin_returns_three_ints_in_range(kelvin: int) -> None:
    rgb = kelvin_to_rgb(kelvin)
    assert isinstance(rgb, tuple) and len(rgb) == 3
    for c in rgb:
        assert isinstance(c, int)
        assert 0 <= c <= 255


def test_kelvin_low_end_has_no_blue() -> None:
    r, g, b = kelvin_to_rgb(1000)
    assert r == 255
    assert b == 0


def test_kelvin_at_6600_boundary_is_full_white_ish() -> None:
    r, _, b = kelvin_to_rgb(6600)
    assert r == 255
    assert b == 255


def test_kelvin_high_end_has_no_red_cap() -> None:
    r, _, b = kelvin_to_rgb(40000)
    assert b == 255
    assert r < 200


def test_kelvin_clamps_below_minimum() -> None:
    assert kelvin_to_rgb(500) == kelvin_to_rgb(1000)


def test_kelvin_clamps_above_maximum() -> None:
    assert kelvin_to_rgb(50000) == kelvin_to_rgb(40000)


def test_apply_brightness_zero_returns_black() -> None:
    assert apply_brightness((200, 100, 50), 0.0) == (0, 0, 0)


def test_apply_brightness_one_returns_input() -> None:
    assert apply_brightness((200, 100, 50), 1.0) == (200, 100, 50)


def test_apply_brightness_half_halves_channels() -> None:
    assert apply_brightness((200, 100, 50), 0.5) == (100, 50, 25)


def test_apply_brightness_rejects_out_of_range() -> None:
    with pytest.raises(ValueError):
        apply_brightness((255, 255, 255), 1.5)
    with pytest.raises(ValueError):
        apply_brightness((255, 255, 255), -0.1)
