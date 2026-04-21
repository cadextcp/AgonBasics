#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Headless-Testrunner fuer BBC-BASIC-Programme.

Findet alle tests/test_*.bas, kopiert sie in sdcard/staged/beispiele/
(mit automatischem Inlining von lib/debug.bas, falls das Testskript
den Marker `REM USES lib/debug` enthaelt), startet sie einzeln im
CLI-Emulator und wertet das Ergebnis aus.

Konvention fuer Tests:
    Am Ende jedes Tests muss eine Erfolgs- oder Fehlermarkierung gedruckt werden
    (per PRINT), damit der Runner erkennt, ob der Test bestanden hat:

        PRINT "=== TEST PASS ==="
        PROC_dbg_exit(0)

        PRINT "=== TEST FAIL ==="
        PROC_dbg_exit(1)

    PROC_dbg_exit stammt aus lib/debug.bas und fuehrt OUT (&00), A aus,
    was den Emulator mit dem uebergebenen Exit-Code beendet.

Optional (expected-output-Vergleich):
    Wenn tests/expected/test_X.txt existiert, wird der Text zwischen
        === OUTPUT BEGIN ===
    und
        === OUTPUT END ===
    aus dem emitterten stdout extrahiert und per Zeilenvergleich gegen
    die Erwartungsdatei geprueft.

