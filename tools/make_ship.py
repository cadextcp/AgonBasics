#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Erzeugt ein 16x16 Schiff-Sprite als RGBA8888 fuer den Agon-VDP.
Byte-Reihenfolge pro Pixel: A, B, G, R (wie vom VDP erwartet).

Schreibt die Datei nach beispiele/ship.rgba. Der Deploy-Schritt
(tools/deploy.py) kopiert sie dann in die gestagte SD-Karte.
"""

from pathlib import Path


def px(r, g, b, a=255):
    """Gibt 4 Bytes in VDP-Byte-Reihenfolge zurueck: A, B, G, R."""
    return (a, b, g, r)


T = px(0, 0, 0, 0)          # Transparent
C = px(0, 220, 255)          # Cyan - Rumpf
W = px(255, 255, 255)        # Weiss - Cockpit
R = px(255, 60, 0)           # Rot/Orange - Flammenrand
Y = px(255, 255, 80)         # Gelb - Flammenkern

# 16x16 Schiff (Draufsicht, zeigt nach oben)
ship = [
    # Row 0-3: Nase und Cockpit
    T, T, T, T, T, T, T, C,  C, T, T, T, T, T, T, T,
    T, T, T, T, T, T, C, C,  C, C, T, T, T, T, T, T,
    T, T, T, T, T, C, C, W,  W, C, C, T, T, T, T, T,
    T, T, T, T, T, C, W, W,  W, W, C, T, T, T, T, T,
    # Row 4-6: Rumpf wird breiter
    T, T, T, T, C, C, C, C,  C, C, C, C, T, T, T, T,
    T, T, T, C, C, C, C, C,  C, C, C, C, C, T, T, T,
    T, T, C, C, C, C, C, C,  C, C, C, C, C, C, T, T,
    # Row 7-9: Fluegel
    T, C, C, T, C, C, C, C,  C, C, C, C, T, C, C, T,
    C, C, T, T, C, C, C, C,  C, C, C, C, T, T, C, C,
    C, T, T, T, T, C, C, C,  C, C, C, T, T, T, T, C,
    # Row 10-11: unterer Rumpf
    T, T, T, T, T, C, C, C,  C, C, C, T, T, T, T, T,
    T, T, T, T, T, T, C, C,  C, C, T, T, T, T, T, T,
    # Row 12-15: Triebwerksflammen
    T, T, T, T, T, T, C, R,  R, C, T, T, T, T, T, T,
    T, T, T, T, T, T, R, Y,  Y, R, T, T, T, T, T, T,
    T, T, T, T, T, T, T, Y,  Y, T, T, T, T, T, T, T,
    T, T, T, T, T, T, T, R,  R, T, T, T, T, T, T, T,
]

assert len(ship) == 256, f"Erwartet 256 Pixel, gesehen {len(ship)}"

# Als flaches Byte-Array schreiben (4 Bytes pro Pixel = 1024 Bytes)
data = bytearray()
for a, b, g, r in ship:
    data.extend([a, b, g, r])

assert len(data) == 1024, f"Erwartet 1024 Bytes, gesehen {len(data)}"

root = Path(__file__).resolve().parent.parent
out = root / "beispiele" / "ship.rgba"
out.parent.mkdir(parents=True, exist_ok=True)
with out.open("wb") as f:
    f.write(data)

print(f"ship.rgba geschrieben: {out} ({len(data)} Bytes, RGBA8888 ABGR)")
