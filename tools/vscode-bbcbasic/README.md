# BBC BASIC (Agon) — lokale VS-Code-Extension

Schlankes Syntax-Highlighting fuer BBC-BASIC-Quelltext (`.bas`), wie er
im AgonBasics-Projekt benutzt wird. Zielt auf BBC BASIC Z80 3.00 auf
Agon Light / Console8 — deshalb heisst die Extension `bbcbasic-agon`.

## Features

- **Syntax-Highlighting**: REM-Kommentare, Zeilennummern, Strings,
  Hex-Zahlen, Keywords (IF/FOR/REPEAT/DEF/...), IO-Befehle (VDU/MODE/
  GCOL/PLOT/...), Star-Commands (`*FX`, `*CD`), PROC-/FN-Aufrufe.
- **Go to Definition** (Strg+Klick): Klick auf einen `PROC_tick`- oder
  `FN_dbg_time`-Aufruf springt zur passenden `DEF`-Zeile. Sucht zuerst
  im aktuellen Dokument, dann workspace-weit in allen `.bas`-Dateien
  (ausser `sdcard/staged/`, wo auto-inlined Library-Kopien liegen).
- **Outline / Go to Symbol** (Ctrl+Shift+O): listet alle PROCs und
  FNs einer Datei.
- **Hover-Dokumentation**: Maus ueber `VDU 23, 27, 13, x; y;` (oder
  `*FX 19`, `VDU 22`, ...) zeigt Beschreibung + Link auf die offizielle
  Agon-Doku. Tabelle der erkannten Muster: siehe `DOC_PATTERNS` in
  `extension.js`.
- **Snippets fuer haeufige Muster**: tippe z. B. `vdu-sprite-move` und
  Tab fuellt `VDU 23, 27, 13, x%; y%;` mit Platzhaltern aus. Komplette
  Sprite-Initialisierung mit `vdu-sprite-setup`. Liste der Prefixe:
  siehe `snippets/bbcbasic.json` (unten).
- **Toggle Line Comment** (Ctrl+/): setzt/entfernt `REM` am Zeilenanfang.

## Snippet-Prefixe

Im BBC-BASIC-Editor `prefix` eingeben und Tab druecken:

| Prefix                     | expandiert zu                                     |
|----------------------------|---------------------------------------------------|
| `vdu-mode`                 | `VDU 22, 8`                                       |
| `vdu-cursor-off`           | `VDU 23, 1, 0`                                    |
| `vdu-cursor-on`            | `VDU 23, 1, 1`                                    |
| `vdu-bitmap-select`        | `VDU 23, 27, 0, 0`                                |
| `vdu-bitmap-load`          | kompletter Loader-Block (OPENIN + BGET-Loop)      |
| `vdu-sprite-select`        | `VDU 23, 27, 4, 0`                                |
| `vdu-sprite-clear`         | `VDU 23, 27, 5`                                   |
| `vdu-sprite-add-frame`     | `VDU 23, 27, 6, 0`                                |
| `vdu-sprite-active`        | `VDU 23, 27, 7, 1`                                |
| `vdu-sprite-show`          | `VDU 23, 27, 11`                                  |
| `vdu-sprite-hide`          | `VDU 23, 27, 12`                                  |
| `vdu-sprite-move`          | `VDU 23, 27, 13, x%; y%;`                         |
| `vdu-sprite-refresh`       | `VDU 23, 27, 15`                                  |
| `vdu-sprite-setup`         | Bitmap laden + Sprite koppeln + aktivieren        |
| `plot-rect`                | `MOVE` + `PLOT 101` Rechteck                      |
| `gcol`                     | `GCOL 0, 7`                                       |
| `clg`                      | `GCOL 0, 0 : CLG`                                 |
| `fx-vsync`                 | `*FX 19`                                          |
| `fx-keydelay`              | `*FX 11, 250`                                     |
| `fx-keyrate`               | `*FX 12, 33`                                      |
| `def-proc`                 | DEF PROC-Geruest mit ENDPROC                      |
| `def-fn`                   | einzeilige FN-Definition                          |
| `repeat`                   | REPEAT/UNTIL-Loop                                 |
| `for`                      | FOR/NEXT-Loop                                     |
| `inkey-scan`               | INKEY(-66) Scancode-Pattern                       |
| `inkey-char`               | `k% = INKEY(0)`                                   |
| `openin`                   | Datei oeffnen + CLOSE (mit Fehlercheck)           |

