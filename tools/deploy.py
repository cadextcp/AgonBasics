#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Kopiert den BASIC-Quelltext des Projekts in die gestagte SD-Karte.

Quellen:
    beispiele/   -> sdcard/staged/beispiele/
    lib/         -> sdcard/staged/beispiele/
    schulung/    -> sdcard/staged/beispiele/ (Lerngruppen-Iterationen)
    tests/*.bas  -> sdcard/staged/beispiele/ (nur auf Wunsch)

Regeln:
    *.bas -> CRLF (von Agon-BBC-BASIC erwartet)
    binaere Dateien (*.rgba, *.bin, ...) -> 1:1 kopiert

Spezielle Konvention fuer Bibliotheksnutzung:
    Enthaelt eine .bas-Quelldatei irgendwo den Marker

        REM USES lib/debug

    so wird beim Kopieren der Inhalt von lib/debug.bas an das Dateiende
    angehaengt (vor etwaige hoehere Zeilennummern). So koennen Programme
    PROC_dbg_* nutzen, ohne die Library manuell einzukopieren.

Idempotent: unveraenderte Zieldateien werden uebersprungen.
"""

from __future__ import annotations

import argparse
import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SDCARD_STAGED = ROOT / "sdcard" / "staged"
STAGE_SUBDIR = "beispiele"  # alles landet in sdcard/staged/beispiele/

SOURCE_DIRS = [
    ROOT / "beispiele",
    ROOT / "lib",
    ROOT / "schulung",
]

LIB_DEBUG = ROOT / "lib" / "debug.bas"
TEXT_SUFFIXES = {".bas", ".txt", ".md", ".asm", ".inc"}

USES_MARKER_RE = re.compile(r"^\s*\d+\s*REM\s+USES\s+lib/debug\b", re.IGNORECASE | re.MULTILINE)


def log(msg: str) -> None:
    print(f"[deploy] {msg}", flush=True)


def normalize_crlf(text: str) -> str:
    """Alle Zeilenenden auf CRLF normalisieren."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return text.replace("\n", "\r\n")


def inline_lib_if_requested(src_text: str) -> str:
    """Wenn src_text den USES-Marker enthaelt, lib/debug.bas ans Ende haengen."""
    if not USES_MARKER_RE.search(src_text):
        return src_text
    if not LIB_DEBUG.exists():
        return src_text
    lib_text = LIB_DEBUG.read_text(encoding="utf-8")
    sep = "\n" if not src_text.endswith("\n") else ""
    # ein Leerzeilen-Trennkommentar hilft beim manuellen Debuggen
    return (
        src_text.rstrip()
        + "\n29990 REM === auto-inlined lib/debug.bas ===\n"
        + lib_text.rstrip()
        + "\n"
    )


def file_content(path: Path) -> bytes:
    data = path.read_bytes()
    if path.suffix.lower() in TEXT_SUFFIXES:
        text = data.decode("utf-8", errors="replace")
        if path.suffix.lower() == ".bas":
            text = inline_lib_if_requested(text)
        text = normalize_crlf(text)
        return text.encode("utf-8")
    return data


def content_hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def deploy_file(src: Path, dst: Path) -> bool:
    """Kopiert eine Datei, falls noetig. Gibt True zurueck, wenn geschrieben."""
    content = file_content(src)
    if dst.exists():
        existing = dst.read_bytes()
        if content_hash(existing) == content_hash(content):
            return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(content)
    return True


def deploy_tree(src_root: Path, dst_root: Path) -> tuple[int, int]:
    """Rekursives Deployment. Gibt (geschrieben, uebersprungen) zurueck."""
    written = 0
    skipped = 0
    for src in src_root.rglob("*"):
        if src.is_dir():
            continue
        rel = src.relative_to(src_root)
        dst = dst_root / rel
        if deploy_file(src, dst):
            written += 1
            log(f"  {rel}")
        else:
            skipped += 1
    return written, skipped


def main() -> int:
    parser = argparse.ArgumentParser(description="AgonBasics deploy")
    parser.add_argument(
        "--target",
        type=Path,
        default=None,
        help="Ziel-SD-Karten-Wurzel (default: sdcard/staged/)",
    )
    args = parser.parse_args()

    target_root = args.target or SDCARD_STAGED
    if not target_root.exists():
        log(
            f"Ziel existiert nicht: {target_root}\n"
            "  Zuerst `uv run tools/setup.py` ausfuehren."
        )
        return 1

    dst = target_root / STAGE_SUBDIR
    log(f"Deploy -> {dst}")

    total_written = 0
    total_skipped = 0
    for src in SOURCE_DIRS:
        if not src.exists():
            log(f"  (ueberspringe {src.name}/: nicht vorhanden)")
            continue
        written, skipped = deploy_tree(src, dst)
        total_written += written
        total_skipped += skipped

    log(
        f"Fertig: {total_written} Datei(en) geschrieben, "
        f"{total_skipped} uebersprungen."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
