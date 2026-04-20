#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Startet den GUI-Emulator mit aktiviertem eZ80-Debugger.

Der Debugger laeuft im Terminal, aus dem dieses Skript gestartet wurde.
Befehle im Debugger: `help`, `step`, `continue`, `registers`, `memory <addr> <len>`,
`break <addr>`, `trace`.

Breakpoints koennen mit `-b <adresse>` gesetzt werden (mehrfach moeglich).
Innerhalb eines BASIC-Programms triggert `PROC_dbg_bp(id)` aus lib/debug.bas
einen Emulator-Breakpoint (per `OUT (&10), A`).

Beispiele:
    uv run tools/debug.py
        GUI + Debugger, MOS-Prompt

    uv run tools/debug.py --program debug_demo.bas
        GUI + Debugger, laedt beispiele/debug_demo.bas

    uv run tools/debug.py -b 0x40000 -b 0x40100
        Startet mit zwei Adress-Breakpoints
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SDCARD_STAGED = ROOT / "sdcard" / "staged"


def log(msg: str) -> None:
    print(f"[debug] {msg}", flush=True)


def find_emulator_exe() -> Path:
    from importlib.util import spec_from_file_location, module_from_spec

    spec = spec_from_file_location("_run", ROOT / "tools" / "run.py")
    mod = module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    emu_dir = mod.find_emulator_dir()
    exe = emu_dir / mod.exe_name("fab-agon-emulator")
    if not exe.exists():
        raise FileNotFoundError(exe)
    return exe


def write_autoexec_for_program(program: str | None, keyboard: int) -> None:
    # Dieselbe 3-Zeilen-Logik wie run.py: mit --program wird das Programm
    # automatisch geladen und gestartet; ohne --program landet man am
    # BBC-BASIC-Prompt.
    lines = [f"SET KEYBOARD {keyboard}"]
    if program:
        lines.append("cd beispiele")
        lines.append(f"/bin/bbcbasic {program}")
    else:
        lines.append("/bin/bbcbasic")
    autoexec = SDCARD_STAGED / "autoexec.txt"
    autoexec.write_bytes(("\n".join(lines) + "\n").encode("utf-8"))
    log(f"autoexec.txt fuer Debug-Run geschrieben ({len(lines)} Zeilen)")


def main() -> int:
    # DEFAULT_KEYBOARD aus run.py wiederverwenden
    from importlib.util import spec_from_file_location, module_from_spec

    spec = spec_from_file_location("_run", ROOT / "tools" / "run.py")
    run_mod = module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(run_mod)  # type: ignore[union-attr]
    default_keyboard = run_mod.DEFAULT_KEYBOARD

    parser = argparse.ArgumentParser(description="AgonBasics debug")
    parser.add_argument(
        "--program",
        "-p",
        help="BASIC-Programm aus beispiele/ (zum manuellen CHAINen im BASIC-Prompt)",
    )
    parser.add_argument(
        "-b",
        "--breakpoint",
        action="append",
        default=[],
        metavar="ADDR",
        help="Adress-Breakpoint (hex, z.B. 0x40000), mehrfach erlaubt",
    )
    parser.add_argument(
        "--firmware",
        choices=["console8", "quark", "electron", "fb"],
    )
    parser.add_argument(
        "-u", "--unlimited-cpu", action="store_true"
    )
    parser.add_argument(
        "--keyboard",
        type=int,
        default=default_keyboard,
        metavar="N",
        help=(
            f"Keyboard-Layout fuer SET KEYBOARD (default: {default_keyboard} = German; "
            "0=UK, 1=US, 2=German, 5=French, 11=Swiss German, ...)"
        ),
    )
    parser.add_argument(
        "extra_args", nargs="*",
        help="Weitere Argumente werden durchgereicht",
    )
    args = parser.parse_args()

    if not SDCARD_STAGED.exists():
        log(
            f"SD-Karte fehlt: {SDCARD_STAGED}. "
            "Zuerst `uv run tools/setup.py` ausfuehren."
        )
        return 1

    try:
        exe = find_emulator_exe()
    except FileNotFoundError as e:
        log(f"GUI-Emulator nicht gefunden: {e}")
        return 1

    # Pre-Flight: existiert das Programm in beispiele/ oder lib/?
    try:
        src = run_mod.resolve_program(args.program)
    except FileNotFoundError as e:
        log(str(e))
        return 2
    if src is not None:
        log(f"Programm-Quelle: {src.relative_to(run_mod.ROOT)}")

    write_autoexec_for_program(args.program, args.keyboard)

    cmd = [
        str(exe),
        "--sdcard",
        str(SDCARD_STAGED.resolve()),
        "-d",
    ]
    for bp in args.breakpoint:
        cmd += ["-b", bp]
    if args.firmware:
        cmd += ["--firmware", args.firmware]
    if args.unlimited_cpu:
        cmd.append("-u")
    if args.extra_args:
        cmd += args.extra_args

    log(f"Starte: {' '.join(repr(c) for c in cmd)}")
    print()
    print("  +------------------------------------------------------------+")
    print("  | eZ80-Debugger aktiv. Tippe 'help' im Debug-Prompt fuer      |")
    print("  | Befehlsuebersicht. Emulator-Breakpoints aus BASIC via       |")
    print("  | PROC_dbg_bp(id%) in lib/debug.bas.                          |")
    if args.program:
        print(f"  | {args.program} startet automatisch im Emulator.".ljust(63) + "|")
    print("  +------------------------------------------------------------+")
    print()

    return subprocess.call(cmd, cwd=exe.parent)


if __name__ == "__main__":
    raise SystemExit(main())
