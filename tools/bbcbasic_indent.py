#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
BBC BASIC Auto-Einruecker.

Rueckt Block-Strukturen mit 2 Spaces pro Schachtelungs-Ebene ein:

    FOR ... NEXT
    REPEAT ... UNTIL
    WHILE ... WEND / ENDWHILE
    DEF PROC ... ENDPROC
    DEF FN ... ENDFN

Bewusst konservativ: IF/THEN/ELSE werden NICHT als Blocks behandelt (BBC
BASIC Z80 hat kein strukturiertes IF-THEN-ENDIF; ein `IF cond THEN stmt`
ist einzeilig, ENDIF waere ohnehin ungueltig). Multi-Statement-Zeilen
mit ausgeglichenem FOR...NEXT oder REPEAT...UNTIL auf einer Zeile
aendern die Tiefe netto nicht.

Strings ("...") und `REM ...`-Kommentare werden vorher ausmaskiert, damit
darin vorkommende Keywords nicht falsch gezaehlt werden.

Idempotent: Skript zweimal laufen lassen aendert nichts mehr.

Aufruf:

    uv run tools/bbcbasic_indent.py werkzeuge/sprite_editor/sped.bas
    uv run tools/bbcbasic_indent.py --check beispiele/breakout.bas
    uv run tools/bbcbasic_indent.py --diff beispiele/breakout.bas
