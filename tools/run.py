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
        GUI-Emulator oeffnen, hello.bas laedt und startet automatisch.

    uv run tools/run.py --program summe_bug.bas --hold
        GUI-Emulator. Programm startet, wenn PROC_dbg_exit aufgerufen wird
        schliesst sich das Emulator-Fenster NICHT. Man landet im
        BBC-BASIC-Prompt und kann Variablen inspizieren.

    uv run tools/run.py --headless --program hello.bas
        CLI-Emulator. Programm sollte sich per PROC_dbg_exit beenden;
        sonst greift --timeout.

    uv run tools/run.py --firmware quark -u
        GUI mit Quark MOS 1.04, ohne CPU-Limit.

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

# Default-Firmware fuer den GUI-Emulator. Der GUI-Emulator waehlt von sich
# aus 'platform' (MOS 3.x), der CLI-Emulator immer Console8 MOS 2.3.3. Damit
# GUI und CLI das gleiche Verhalten zeigen (und unsere autoexec.txt passt),
# erzwingen wir console8 im GUI-Pfad. Der CLI ignoriert --firmware eh.
DEFAULT_FIRMWARE = "console8"


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


def resolve_program(program: str | None) -> Path | None:
    """Prueft, ob `program` in beispiele/ oder lib/ existiert.

    Gibt den Pfad der Quelle zurueck (fuer Info-Logs) bzw. None, wenn kein
    Programm angegeben wurde. Wirft FileNotFoundError mit hilfreicher Liste,
    wenn angegeben aber nicht vorhanden.
    """
    if not program:
        return None

    candidates = [
        ROOT / "beispiele" / program,
        ROOT / "lib" / program,
    ]
    for c in candidates:
        if c.exists():
            return c

    available = sorted(
        [p.name for p in (ROOT / "beispiele").glob("*.bas")]
        + [p.name for p in (ROOT / "lib").glob("*.bas")]
    )
    hint = "\n  ".join(available) if available else "(keine)"
    raise FileNotFoundError(
        f"Programm '{program}' nicht gefunden.\n"
        f"  Gesucht in: beispiele/{program}, lib/{program}\n"
        f"  Verfuegbar:\n  {hint}\n"
        f"  Tipp: Dateiname muss inklusive .bas-Endung angegeben werden,\n"
        f"  z. B. `--program hello.bas`."
    )


def apply_hold_to_staged(program: str) -> None:
    """Schaltet den Hold-Mode im gestagten Programm ein.

    Sucht die HOLD-MARKER-Zeile in der (via `REM USES lib/debug` automatisch
    mitgestagten) Library-Inline-Sektion und ersetzt `dbg_hold% = 0` durch
    `dbg_hold% = TRUE`. Dann bleibt der Emulator nach PROC_dbg_exit offen
    (der BASIC-Prompt erscheint, Variablen koennen inspiziert werden).

    Naechstes `uv run tools/deploy.py` setzt den Normalzustand wieder.
    """
    staged = SDCARD_STAGED / "beispiele" / program
    if not staged.exists():
        log(
            f"--hold: gestagte Datei fehlt ({staged}); "
            "fuehre zuerst `uv run tools/deploy.py` aus."
        )
        return
    text = staged.read_bytes().decode("utf-8", errors="replace")
    marker = "31012 dbg_hold% = 0"
    if marker not in text:
        log(
            "--hold: HOLD-MARKER nicht gefunden. Enthaelt das Programm "
            "`REM USES lib/debug`? Nur mit inline-lib greift der Hold-Mode."
        )
        return
    patched = text.replace(marker, "31012 dbg_hold% = TRUE", 1)
    staged.write_bytes(patched.encode("utf-8"))
    log(f"--hold: Hold-Mode in {staged.name} aktiviert")


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

    try:
        src = resolve_program(args.program)
    except FileNotFoundError as e:
        log(str(e))
        return 2
    if src is not None:
        log(f"Programm-Quelle: {src.relative_to(ROOT)}")

    write_autoexec(SDCARD_STAGED, build_gui_autoexec(args.program, args.keyboard))

    if args.hold and args.program:
        apply_hold_to_staged(args.program)

    cmd = [str(exe), "--sdcard", str(SDCARD_STAGED.resolve())]
    # GUI-Default des Emulators ist 'platform' (MOS 3.x), wir setzen aber
    # immer explizit die vom CLI und unseren Tests bekannte 2.x-Variante.
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
        print(f"  | {args.program} startet automatisch im Emulator.".ljust(63) + "|")
        if args.hold:
            print("  | --hold aktiv: Fenster bleibt nach PROC_dbg_exit offen.      |")
        else:
            print("  | Nach Ende zurueck am BBC-BASIC-Prompt (>).                  |")
        print("  +------------------------------------------------------------+")
        print()
    return subprocess.call(cmd, cwd=emu_dir)


def run_headless(args: argparse.Namespace) -> int:
    emu_dir = find_emulator_dir()
    exe = emu_dir / exe_name("agon-cli-emulator")
    if not exe.exists():
        log(f"CLI-Emulator nicht gefunden: {exe}")
        return 1

    try:
        src = resolve_program(args.program)
    except FileNotFoundError as e:
        log(str(e))
        return 2
    if src is not None:
        log(f"Programm-Quelle: {src.relative_to(ROOT)}")

    # Headless = dieselbe autoexec-Logik wie GUI; das Programm laedt und
    # startet sich selbst. Ohne --program landen wir am BBC-BASIC-Prompt.
    # Programme sollten sich selbst via PROC_dbg_exit(rc) beenden, sonst
    # greift der --timeout.
    lines = build_gui_autoexec(args.program, args.keyboard)
    write_autoexec(SDCARD_STAGED, lines)

    if args.hold and args.program:
        apply_hold_to_staged(args.program)

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
            encoding="utf-8",
            errors="replace",
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
    # stdout so konfigurieren, dass unbekannte Bytes (z.B. VDU-packet-Noise
    # vom Emulator) nicht crashen - sonst bricht print() unter Windows mit
    # UnicodeEncodeError ab, sobald der CLI-Emulator non-cp1252-Bytes ausgibt.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")

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
        "--hold",
        action="store_true",
        help=(
            "Emulator bleibt nach PROC_dbg_exit geoeffnet (setzt "
            "dbg_hold% = TRUE im gestagten Programm). Nuetzlich fuer "
            "interaktives Debuggen, wenn man nach einem ASSERT FAIL noch "
            "Variablen inspizieren will. `uv run tools/deploy.py` setzt "
            "den Normalzustand wieder."
        ),
    )
    parser.add_argument(
        "--firmware",
        choices=["console8", "quark", "electron", "fb"],
        default=DEFAULT_FIRMWARE,
        help=(
            f"MOS/VDP-Variante fuer GUI-Mode (default: {DEFAULT_FIRMWARE} = MOS 2.3.3). "
            "GUI-Default des Emulators waere 'platform' (MOS 3.x), aber 2.3.3 "
            "ist konsistent zum CLI-Emulator und gegen autoexec.txt getestet."
        ),
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
