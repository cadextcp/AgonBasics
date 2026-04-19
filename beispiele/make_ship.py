#!/usr/bin/env python3
"""Generate a 16x16 ship sprite in RGBA8888 format for Agon VDP.
Byte order per pixel: A, B, G, R (as expected by VDP)."""

def px(r, g, b, a=255):
    """Return 4 bytes in VDP byte order: A, B, G, R."""
    return (a, b, g, r)

T = px(0, 0, 0, 0)         # Transparent
C = px(0, 220, 255)         # Cyan - ship body
W = px(255, 255, 255)       # White - cockpit
R = px(255, 60, 0)          # Red/orange - flame edge
Y = px(255, 255, 80)        # Yellow - flame core

# 16x16 ship design (top-down view, pointing up)
ship = [
    # Row 0-3: nose and cockpit
    T,T,T,T,T,T,T,C, C,T,T,T,T,T,T,T,
    T,T,T,T,T,T,C,C, C,C,T,T,T,T,T,T,
    T,T,T,T,T,C,C,W, W,C,C,T,T,T,T,T,
    T,T,T,T,T,C,W,W, W,W,C,T,T,T,T,T,
    # Row 4-6: body widens
    T,T,T,T,C,C,C,C, C,C,C,C,T,T,T,T,
    T,T,T,C,C,C,C,C, C,C,C,C,C,T,T,T,
    T,T,C,C,C,C,C,C, C,C,C,C,C,C,T,T,
    # Row 7-9: wings
    T,C,C,T,C,C,C,C, C,C,C,C,T,C,C,T,
    C,C,T,T,C,C,C,C, C,C,C,C,T,T,C,C,
    C,T,T,T,T,C,C,C, C,C,C,T,T,T,T,C,
    # Row 10-11: lower body
    T,T,T,T,T,C,C,C, C,C,C,T,T,T,T,T,
    T,T,T,T,T,T,C,C, C,C,T,T,T,T,T,T,
    # Row 12-15: engine flames
    T,T,T,T,T,T,C,R, R,C,T,T,T,T,T,T,
    T,T,T,T,T,T,R,Y, Y,R,T,T,T,T,T,T,
    T,T,T,T,T,T,T,Y, Y,T,T,T,T,T,T,T,
    T,T,T,T,T,T,T,R, R,T,T,T,T,T,T,T,
]

assert len(ship) == 256, f"Expected 256 pixels, got {len(ship)}"

# Write as flat bytes (4 bytes per pixel = 1024 bytes total)
data = bytearray()
for a, b, g, r in ship:
    data.extend([a, b, g, r])

assert len(data) == 1024, f"Expected 1024 bytes, got {len(data)}"

with open("sdcard/beispiele/ship.rgba", "wb") as f:
    f.write(data)

print(f"ship.rgba written ({len(data)} bytes, RGBA8888 ABGR byte order)")