"""

from __future__ import annotations

import argparse
import difflib
import re
import sys
from pathlib import Path


LINE_NUM_RE = re.compile(r"^(\s*)(\d+)(\s*)(.*)$")

OPEN_PATTERNS = [
    re.compile(r"\bDEF\s+PROC", re.IGNORECASE),
    re.compile(r"\bFOR\b", re.IGNORECASE),
    re.compile(r"\bREPEAT\b", re.IGNORECASE),
    re.compile(r"\bWHILE\b", re.IGNORECASE),
    # Kein DEF FN: einzeilige FNs (`DEF FNfoo = <expr>`) haben kein
    # ENDFN, und Multi-Line-FNs werden mit `=<result>` beendet, nicht
    # mit ENDFN. Zu heterogen fuer einen einfachen Depth-Counter.
    # FN-Bodies bleiben deshalb un-indented - in der Praxis verschmerzbar.
]

CLOSE_PATTERNS = [
    re.compile(r"\bENDPROC\b", re.IGNORECASE),
    re.compile(r"\bNEXT\b", re.IGNORECASE),
    re.compile(r"\bUNTIL\b", re.IGNORECASE),
    re.compile(r"\bENDWHILE\b", re.IGNORECASE),
    re.compile(r"\bWEND\b", re.IGNORECASE),
]

# Wenn die erste Anweisung einer Zeile (nach Zeilennummer) ein
# Block-Closer ist, wird DIESE Zeile bereits auf dem kleineren
# Level eingerueckt (nicht erst die naechste).
FIRST_CLOSE_RE = re.compile(
    r"^\s*(ENDPROC|NEXT|UNTIL|ENDWHILE|WEND)\b",
    re.IGNORECASE,
)


def mask_strings_and_rem(code: str) -> str:
    """Ersetzt String-Literale, REM-Kommentare sowie die in einem IF
    verzweigten Statements durch Leerzeichen.

    Die Laenge bleibt erhalten; Inhalte werden nur zu Spaces. So zaehlen
    Keywords (FOR, NEXT, ENDPROC, ...) innerhalb

      - von Strings ("..."),
      - von REM-Kommentaren,
      - hinter einem IF (BBC-BASIC-Form `IF cond stmt` oder
        `IF cond THEN stmt`)

    NICHT als strukturelle Block-Opener/-Closer.

    Beispiele:
      `IF cond THEN ENDPROC`       -> ENDPROC ist conditional, kein Close
      `IF bcol%=c% ENDPROC`         -> dto., ohne THEN (ist valide in
                                       BBC BASIC Z80)
      `IF cond THEN NEXT : X%=1`    -> NEXT conditional, X%=1 laeuft
                                       unconditional, aber es enthaelt
                                       keine Block-Keywords -> egal

    Die Maskierung geht vom IF bis zum naechsten `:` (Statement-Ende
    auf der gleichen Zeile) oder bis Zeilenende, je nachdem was frueher
    kommt.
    """
    out = []
    in_string = False
    for ch in code:
        if ch == '"':
            in_string = not in_string
            out.append('"')
        elif in_string:
            out.append(" ")
        else:
            out.append(ch)
    masked = "".join(out)

    # REM bis Zeilenende ausblenden
    m = re.search(r"\bREM\b", masked, re.IGNORECASE)
    if m:
        masked = masked[: m.start()] + (" " * (len(masked) - m.start()))

    # IF-Anweisungen: das Statement nach IF ist konditional und zaehlt
    # nicht als struktureller Block-Ein-/Ausstieg. Unterscheidung nach
    # BBC-BASIC-Praxis:
    #   - `IF cond stmt` (ohne THEN): nur das stmt bis zum naechsten `:`
    #     ist conditional.
    #   - `IF cond THEN stmt1 : stmt2 : ...`: in der Praxis wird oft der
    #     GANZE Rest der Zeile als conditional empfunden, auch wenn BBC
    #     BASIC Z80 strict nur stmt1 conditional macht. Darum maskieren
    #     wir ab IF bis Zeilenende, sobald ein THEN im Statement steht.
    pos = 0
    while pos < len(masked):
        m = re.search(r"\bIF\b", masked[pos:], re.IGNORECASE)
        if not m:
            break
        start = pos + m.start()
        colon = masked.find(":", start)
        stmt_end = colon if colon != -1 else len(masked)

        has_then = bool(
            re.search(
                r"\bTHEN\b", masked[start:stmt_end], re.IGNORECASE
            )
        )
        if has_then:
            # Bis Zeilenende maskieren - folgende Statements der gleichen
            # Zeile gehoeren praktisch zum THEN-Branch.
            masked = masked[:start] + (" " * (len(masked) - start))
            break

        # IF ohne THEN: nur das eine Statement maskieren
        masked = masked[:start] + (" " * (stmt_end - start)) + masked[stmt_end:]
        pos = stmt_end + 1
    return masked


def count_matches(text: str, patterns: list[re.Pattern[str]]) -> int:
    return sum(len(p.findall(text)) for p in patterns)


def reindent_line(
    line: str, depth: int, indent_str: str = "  "
) -> tuple[str, int]:
    """Gibt (neue Zeile, neue Tiefe) zurueck. Line-Endings bleiben erhalten."""
    # Zeilenende abspalten, damit wir es hinterher wieder anhaengen koennen
    stripped = line.rstrip("\r\n")
    suffix = line[len(stripped):]

    m = LINE_NUM_RE.match(stripped)
    if not m:
        # Keine Zeilennummer gefunden (z. B. reine Leerzeile) - unveraendert
        return line, depth

    _lead, lnum, _sep, rest = m.groups()

    # Strings + REM ausblenden, dann Opener/Closer zaehlen
    code = mask_strings_and_rem(rest)
    opens = count_matches(code, OPEN_PATTERNS)
    closes = count_matches(code, CLOSE_PATTERNS)

    # Startet die Zeile mit einem Closer, wird sie selbst schon dedentet.
    line_level = depth
    if FIRST_CLOSE_RE.match(code):
        line_level = max(depth - 1, 0)

    indent = indent_str * line_level
    new_stripped = f"{lnum} {indent}{rest}" if rest else f"{lnum}"
    new_depth = depth + opens - closes
    return new_stripped + suffix, new_depth


def reindent_text(text: str) -> tuple[str, int]:
    """Reindent des ganzen Textes; gibt (neuer Text, finale Tiefe) zurueck."""
    lines = text.splitlines(keepends=True)
    out_lines: list[str] = []
    depth = 0
    for line in lines:
        new_line, depth = reindent_line(line, depth)
        out_lines.append(new_line)
    return "".join(out_lines), depth


def main() -> int:
    parser = argparse.ArgumentParser(
        description="BBC BASIC auto-indenter (FOR/REPEAT/WHILE/DEF-Blocks)."
    )
    parser.add_argument("file", type=Path, help=".bas-Datei")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Nur pruefen; Exit-Code 1 wenn Datei veraendert wuerde.",
    )
    parser.add_argument(
        "--diff",
        action="store_true",
        help="Unified diff auf stdout ausgeben (statt Datei zu schreiben).",
    )
    args = parser.parse_args()

    if not args.file.exists():
        print(f"Datei fehlt: {args.file}", file=sys.stderr)
        return 2

    raw = args.file.read_bytes()
    try:
        original = raw.decode("utf-8")
    except UnicodeDecodeError:
        original = raw.decode("cp1252")

    result, final_depth = reindent_text(original)

    if final_depth != 0:
        print(
            f"[warn] {args.file}: finale Block-Tiefe ist {final_depth}, "
            f"nicht 0 - wahrscheinlich unbalancierte Block-Struktur.",
            file=sys.stderr,
        )

    if args.diff:
        diff = difflib.unified_diff(
            original.splitlines(keepends=True),
            result.splitlines(keepends=True),
            fromfile=str(args.file),
            tofile=f"{args.file} (reindent)",
            n=2,
        )
        sys.stdout.writelines(diff)
        return 0

    if args.check:
        if original == result:
            print(f"{args.file}: bereits korrekt eingerueckt")
            return 0
        print(f"{args.file}: wuerde neu eingerueckt werden")
        return 1

    if original == result:
        print(f"{args.file}: unveraendert")
        return 0

    # CRLF beibehalten: reindent_text arbeitet mit splitlines(keepends=True),
    # also bleibt das urspruengliche Line-Ending pro Zeile erhalten.
    args.file.write_bytes(result.encode("utf-8"))
    print(f"{args.file}: neu eingerueckt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
