# AgonBasics

BBC BASIC Beispiele für den [Agon Light](https://www.thebyteattic.com/p/agon.html) bzw. den [fab-agon-emulator](https://github.com/tomm/fab-agon-emulator).

## Beispiele

| Datei | Beschreibung |
|---|---|
| `hello.bas` | Hello World |
| `eingabe.bas` | Tastatureingabe und INKEY |
| `schleife.bas` | FOR/NEXT Schleife |
| `dreieck.bas` | Gefülltes Dreieck (PLOT) |
| `rechteck.bas` | Rechteck zeichnen (DRAW) |
| `kreis.bas` | Kreis zeichnen (PLOT) |
| `prozedur.bas` | DEF PROC Prozeduren |
| `melodie.bas` | Melodie mit SOUND/DATA |
| `datei.bas` | Datei-Operationen (OPENOUT/CLOSE#) |
| `assembler.bas` | Inline eZ80 Assembler |
| `sprite.bas` | Hardware-Sprite laden und mit WASD bewegen |
| `timer.bas` | 20-Minuten Countdown mit Regenbogen-Animation |

## Setup

```bash
git clone --recurse-submodules https://github.com/cadextcp/AgonBasics.git
cd AgonBasics

# Beispiele in die SD-Karte des Emulators kopieren
cp beispiele/*.bas fab-agon-emulator/sdcard/beispiele/
cp beispiele/ship.rgba fab-agon-emulator/sdcard/beispiele/
```

## Benutzung im Emulator

```
*CD beispiele
LOAD "hello.bas"
RUN
```

## Hinweise

- Alle `.bas`-Dateien sind im Textformat mit CRLF-Zeilenenden (wie von BBC BASIC für Agon erwartet).
- `ship.rgba` ist ein 16x16 Sprite im RGBA8888-Format für `sprite.bas`.
- `make_ship.py` erzeugt die `ship.rgba` Bitmap neu.
