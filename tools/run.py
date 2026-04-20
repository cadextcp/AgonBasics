#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Startet den Agon-Emulator (GUI oder headless) mit der gestagten SD-Karte.

Beispiele:
    uv run tools/run.py
        GUI-Emulator oeffnen, direkt am BBC-BASIC-Prompt.

    uv run tools/run.py --program hello.bas
        GUI-Emulator oeffnen, hello.bas laedt und startet automatisch
        (autoexec: SET KEYBOARD 2 / cd beispiele / /bin/bbcbasic hello.bas).

    uv run tools/run.py --headless --program hello.bas
        CLI-Emulator, gleiche autoexec-Logik. Programm laeuft und beendet
        sich idealerweise per PROC_dbg_exit; sonst greift --timeout.

    uv run tools/run.py --firmware quark -u
        GUI-Emulator mit Quark MOS 1.04, ohne CPU-Limit.

    uv run tools/run.py --keyboard 0
        Keyboard-Layout ueberschreiben (0=UK, 1=US, 2=German default).
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SDCARD_STAGED = ROOT / "sdcard" / "staged"
EMU_ROOT = ROOT / "emulator" / "fab-agon-emulator-v1.1.3-windows-x64"
EMU_ROOT_LINUX = ROOT / "emulator" / "fab-agon-emulator-v1.1.3-linux-x86_64"

# Default-Keyboard-Layout fuer autoexec.txt. Uebersicht aus der offiziellen
# Doku (https://agonplatform.github.io/agon-docs/mos/Star-Commands/#keyboard-layout):
#   0 UK, 1 US, 2 German, 3 Italian, 4 Spanish, 5 French, 6 Belgian,
#   7 Norwegian, 8 Japanese, 9 US International, ..., 17 Dvorak.
# Ueberschreibbar per --keyboard N.
DEFAULT_KEYBOARD = 2


def log(msg: str) -> None:
    print(f"[run] {msg}", flush=True)


def find_emulator_dir() -> Path:
    """Findet den entpackten Emulator-Ordner unabhaengig vom OS."""
    for candidate in (EMU_ROOT, EMU_ROOT_LINUX):
        if candidate.exists():
            return candidate
    # Fallback: alles unter emulator/ durchsuchen
    base = ROOT / "emulator"
    if base.exists():
        for child in base.iterdir():
            if child.is_dir() and child.name.startswith("fab-agon-emulator"):
                return child
    raise FileNotFoundError(
        "Emulator nicht gefunden. Zuerst `uv run tools/setup.py` ausfuehren."
    )


def exe_name(base: str) -> str:
    if sys.platform.startswith("win"):
        return f"{base}.exe"
    return base


def write_autoexec(sdcard: Path, lines: list[str]) -> None:
    """Schreibt autoexec.txt mit LF-Zeilenenden (Pflicht!)."""
    content = "".join(line + "\n" for line in lines)
    autoexec = sdcard / "autoexec.txt"
    # auf LF normieren
    autoexec.write_bytes(content.encode("utf-8"))
    log(f"autoexec.txt gesetzt: {len(lines)} Zeile(n)")


def restore_default_autoexec(sdcard: Path, keyboard: int = DEFAULT_KEYBOARD) -> None:
    """Stellt ein neutrales autoexec wieder her (BBC BASIC am MOS-Prompt)."""
    # Einfaches Default: nur Keyboard setzen
    write_autoexec(sdcard, [f"SET KEYBOARD {keyboard}"])


def build_gui_autoexec(
    program: str | None, keyboard: int = DEFAULT_KEYBOARD
) -> list[str]:
    """Autoexec-Zeilen fuer eine BASIC-Session.

    Ohne --program: nur Keyboard + bbcbasic -> MOS-Prompt -> BBC-BASIC-Prompt.
    Mit --program: wechselt ins beispiele/ und uebergibt den Dateinamen an
    bbcbasic. BBC BASIC fuer Agon interpretiert das erste Argument als
    LOAD+RUN-Datei, daher startet das Programm automatisch.

    Der `cd beispiele`-Schritt sorgt dafuer, dass das Programm seine Assets
    per relativem Pfad laden kann (z. B. sprite.bas: OPENIN "ship.rgba").

    Der fuehrende Slash bei `/bin/bbcbasic` ist ein absoluter Pfad vom
    SD-Karten-Root; er funktioniert auch nach `cd beispiele`. MOS 2.x
    unterstuetzt `..` im Pfad nicht.
    """
    lines = [f"SET KEYBOARD {keyboard}"]
    if program:
        lines.append("cd beispiele")
        lines.append(f"/bin/bbcbasic {program}")
    else:
        lines.append("/bin/bbcbasic")
    return lines


