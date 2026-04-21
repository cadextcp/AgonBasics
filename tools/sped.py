#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Startet den SPED Sprite-Editor im GUI-Emulator.

Convenience-Wrapper um `tools/run.py --program sped.bas`. Sorgt dafuer,
dass vorher `tools/deploy.py` gelaufen ist, damit `werkzeuge/sprite_editor/
sped.bas` + `sped.ini` auf der gestagten SD-Karte liegen.

Optionen werden an run.py durchgereicht, z. B.:

    uv run tools/sped.py                # GUI
    uv run tools/sped.py --fullscreen   # GUI-Vollbild
    uv run tools/sped.py -u              # ohne CPU-Limit

Fuer Details zum Editor selbst: werkzeuge/sprite_editor/README.md.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEPLOY = ROOT / "tools" / "deploy.py"
RUN = ROOT / "tools" / "run.py"


def main() -> int:
    # erst deploy, damit aktuelle Version von sped.bas + sped.ini auf
    # der gestagten SD-Karte landet
    rc = subprocess.call(["uv", "run", str(DEPLOY)])
    if rc != 0:
        print("[sped] deploy fehlgeschlagen", file=sys.stderr)
        return rc

    # dann starten; Extra-Argumente weiterreichen
    cmd = ["uv", "run", str(RUN), "--program", "sped.bas"] + sys.argv[1:]
    return subprocess.call(cmd)


if __name__ == "__main__":
    raise SystemExit(main())
