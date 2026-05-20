from __future__ import annotations

import math

KELVIN_MIN = 1000
KELVIN_MAX = 40000


def kelvin_to_rgb(kelvin: int) -> tuple[int, int, int]:
    """Convert color temperature in Kelvin to approximate sRGB.

    Implements Tanner Helland's algorithm. Input clamped to [1000, 40000].
    """
    temp = max(KELVIN_MIN, min(KELVIN_MAX, kelvin)) / 100

    if temp <= 66:
        red = 255.0
    else:
        red = 329.698727446 * ((temp - 60) ** -0.1332047592)

    if temp <= 66:
        green = 99.4708025861 * math.log(temp) - 161.1195681661
    else:
        green = 288.1221695283 * ((temp - 60) ** -0.0755148492)

    if temp >= 66:
        blue = 255.0
    elif temp <= 19:
        blue = 0.0
    else:
        blue = 138.5177312231 * math.log(temp - 10) - 305.0447927307

    r = int(max(0, min(255, round(red))))
    g = int(max(0, min(255, round(green))))
    b = int(max(0, min(255, round(blue))))
    return (r, g, b)


def apply_brightness(rgb: tuple[int, int, int], brightness: float) -> tuple[int, int, int]:
    """Scale RGB toward black by ``brightness`` (0.0 = black, 1.0 = unchanged)."""
    if not (0.0 <= brightness <= 1.0):
        raise ValueError(f"brightness must be in [0.0, 1.0], got {brightness!r}")
    r = int(round(rgb[0] * brightness))
    g = int(round(rgb[1] * brightness))
    b = int(round(rgb[2] * brightness))
    return (r, g, b)