def run_gui(args: argparse.Namespace) -> int:
    emu_dir = find_emulator_dir()
    exe = emu_dir / exe_name("fab-agon-emulator")
    if not exe.exists():
        log(f"GUI-Emulator nicht gefunden: {exe}")
        return 1

    write_autoexec(SDCARD_STAGED, build_gui_autoexec(args.program, args.keyboard))

    cmd = [str(exe), "--sdcard", str(SDCARD_STAGED.resolve())]
    if args.firmware:
        cmd += ["--firmware", args.firmware]
    if args.unlimited_cpu:
        cmd.append("-u")
    if args.fullscreen:
        cmd.append("-f")
    if args.mode is not None:
        cmd += ["--mode", str(args.mode)]
    if args.extra_args:
        cmd += args.extra_args

    log(f"Starte: {' '.join(repr(c) for c in cmd)}")
    if args.program:
        print()
        print("  +------------------------------------------------------------+")
        print("  | Im BBC-BASIC-Prompt (>) bitte eingeben:                    |")
        print(f'  |   *CD beispiele'.ljust(63) + "|")
        print(f'  |   CHAIN "{args.program}"'.ljust(63) + "|")
        print("  +------------------------------------------------------------+")
        print()
    return subprocess.call(cmd, cwd=emu_dir)


def run_headless(args: argparse.Namespace) -> int:
    emu_dir = find_emulator_dir()
    exe = emu_dir / exe_name("agon-cli-emulator")
    if not exe.exists():
        log(f"CLI-Emulator nicht gefunden: {exe}")
        return 1

    # Headless = dieselbe autoexec-Logik wie GUI; das Programm laedt und
    # startet sich selbst. Ohne --program landen wir am BBC-BASIC-Prompt.
    # Programme sollten sich selbst via PROC_dbg_exit(rc) beenden, sonst
    # greift der --timeout.
    lines = build_gui_autoexec(args.program, args.keyboard)
    write_autoexec(SDCARD_STAGED, lines)

    cmd = [str(exe), "--sdcard", str(SDCARD_STAGED.resolve())]
    if args.unlimited_cpu:
        cmd.append("-u")

    # ein paar leere Zeilen in stdin als Timing-Puffer - falls das Programm
    # INPUT/GET erwartet, verschluckt es diese Leereingaben statt zu hangen.
    stdin_text = "\n" * 8

    log(f"Starte headless: {' '.join(repr(c) for c in cmd)}")
    log(f"autoexec ({len(lines)} Zeilen):")
    for ln in lines:
        log(f"  | {ln}")

    try:
        proc = subprocess.Popen(
            cmd,
            cwd=emu_dir,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
    except FileNotFoundError as e:
        log(f"Kann CLI-Emulator nicht starten: {e}")
        return 1

    try:
        stdout, _ = proc.communicate(
            input=stdin_text, timeout=args.timeout
        )
    except subprocess.TimeoutExpired:
        log(f"Timeout nach {args.timeout}s - prozess wird beendet")
        proc.kill()
        stdout, _ = proc.communicate()
        print(stdout)
        return 124
    print(stdout, end="")
    return proc.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="AgonBasics run")
    parser.add_argument(
        "--program",
        "-p",
        help="BASIC-Programm aus beispiele/ autostarten (z.B. hello.bas)",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="CLI-Emulator (keine Grafik, text-only)",
    )
    parser.add_argument(
        "--firmware",
        choices=["console8", "quark", "electron", "fb"],
        help="MOS/VDP-Variante (default: console8)",
    )
    parser.add_argument(
        "-u",
        "--unlimited-cpu",
        action="store_true",
        help="eZ80-CPU ohne 18.432 MHz Limit laufen lassen",
    )
    parser.add_argument(
        "-f",
        "--fullscreen",
        action="store_true",
        help="GUI im Vollbild starten",
    )
    parser.add_argument(
        "--mode",
        type=int,
        help="Bildschirmmodus beim Start setzen",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=20.0,
        help="Headless-Timeout in Sekunden (default: 20)",
    )
    parser.add_argument(
        "--keyboard",
        type=int,
        default=DEFAULT_KEYBOARD,
        metavar="N",
        help=(
            f"Keyboard-Layout fuer SET KEYBOARD (default: {DEFAULT_KEYBOARD} = German; "
            "0=UK, 1=US, 2=German, 3=Italian, 5=French, 11=Swiss German, ...)"
        ),
    )
    parser.add_argument(
        "extra_args",
        nargs="*",
        help="Zusaetzliche Flags werden an den Emulator durchgereicht",
    )
    args = parser.parse_args()

    if not SDCARD_STAGED.exists():
        log(
            f"SD-Karte fehlt: {SDCARD_STAGED}\n"
            "  Zuerst `uv run tools/setup.py` ausfuehren."
        )
        return 1

    return run_headless(args) if args.headless else run_gui(args)


if __name__ == "__main__":
    raise SystemExit(main())
