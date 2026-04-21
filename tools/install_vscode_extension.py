#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Installiert die im Repo liegende BBC-BASIC-Extension in VS Code.

Kopiert tools/vscode-bbcbasic/ nach ~/.vscode/extensions/bbcbasic-agon-<ver>/
(bzw. %USERPROFILE%\\.vscode\\extensions\\... unter Windows). Nach einem
Reload des VS-Code-Fensters ist .bas-Highlighting inkl. REM-Kommentaren
aktiv.

Optionen:
    --target-dir PATH  Anderen Extension-Ordner als ~/.vscode/extensions
                       benutzen (z. B. ~/.vscode-insiders/extensions).
    --uninstall        Die installierte Variante wieder entfernen.

Deinstallation alternativ:
    rm -rf ~/.vscode/extensions/bbcbasic-agon-*
    (oder via VS Code: Extensions-Panel -> "BBC BASIC (Agon)" -> Uninstall)
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from shutil import copytree, rmtree

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "tools" / "vscode-bbcbasic"


def log(msg: str) -> None:
    print(f"[install_vscode_extension] {msg}", flush=True)


def read_version() -> str:
    """Liest die Versionsnummer aus der package.json der Extension."""
    pkg = json.loads((SRC / "package.json").read_text(encoding="utf-8"))
    return pkg.get("version", "0.0.0")


def default_extensions_dir() -> Path:
    """Standard-Speicherort fuer VS-Code-User-Extensions.

    Linux/macOS: ~/.vscode/extensions
    Windows:     %USERPROFILE%\\.vscode\\extensions
    """
    return Path.home() / ".vscode" / "extensions"


def install(target_dir: Path) -> int:
    if not SRC.exists():
        log(f"Quelle fehlt: {SRC}")
        return 1

    version = read_version()
    dst = target_dir / f"bbcbasic-agon-{version}"

    # Alte Installationen (auch andere Versionen) entfernen, sonst liegen
    # z. B. bbcbasic-agon-0.0.1 und bbcbasic-agon-0.1.0 parallel und VS Code
    # laedt nicht-deterministisch die "falsche".
    for old in sorted(target_dir.glob("bbcbasic-agon-*")):
        log(f"Entferne alte Installation: {old}")
        rmtree(old)

    dst.parent.mkdir(parents=True, exist_ok=True)
    copytree(SRC, dst)

    log(f"Installiert: {dst}")
    print()
    print("Naechste Schritte:")
    print("  1) VS Code neu laden: Ctrl+Shift+P -> Developer: Reload Window")
    print("  2) Ein beliebiges .bas-File oeffnen. Rechts unten in der")
    print("     Statusleiste sollte 'BBC BASIC' stehen (statt 'Visual Basic').")
    print()
    print("Farbe der REM-Kommentare weiter tunen? Siehe")
    print(f"  {SRC / 'README.md'}  -> Abschnitt 'Farbe anpassen'.")
    return 0


def uninstall(target_dir: Path) -> int:
    matches = sorted(target_dir.glob("bbcbasic-agon-*"))
    if not matches:
        log(f"Keine Installation gefunden unter {target_dir}")
        return 0
    for m in matches:
        log(f"Entferne {m}")
        rmtree(m)
    log("Fertig. VS Code einmal neu laden.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="AgonBasics: BBC-BASIC-Extension in VS Code installieren"
    )
    parser.add_argument(
        "--target-dir",
        type=Path,
        default=default_extensions_dir(),
        help="Anderes Extensions-Verzeichnis (default: %(default)s).",
    )
    parser.add_argument(
        "--uninstall",
        action="store_true",
        help="Installierte Extension entfernen statt installieren.",
    )
    args = parser.parse_args()

    if args.uninstall:
        return uninstall(args.target_dir)
    return install(args.target_dir)


if __name__ == "__main__":
    raise SystemExit(main())
