# Links & Ressourcen

Die **offizielle Agon-Platform-Doku** unter <https://agonplatform.github.io/agon-docs/>
ist die kanonische Quelle fuer MOS-, VDP- und BBC-BASIC-Details.
`tools/fetch_docs.py` klont eine lokale Kopie in `docs/agon-platform-docs/`
(gitignored) fuer Offline-Zugriff.

## Offizielle Agon-Platform-Doku (agonplatform.github.io)

Quelle: <https://github.com/AgonPlatform/agon-docs> (MkDocs-Material)

### Einstieg

- [Start here](https://agonplatform.github.io/agon-docs/) - Willkommen + Einordnung der Firmware-Bestandteile
- [FAQ](https://agonplatform.github.io/agon-docs/FAQ/) - haeufige Probleme und Antworten
- [Theory of operation](https://agonplatform.github.io/agon-docs/Theory-of-operation/) - Architektur eZ80 + ESP32, Speicherkarte, CPU-Modi
- [Programming](https://agonplatform.github.io/agon-docs/Programming/) - Ueberblick: wie man fuer Agon programmiert

### MOS (Machine Operating System)

Alles Host-seitige bis hin zum BASIC-Start.

- [MOS Overview](https://agonplatform.github.io/agon-docs/MOS/) - CLI, autoexec.txt, Dateisystem
- [Star commands (CLI)](https://agonplatform.github.io/agon-docs/mos/Star-Commands/) - `*CAT`, `*CD`, `*LOAD`, `*RUN`, `*FX`, `*EDIT`, ...
- [MOS API](https://agonplatform.github.io/agon-docs/mos/API/) - RST 08h Syscalls, `mos_api.inc` fuer Assembler
- [C functions](https://agonplatform.github.io/agon-docs/mos/C-Functions/) - C-Header fuer AgDev-Projekte
- [Executable format](https://agonplatform.github.io/agon-docs/mos/Executables/) - Magic Bytes, Header, Z80 vs. ADL
- [Modules](https://agonplatform.github.io/agon-docs/mos/Modules/) - Lade- und Unload-Logik
- [System Variables](https://agonplatform.github.io/agon-docs/mos/System-Variables/) - SYSVARS-Block, wichtig fuer Debugging und Timing
- [Argument Substitution](https://agonplatform.github.io/agon-docs/mos/Argument-Substitution/) - `$1..$9` im MOS-CLI
- [Keyboard Input](https://agonplatform.github.io/agon-docs/mos/Keyboard/) - PS/2-Handling, Key-Codes, Layouts

### VDP (Visual Display Processor / ESP32)

Alles Bildschirm-, Sound- und Input-seitige.

- [VDP Overview](https://agonplatform.github.io/agon-docs/VDP/) - Einfuehrung, Command-Protokoll zwischen eZ80 und ESP32
- [VDU / Main Commands](https://agonplatform.github.io/agon-docs/vdp/VDU-Commands/) - `VDU 0..31` Grundbefehle
- [Screen Modes](https://agonplatform.github.io/agon-docs/vdp/Screen-Modes/) - alle Modi inkl. Doppelpufferung
- [PLOT Commands](https://agonplatform.github.io/agon-docs/vdp/PLOT-Commands/) - `VDU 25,k,x;y;` Zeichen-Operationen
- [System Commands](https://agonplatform.github.io/agon-docs/vdp/System-Commands/) - `VDU 23,0,...` Erweiterungen
- [Enhanced Audio API](https://agonplatform.github.io/agon-docs/vdp/Enhanced-Audio-API/) - Kanaele, Samples, Huellkurven
- [Bitmaps and Sprites API](https://agonplatform.github.io/agon-docs/vdp/Bitmaps-API/) - `VDU 23,27,...` (unser `sprite.bas`)
- [Buffered Commands API](https://agonplatform.github.io/agon-docs/vdp/Buffered-Commands-API/) - `VDU 23,0,&A0,...` Datenpuffer
- [Context Management API](https://agonplatform.github.io/agon-docs/vdp/Context-Management-API/) - Render-Kontexte stacken
- [Copper Effects API](https://agonplatform.github.io/agon-docs/vdp/Copper-API/) - Scanline-basierte Effekte
- [Font Management API](https://agonplatform.github.io/agon-docs/vdp/Font-API/) - eigene Bitmap-Fonts laden
- [Tile Engine](https://agonplatform.github.io/agon-docs/vdp/Tile-Engine/) - Hardware-Tilemap
- [VDP Variables](https://agonplatform.github.io/agon-docs/vdp/VDP-Variables/) - lesbare VDP-interne Zustaende

### BBC BASIC

- [BBC Basic](https://agonplatform.github.io/agon-docs/BBC-BASIC-for-Agon/) - Sprache + Agon-Erweiterungen (nur eine Seite, aber sehr dicht)

### Sonstiges

- [GPIO](https://agonplatform.github.io/agon-docs/GPIO/) - Pin-Belegung, UART1
- [Updating Firmware](https://agonplatform.github.io/agon-docs/Updating-Firmware/) - `mos/flash.bin` Workflow
- [External documentation](https://agonplatform.github.io/agon-docs/External-Documentation/) - Links zu Zilog, BBC BASIC, FatFS
- [Third party projects](https://agonplatform.github.io/agon-docs/Third-Party-Projects/) - Community-Projekte

### Offline lesen

```
uv run tools/fetch_docs.py          # git clone/pull (default)
uv run tools/fetch_docs.py --tarball  # ohne git, main-Snapshot
uv run tools/fetch_docs.py --prune    # lokalen Stand loeschen
```

Das landet in `docs/agon-platform-docs/` (gitignored). In VS Code:
`code docs/agon-platform-docs/` oeffnen und die Markdown-Dateien lesen.

### Quick-Reference

Haeufige VDU-/PLOT-Codes, MOS-Syscalls, Speicherkarte und Screen-Modes
in lokalisierter Kurzform: [REFERENCE.md](REFERENCE.md).

---

## Emulator & SD-Karte

- **fab-agon-emulator** - <https://github.com/tomm/fab-agon-emulator>
- **Windows-Release v1.1.3** - <https://github.com/tomm/fab-agon-emulator/releases/tag/1.1.3>
- **Debug-I/O-Ports (README)** - <https://github.com/tomm/fab-agon-emulator#debug-io-space>
- **Popup MOS** (batteriebetriebene SD-Karte) - <https://github.com/tomm/popup-mos>

## BBC BASIC Interpreter

- **agon-bbc-basic** (Z80, 64 KiB) - <https://github.com/breakintoprogram/agon-bbc-basic>
- **agon-bbc-basic-adl** (ADL-Modus, 512 KiB) - <https://github.com/breakintoprogram/agon-bbc-basic-adl>
- **BBC-BASIC-Manual (Agon, Mirror)** - <https://oldpatientsea.github.io/agon-bbc-basic-manual/0.1/index.html>
- **R. T. Russell BBC BASIC Home** - <https://www.bbcbasic.co.uk/>

## Firmware

- **AgonPlatform MOS** - <https://github.com/AgonPlatform/agon-mos>
- **AgonPlatform VDP** - <https://github.com/AgonPlatform/agon-vdp>
- **Quark MOS (original)** - <https://github.com/breakintoprogram/agon-mos>
- **agon-flash** (Firmware-Updater) - <https://github.com/envenomator/agon-flash>

## Tools auf dem Geraet

- **ez80asm** - <https://github.com/envenomator/agon-ez80asm>
- **agon-utilities** (grep, sort, nano, vi, ...) - <https://github.com/lennart-benschop/agon-utilities>
- **agon-hexload** - <https://github.com/envenomator/agon-hexload>

## Hardware

- **The Byte Attic (Agon Light 2)** - <https://www.thebyteattic.com/p/agon.html>
- **eZ80F92 Datenblatt** - <https://www.zilog.com/docs/ez80acclaim/ps0153.pdf>
- **eZ80 CPU User Manual (UM0077)** - <http://www.zilog.com/docs/um0077.pdf>

## Community

- **Agon Discord** - per Einladung (siehe Byte-Attic-Seite)
- **Break Into Program Blog** - <http://www.breakintoprogram.co.uk/hardware/computers/agon>

## Dieses Projekt

- Repo - <https://github.com/cadextcp/AgonBasics>
- Issues / Pull Requests willkommen
