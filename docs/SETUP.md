# Setup (Windows)

Von null auf lauffaehigen Emulator, mit Beispielen und Tests.

## Voraussetzungen

1. **Git** (z. B. Git for Windows)
2. **uv** (Python-Paket-/Script-Runner):
   ```
   winget install --id=astral-sh.uv -e
   ```
   oder
   ```
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```
3. Kein Python-System-Install noetig — `uv run` holt sich einen passenden
   Interpreter beim ersten Lauf selbst.

Pruefen:

```
uv --version
```

## Repository klonen

```
git clone https://github.com/cadextcp/AgonBasics.git
cd AgonBasics
```

(Ein Submodul ist nicht mehr noetig — der Emulator wird vom Setup-Skript
als Prebuilt-Binary heruntergeladen.)

## Erstes Setup

```
uv run tools/setup.py
```

Was passiert:

1. `fab-agon-emulator-v1.1.3-windows-x64.zip` wird nach `emulator/download/`
   geladen (~8 MB).
2. SHA-256 wird gegen eine gepinnte Pruefsumme verifiziert.
3. Das Archiv wird nach `emulator/fab-agon-emulator-v1.1.3-windows-x64/`
   entpackt.
4. Die mitgelieferte Popup-MOS-SD-Karte wandert nach `sdcard/staged/`.
5. `tools/deploy.py` kopiert `beispiele/` und `lib/` dahin hinein.

Am Ende sollten zwei Ordner existieren:

```
emulator/fab-agon-emulator-v1.1.3-windows-x64/
  ├── fab-agon-emulator.exe
  ├── agon-cli-emulator.exe
  ├── firmware/
  └── sdcard/   (Popup-MOS-Original, unveraendert)

sdcard/staged/
  ├── bin/bbcbasic.bin
  ├── bin/bbcbasic24.bin
  ├── bin/ez80asm.bin
  ├── mos/*, docs/*, demos/*, fonts/*
  ├── autoexec.txt
  └── beispiele/
      ├── hello.bas
      ├── sprite.bas
      ├── debug_demo.bas
      ├── debug.bas         (aus lib/)
      └── ...
```

## Erster Smoke-Test

```
uv run tools/run.py --headless --program hello.bas
```

Erwartete stdout (gekuerzt):

```
...
Hello AgonLight!
>
```

Falls das funktioniert, ist alles eingerichtet.

Fuer den grafischen Start:

```
uv run tools/run.py --program hello.bas
```

Ein SDL-Fenster oeffnet sich. Im BBC-BASIC-Prompt (`>`) tippen:

```
CHAIN "hello.bas"
```

und Enter.

## Haeufige Probleme

### `uv: command not found`

uv ist nicht installiert oder nicht in `PATH`. Siehe Voraussetzungen.

### `SHA-256 mismatch`

Der Download wurde unvollstaendig oder durch einen Proxy veraendert. Der
Setup-Exit-Code ist 2. Netzwerk / Proxy pruefen und `uv run tools/setup.py --force`
wiederholen.

### Emulator-Fenster stuerzt sofort ab

Haeufig Grafiktreiber-Probleme mit SDL3. Workaround: Software-Renderer:

```
uv run tools/run.py --program hello.bas --renderer sw
```

(wird via `extra_args` an den Emulator durchgereicht)

### `sdcard/staged/` fehlt

`uv run tools/setup.py` wurde noch nicht ausgefuehrt. Oder gel??scht?
Mit `uv run tools/setup.py --force` neu anlegen.

## Neuere Emulator-Version

In `tools/setup.py` sind Version und SHA-256 gepinnt. Um auf ein neueres
Release zu wechseln:

1. Unter <https://github.com/tomm/fab-agon-emulator/releases> die Windows-x64-ZIP-URL und deren SHA-256 holen.
2. `EMU_VERSION` und den Eintrag in `EMU_ASSETS["windows_x64"]` in
   `tools/setup.py` aktualisieren.
3. `uv run tools/setup.py --force` ausfuehren.

## Offline-Doku mit ziehen

Optional, aber empfohlen fuer Arbeit ohne Internet:

```
uv run tools/fetch_docs.py
```

Klont die offizielle Agon-Platform-Doku (<https://github.com/AgonPlatform/agon-docs>)
nach `docs/agon-platform-docs/` (gitignored). Danach in VS Code:

```
code docs/agon-platform-docs/
```

Details: [RESOURCES.md](RESOURCES.md) und [FAQ](https://agonplatform.github.io/agon-docs/FAQ/).
