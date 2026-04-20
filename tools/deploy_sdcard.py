#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Kopiert sdcard/staged/ auf eine physische microSD-Karte.

Sicherheitsmassnahmen:
  - Nur Wechseldatenraeger (Windows: DRIVE_REMOVABLE) werden akzeptiert.
  - Niemals auf das Systemlaufwerk schreiben.
  - Ohne --confirm wird nur angezeigt, was passieren wuerde (Dry-Run).

Aufruf (Windows):
    uv run tools/deploy_sdcard.py F:
        Dry-Run: zeigt nur an, was kopiert wuerde.

    uv run tools/deploy_sdcard.py F: --confirm
        Kopiert wirklich. Ueberschreibt gleichnamige Zieldateien.

    uv run tools/deploy_sdcard.py F: --confirm --mirror
        Kopiert und entfernt zusaetzlich Dateien, die im Ziel liegen,
        aber nicht in sdcard/staged/ existieren. GEFAEHRLICH: alles auf
        der SD, was nicht zum Projekt gehoert, wird geloescht!

Aufruf (Linux/macOS):
    uv run tools/deploy_sdcard.py /media/$USER/AGON
"""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SDCARD_STAGED = ROOT / "sdcard" / "staged"


# Windows API-Konstanten
DRIVE_UNKNOWN = 0
DRIVE_NO_ROOT_DIR = 1
DRIVE_REMOVABLE = 2
DRIVE_FIXED = 3
DRIVE_REMOTE = 4
DRIVE_CDROM = 5
DRIVE_RAMDISK = 6
DRIVE_TYPES = {
    0: "UNKNOWN",
    1: "NO_ROOT_DIR",
    2: "REMOVABLE",
    3: "FIXED",
    4: "REMOTE",
    5: "CDROM",
    6: "RAMDISK",
}


def log(msg: str) -> None:
    print(f"[deploy_sdcard] {msg}", flush=True)


def windows_drive_type(path: Path) -> int:
    """Gibt den Windows-Laufwerkstyp der Wurzel von path zurueck."""
    root = str(path.resolve().anchor)  # z.B. "F:\"
    if not root:
        return DRIVE_UNKNOWN
    return ctypes.windll.kernel32.GetDriveTypeW(ctypes.c_wchar_p(root))


def windows_system_drive() -> str:
    """Gibt das Systemlaufwerk zurueck (z.B. 'C:\\')."""
    sd = os.environ.get("SystemDrive", "C:")
    if not sd.endswith("\\"):
        sd += "\\"
    return sd


def assert_safe_target(target: Path) -> None:
    """Stellt sicher, dass das Ziel ein Wechseldatenraeger und nicht System ist."""
    target = target.resolve()

    if sys.platform.startswith("win"):
        dt = windows_drive_type(target)
        log(f"Laufwerkstyp: {DRIVE_TYPES.get(dt, 'UNKNOWN')} ({dt})")
        if dt != DRIVE_REMOVABLE:
            raise SystemExit(
                f"Abgebrochen: Ziel {target} ist kein Wechseldatenraeger. "
                f"Nur DRIVE_REMOVABLE (microSD-Kartenleser etc.) wird erlaubt."
            )
        sysdrive = windows_system_drive().rstrip("\\").upper()
        target_drive = str(target.anchor).rstrip("\\").upper()
        if target_drive == sysdrive:
            raise SystemExit(
                f"Abgebrochen: Ziel {target} liegt auf dem Systemlaufwerk."
            )
    else:
        # Linux/macOS: sehr konservativ - Ziel MUSS unter /media, /mnt, /Volumes
        # oder /run/media liegen. Nicht das root-Dateisystem.
        parts = target.parts
        if target == Path(target.anchor):
            raise SystemExit(
                f"Abgebrochen: Ziel {target} ist ein Root-Dateisystem."
            )
        mount_prefixes = ("/media", "/mnt", "/Volumes", "/run/media")
        if not any(str(target).startswith(p) for p in mount_prefixes):
            raise SystemExit(
                f"Abgebrochen: Ziel {target} liegt nicht unter "
                f"{mount_prefixes}. Falls das gewollt ist, per --force-path "
                f"ausdruecklich bestaetigen."
            )


def hash_file(path: Path, chunk: int = 65536) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fp:
        for b in iter(lambda: fp.read(chunk), b""):
            h.update(b)
    return h.hexdigest()


def plan_copy(src: Path, dst: Path) -> tuple[list[Path], list[Path], list[Path]]:
    """Gibt (neu, aenderung, gleich) zurueck.

    - neu: Dateien, die im Ziel fehlen
    - aenderung: Dateien mit unterschiedlichem Inhalt
    - gleich: identische Dateien (werden uebersprungen)
    """
    neu: list[Path] = []
    aend: list[Path] = []
    gleich: list[Path] = []
    for srcfile in src.rglob("*"):
        if srcfile.is_dir():
            continue
        rel = srcfile.relative_to(src)
        dstfile = dst / rel
        if not dstfile.exists():
            neu.append(rel)
            continue
        if dstfile.stat().st_size != srcfile.stat().st_size or hash_file(
            dstfile
        ) != hash_file(srcfile):
            aend.append(rel)
        else:
            gleich.append(rel)
    return neu, aend, gleich


def plan_delete(src: Path, dst: Path) -> list[Path]:
    """Dateien, die im Ziel liegen, aber nicht in src vorkommen (fuer --mirror)."""
    if not dst.exists():
        return []
    extra: list[Path] = []
    for dstfile in dst.rglob("*"):
        if dstfile.is_dir():
            continue
        rel = dstfile.relative_to(dst)
        srcfile = src / rel
        if not srcfile.exists():
            extra.append(rel)
    return extra


def apply_copy(src: Path, dst: Path, rels: list[Path]) -> None:
    for rel in rels:
        target = dst / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src / rel, target)


def apply_delete(dst: Path, rels: list[Path]) -> None:
    for rel in rels:
        (dst / rel).unlink()


def main() -> int:
    parser = argparse.ArgumentParser(description="AgonBasics deploy to microSD")
    parser.add_argument(
        "target", type=Path, help="Zielpfad (Windows: F:\\, Linux: /media/...)"
    )
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="Tatsaechlich kopieren (ohne --confirm: Dry-Run)",
    )
    parser.add_argument(
        "--mirror",
        action="store_true",
        help="Zusaetzlich Dateien im Ziel loeschen, die nicht im staging liegen",
    )
    parser.add_argument(
        "--force-path",
        action="store_true",
        help="(Linux/macOS) Sicherheitspruefung des Zielpfads deaktivieren",
    )
    args = parser.parse_args()

    if not SDCARD_STAGED.exists():
        log(
            f"Staging fehlt: {SDCARD_STAGED}. "
            "Zuerst `uv run tools/setup.py` ausfuehren."
        )
        return 1

    target = args.target
    if not target.exists():
        log(f"Ziel existiert nicht: {target}")
        return 1

    if args.force_path and sys.platform.startswith("win"):
        log("--force-path wird unter Windows ignoriert (DRIVE_REMOVABLE bleibt Pflicht).")

    if not args.force_path or sys.platform.startswith("win"):
        assert_safe_target(target)

    neu, aend, gleich = plan_copy(SDCARD_STAGED, target)
    extra = plan_delete(SDCARD_STAGED, target) if args.mirror else []

    log(f"Plan fuer {target}:")
    log(f"  neu:        {len(neu)} Datei(en)")
    log(f"  geaendert:  {len(aend)} Datei(en)")
    log(f"  gleich:     {len(gleich)} Datei(en)")
    if args.mirror:
        log(f"  loeschen:   {len(extra)} Datei(en) (--mirror)")

    if neu or aend:
        print("  Beispiele:")
        for rel in (neu + aend)[:20]:
            print(f"    {'+' if rel in neu else '*'} {rel}")
    if extra:
        print("  Zu loeschen (--mirror):")
        for rel in extra[:20]:
            print(f"    - {rel}")

    if not args.confirm:
        print()
        log("Dry-Run (kein --confirm). Zum Durchfuehren mit --confirm wiederholen.")
        return 0

    log("Fuehre Kopie durch ...")
    apply_copy(SDCARD_STAGED, target, neu + aend)
    if args.mirror and extra:
        log(f"Loesche {len(extra)} Datei(en) im Ziel ...")
        apply_delete(target, extra)

    log("Fertig.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
