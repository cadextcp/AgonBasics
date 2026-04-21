# UPSTREAM

**Quelle:** https://github.com/robogeek42/agon_sped
**Version:** `sped.bas` `VERSION$ = "v1.07"` (siehe Zeile 20)
**Geklont am:** 2026-04-21, Commit
`1162cba897f96cd8f92fb7ce4bb42d66b6fb00cf` ("Update README.md").
**Lizenz:** MIT, Copyright (c) 2023 robogeek42. Volle Lizenztext in
[`LICENSE`](LICENSE).

## Uebernommene Dateien

| Upstream-Datei | Ziel in AgonBasics          | Aenderungen                    |
|----------------|-----------------------------|-------------------------------|
| `sped.bas`     | `werkzeuge/sprite_editor/sped.bas`  | siehe unten                  |
| `sped.ini`    | `werkzeuge/sprite_editor/sped.ini`  | 1:1                           |
| `LICENSE`      | `werkzeuge/sprite_editor/LICENSE`    | 1:1                           |

## Bewusst weggelassen

- `sped102.bbc` ... `sped107.bbc` — vortokenisierte BBC-BASIC-Binaerdateien
  fuer den Agon. Auf echter Hardware laden sie schneller als `.bas`, im
  Emulator ist der Unterschied vernachlaessigbar. Wer sie fuer eine
  physische SD-Karte braucht, kann sie direkt aus dem Upstream holen.
- `spedADL.bas` / `spedADL106.bbc` / `spedADL107.bbc` — 24-Bit-ADL-Variante
  fuer bbcbasic24. AgonBasics nutzt Standard-`bbcbasic` (16-Bit-Z80-Mode),
  daher reicht die normale `sped.bas`.
- `examples/` — Beispiel-Bitmap-Exporte des Upstreams. Koennen bei Bedarf
  manuell nachgeladen werden.
- `number.py` — internes Hilfsskript des Upstream-Autors.
- `TODO.md` / `SpriteEditor_v1.00.png` — Projekt-Artefakte, die im
  AgonBasics-Repo keinen Mehrwert haben.

## Lokale Aenderungen an `sped.bas`

Folgen in einem **separaten Commit** (zur leichteren Nachvollziehbarkeit
gegen Upstream-Updates):

- **Einrueckung** von Block-Strukturen (FOR/NEXT, REPEAT/UNTIL, WHILE/WEND,
  DEF PROC/ENDPROC) mit 2 Spaces pro Ebene. Semantik-neutral —
  BBC BASIC Z80 ignoriert Whitespace zwischen Zeilennummer und Statement.
  Das Tooling liegt unter `tools/bbcbasic_indent.py` und ist idempotent,
  d. h. upstream-Updates koennen "roh" eingespielt und anschliessend mit
  dem Skript wieder formatiert werden.

## Update-Workflow

Fuer ein Upstream-Update (z. B. auf v1.08):

```
# 1) Temporaer klonen
cd /tmp && rm -rf agon_sped && git clone https://github.com/robogeek42/agon_sped.git

# 2) Rohe Datei uebernehmen
cp /tmp/agon_sped/sped.bas werkzeuge/sprite_editor/sped.bas
cp /tmp/agon_sped/sped.ini werkzeuge/sprite_editor/sped.ini

# 3) Einruecken mit unserem Skript
uv run tools/bbcbasic_indent.py werkzeuge/sprite_editor/sped.bas

# 4) Zeile VERSION$= in sped.bas pruefen und diese UPSTREAM.md-Datei
#    (Version + Commit + Datum) aktualisieren.

# 5) Commiten
git add werkzeuge/sprite_editor/
git commit -m "Update sped to v1.08 from upstream"
```