## Warum nicht einfach "Visual Basic"?

VS Code liefert eine VB-Grammatik mit, die bei File-Association
`*.bas -> vb` greift. Sie erkennt aber **nur `'`-Kommentare, nicht
`REM`**. In BBC BASIC ist `REM` der kanonische Kommentar-Einleiter,
deshalb wuerden REM-Zeilen im Editor wie Variablen-Referenzen
aussehen — nicht wie Kommentare.

Diese Extension bringt eine minimale eigene TextMate-Grammar mit,
die BBC-BASIC-spezifisch ist:

- `REM ...` → `comment.line.rem.bbcbasic`
- Zeilennummern am Zeilenanfang → `entity.name.tag.line-number.bbcbasic`
- Hex-Zahlen `&FF` → `constant.numeric.hex.bbcbasic`
- Strings mit `""`-Escape
- Control-Keywords (IF/THEN/ELSE/FOR/NEXT/REPEAT/UNTIL/...)
- Deklarationen (DEF PROC/FN/LOCAL/DIM)
- IO-Befehle (PRINT, VDU, MODE, GCOL, PLOT, MOVE, ...)
- `*FX`, `*CD`, `*DIR` und andere Star-Commands
- `PROC_xyz` / `FN_xyz` Aufrufe als Funktionsnamen

## Installation

Vom Repo-Root:

```
uv run tools/install_vscode_extension.py
```

Danach VS Code neu laden (Ctrl+Shift+P → "Developer: Reload Window")
und im Workspace ist `.bas` automatisch als `bbcbasic` registriert.

## Deinstallation

```
uv run tools/install_vscode_extension.py --uninstall
```

Oder manuell:

```
rm -rf ~/.vscode/extensions/bbcbasic-agon-*
```

Oder via VS Code: Extensions-Panel → "BBC BASIC (Agon)" → Uninstall.

## Struktur der Extension

```
tools/vscode-bbcbasic/
├── package.json                       Extension-Manifest (main, contributes, ...)
├── language-configuration.json        Comment-Marker, Brackets, Word-Pattern
├── extension.js                       Provider fuer Go-to-Def, Outline, Hover-Docs
├── snippets/
│   └── bbcbasic.json                  Code-Snippets (VDU, Sprite, FX, Control-Flow)
├── syntaxes/
│   └── bbcbasic.tmLanguage.json       TextMate-Grammar (die Farben)
└── README.md                          diese Datei
```

`extension.js` ist pure JavaScript (kein TypeScript-Build, keine
npm-Dependencies). Laesst sich mit `node --check extension.js` auf
Syntaxfehler pruefen.

## Farbe anpassen

Wenn du die REM-Kommentare z. B. fetter und gruener willst als dein
Theme-Default, in deine **User-Settings** (nicht Workspace, damit andere
Kollegen das nicht auch kriegen):

```json
"editor.tokenColorCustomizations": {
    "textMateRules": [
        {
            "scope": "comment.line.rem.bbcbasic",
            "settings": {
                "foreground": "#7CB342",
                "fontStyle": "italic bold"
            }
        },
        {
            "scope": "keyword.other.rem.bbcbasic",
            "settings": {
                "foreground": "#7CB342",
                "fontStyle": "bold"
            }
        }
    ]
}
```

`keyword.other.rem.bbcbasic` ist das `REM`-Keyword selbst,
`comment.line.rem.bbcbasic` ist der Rest der Zeile.

## Live-Scope-Inspektion

Mit `Developer: Inspect Editor Tokens and Scopes` in der Command-Palette
siehst du an jeder Cursor-Position, welcher Scope gerade greift. Nuetzlich,
wenn du eigene Tokens (MODE, VDU, etc.) separat einfaerben willst.
