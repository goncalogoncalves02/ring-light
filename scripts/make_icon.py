"""Generate the placeholder app icon (favicon.ico) for RingLight Overlay.

Run with:
    python scripts/make_icon.py

Requires Pillow (dev dependency). Produces a multi-resolution .ico file with
six embedded sizes: 16, 32, 48, 64, 128, 256. The image shows a warm-colored
ring on a transparent background.

Re-run this script to regenerate the icon. The user may also replace the
output file with a professionally designed icon of the same name and same
six embedded sizes.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

_SIZES: list[tuple[int, int]] = [
    (16, 16),
    (32, 32),
    (48, 48),
    (64, 64),
    (128, 128),
    (256, 256),
]
_RING_COLOR = (255, 165, 30, 255)  # warm amber, fully opaque
_OUTPUT_REL = Path("ringlight_overlay") / "resources" / "icons" / "favicon.ico"


def _draw_ring(size: int) -> Image.Image:
    """Draw a ring icon on a transparent canvas of the given square size."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    margin = max(1, size // 8)
    inner_margin = max(2, size // 4)

    outer_box = [margin, margin, size - margin, size - margin]
    inner_box = [inner_margin, inner_margin, size - inner_margin, size - inner_margin]

    draw.ellipse(outer_box, fill=_RING_COLOR)
    draw.ellipse(inner_box, fill=(0, 0, 0, 0))

    return img


def build_icon(output_path: Path) -> None:
    """Build a multi-resolution favicon.ico and write it to *output_path*."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    base = _draw_ring(256)
    additional = [_draw_ring(s) for (s, _) in _SIZES[:-1]]

    base.save(
        output_path,
        format="ICO",
        sizes=_SIZES,
        append_images=additional,
    )
    print(f"Icon written to: {output_path}")


if __name__ == "__main__":
    repo_root = Path(__file__).resolve().parent.parent
    build_icon(repo_root / _OUTPUT_REL)
