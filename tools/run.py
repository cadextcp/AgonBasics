#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Startet den Agon-Emulator (GUI oder headless) mit der gestagten SD-Karte.

Beispiele:
    uv run tools/run.py
        GUI-Emulator oeffnen, MOS-Prompt.

    uv run tools/run.py --program hello.bas
        GUI-Emulator oeffnen, im beispiele/-Ordner, BBC-BASIC-Prompt.
        Im BASIC-Prompt: `CHAIN "hello.bas"` tippen, um das Programm zu starten.

    uv run tools/run.py --headless --program hello.bas
        CLI-Emulator, pipet `cd beispiele`, `bin/bbcbasic`, `CHAIN "hello.bas"`
        in stdin. Bricht nach --timeout Sekunden ab, falls das Programm nicht
        selbst beendet (via PROC_dbg_exit aus lib/debug.bas).

    uv run tools/run.py --firmware quark -u
        GUI-Emulator mit Quark MOS 1.04, ohne CPU-Limit.
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


def restore_default_autoexec(sdcard: Path) -> None:
    """Stellt ein neutrales autoexec wieder her (BBC BASIC am MOS-Prompt)."""
    # Einfaches Default: nur MOS-Prompt
    write_autoexec(sdcard, ["SET KEYBOARD 1"])


def build_gui_autoexec(program: str | None) -> list[str]:
    """Autoexec fuer GUI-Mode."""
    lines = ["SET KEYBOARD 1"]
    if program:
        lines.append("cd beispiele")
        lines.append("bin/bbcbasic")
    return lines


def run_gui(args: argparse.Namespace) -> int:
    emu_dir = find_emulator_dir()
    exe = emu_dir / exe_name("fab-agon-emulator")
    if not exe.exists():
        log(f"GUI-Emulator nicht gefunden: {exe}")
        return 1

    write_autoexec(SDCARD_STAGED, build_gui_autoexec(args.program))

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

    # Headless: wir pipen stdin und erwarten, dass das Programm selbst via
    # PROC_dbg_exit beendet. Ein Default-autoexec darf nichts unerwartetes
    # tun.
    restore_default_autoexec(SDCARD_STAGED)

    cmd = [str(exe), "--sdcard", str(SDCARD_STAGED.resolve())]
    if args.unlimited_cpu:
        cmd.append("-u")

    stdin_lines: list[str] = []
    # Erste Zeile wird beim Boot verschluckt (dummy), darum ein "."
    stdin_lines.append(".")
    stdin_lines.append("bin/bbcbasic")
    if args.program:
        # Arbeitsverzeichnis auf beispiele/ setzen (via BBC-BASIC Star-Cmd),
        # damit das Programm seine Assets per relativem Pfad laden kann
        # (z. B. sprite.bas: OPENIN "ship.rgba").
        stdin_lines.append("*CD beispiele")
        stdin_lines.append(f'CHAIN "{args.program}"')
    # ein paar leere Zeilen als Timing-Puffer fuer bbcbasic-Start
    stdin_lines += [""] * 3
    stdin_text = "\n".join(stdin_lines) + "\n"

    log(f"Starte headless: {' '.join(repr(c) for c in cmd)}")
    log(f"stdin ({len(stdin_lines)} Zeilen):")
    for ln in stdin_lines:
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