Flags:
    --update        erzeugt fehlende tests/expected/*.txt aus der aktuellen
                    Ausgabe (NICHT in CI benutzen, nur lokal zum Anlegen)
    --filter PAT    nur Tests, deren Dateiname PAT enthaelt, ausfuehren
    --timeout SEC   pro Test max. SEC Sekunden (default 25)
"""

from __future__ import annotations

import argparse
import importlib.util
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TESTS_DIR = ROOT / "tests"
EXPECTED_DIR = TESTS_DIR / "expected"
SDCARD_STAGED = ROOT / "sdcard" / "staged"
BEISPIELE_STAGED = SDCARD_STAGED / "beispiele"

PASS_MARKER = "=== TEST PASS ==="
FAIL_MARKER = "=== TEST FAIL ==="
BEGIN_MARKER = "=== OUTPUT BEGIN ==="
END_MARKER = "=== OUTPUT END ==="

ANSI_RE = re.compile(r"\x1b\[[0-9;?]*[ -/]*[@-~]")


def log(msg: str) -> None:
    print(f"[test] {msg}", flush=True)


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_run_helpers():
    return _load_module(ROOT / "tools" / "run.py", "_run")


def load_deploy_helpers():
    return _load_module(ROOT / "tools" / "deploy.py", "_deploy")


def sanitize(text: str) -> str:
    text = ANSI_RE.sub("", text)
    return text.replace("\r\n", "\n").replace("\r", "\n")


def extract_output(stdout: str) -> str | None:
    text = sanitize(stdout)
    begin_idx = text.find(BEGIN_MARKER)
    end_idx = text.find(END_MARKER)
    if begin_idx < 0 or end_idx < 0 or end_idx <= begin_idx:
        return None
    block = text[begin_idx + len(BEGIN_MARKER) : end_idx]
    return block.strip("\n")


def stage_test(deploy_mod, test_bas: Path) -> None:
    """Kopiert die Test-Datei mit lib-Inlining und CRLF nach staged/beispiele/."""
    BEISPIELE_STAGED.mkdir(parents=True, exist_ok=True)
    dst = BEISPIELE_STAGED / test_bas.name
    content = deploy_mod.file_content(test_bas)
    dst.write_bytes(content)


def run_single(run_mod, exe: Path, emu_dir: Path, test_name: str, timeout: float) -> str:
    # autoexec.txt treibt den ganzen Run: cd beispiele + /bin/bbcbasic <file>
    # BBC BASIC fuer Agon lädt und startet die Datei automatisch. Der Test
    # muss sich selbst per PROC_dbg_exit(rc) beenden.
    lines = run_mod.build_gui_autoexec(test_name)
    run_mod.write_autoexec(SDCARD_STAGED, lines)

    cmd = [
        str(exe),
        "--sdcard",
        str(SDCARD_STAGED.resolve()),
    ]
    # Minimaler stdin-Puffer fuer Programme, die INPUT/GET aufrufen.
    stdin_text = "\n" * 8

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
    try:
        stdout, _ = proc.communicate(input=stdin_text, timeout=timeout)
    except subprocess.TimeoutExpired:
        proc.kill()
        stdout, _ = proc.communicate()
        stdout += f"\n[test] TIMEOUT nach {timeout}s\n"
    return stdout


def evaluate(stdout: str, test_bas: Path, update: bool) -> tuple[bool, str]:
    text = sanitize(stdout)
    reasons = []

    if FAIL_MARKER in text:
        reasons.append(f"{FAIL_MARKER} gesehen")
        return False, "; ".join(reasons)

    if PASS_MARKER not in text:
        reasons.append(f"{PASS_MARKER} fehlt")
        return False, "; ".join(reasons)

    expected_file = EXPECTED_DIR / f"{test_bas.stem}.txt"
    block = extract_output(stdout)
    if expected_file.exists():
        if block is None:
            reasons.append("OUTPUT BEGIN/END Marker fehlen")
            return False, "; ".join(reasons)
        expected = expected_file.read_text(encoding="utf-8").rstrip("\n")
        if block.rstrip("\n") != expected:
            diff = _short_diff(expected, block)
            reasons.append(f"expected output mismatch:\n{diff}")
            return False, "; ".join(reasons)
    else:
        if update and block is not None:
            EXPECTED_DIR.mkdir(parents=True, exist_ok=True)
            expected_file.write_text(block + "\n", encoding="utf-8")
            log(f"  -> expected/{expected_file.name} angelegt")

    return True, "ok"


def _short_diff(expected: str, actual: str) -> str:
    import difflib

    exp_lines = expected.splitlines()
    act_lines = actual.splitlines()
    return "\n".join(
        difflib.unified_diff(
            exp_lines, act_lines, fromfile="expected", tofile="actual", lineterm=""
        )
    )


def main() -> int:
    # stdout robust machen gegen VDU-Noise (siehe run.py)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")

    parser = argparse.ArgumentParser(description="AgonBasics test runner")
    parser.add_argument("--filter", default=None)
    parser.add_argument("--timeout", type=float, default=25.0)
    parser.add_argument("--update", action="store_true")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    if not SDCARD_STAGED.exists():
        log(
            f"SD-Karte fehlt: {SDCARD_STAGED}. "
            "Zuerst `uv run tools/setup.py` ausfuehren."
        )
        return 1

    run_mod = load_run_helpers()
    deploy_mod = load_deploy_helpers()

    try:
        emu_dir = run_mod.find_emulator_dir()
    except FileNotFoundError as e:
        log(f"Emulator nicht gefunden: {e}")
        return 1
    exe = emu_dir / run_mod.exe_name("agon-cli-emulator")
    if not exe.exists():
        log(f"CLI-Emulator nicht gefunden: {exe}")
        return 1

    tests = sorted(TESTS_DIR.glob("test_*.bas"))
    if args.filter:
        tests = [t for t in tests if args.filter in t.name]
    if not tests:
        log("Keine Tests gefunden.")
        return 0

    log(f"Starte {len(tests)} Test(s)")
    passed = 0
    failed = 0
    start = time.time()

    for t in tests:
        log(f"* {t.name}")
        stage_test(deploy_mod, t)
        try:
            out = run_single(run_mod, exe, emu_dir, t.name, args.timeout)
        except Exception as e:  # pragma: no cover
            log(f"  FEHLER: {e}")
            failed += 1
            continue
        ok, reason = evaluate(out, t, args.update)
        if args.verbose or not ok:
            print("--- stdout ---")
            print(out.rstrip())
            print("--- end ---")
        if ok:
            log(f"  PASS")
            passed += 1
        else:
            log(f"  FAIL: {reason}")
            failed += 1

    elapsed = time.time() - start
    log(f"Ergebnis: {passed} pass, {failed} fail, {elapsed:.1f}s")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
