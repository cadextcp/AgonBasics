#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Einmaliges Setup fuer AgonBasics.

Laedt den fab-agon-emulator (Windows x64) herunter, entpackt ihn nach
`emulator/` und staged die mitgelieferte SD-Karte (Popup MOS) nach
`sdcard/staged/`. Anschliessend werden `beispiele/` und `lib/` via
`tools/deploy.py` hineinkopiert.

Usage:
    uv run tools/setup.py                 # Standardlauf (interaktiv)
    uv run tools/setup.py --no-interactive  # fuer CI, keine Rueckfragen
    uv run tools/setup.py --force         # Download neu erzwingen
    uv run tools/setup.py --refresh-sdcard  # zusaetzlich frisches Popup MOS ziehen

Exit codes:
    0 = Erfolg
    1 = Download / Extraktion fehlgeschlagen
    2 = Hash mismatch (moeglicher Manipulationsversuch, Netzwerkfehler)
    3 = Voraussetzung nicht erfuellt (z. B. anderes OS)
"""

from __future__ import annotations

import argparse
import hashlib
import io
import os
import platform
import shutil
import subprocess
import sys
import tarfile
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Gepinnte Versionen und Pruefsummen
# ---------------------------------------------------------------------------
EMU_VERSION = "1.1.3"
EMU_ASSETS = {
    # key: (platform.system() lowercased + "_" + machine lowercased subset)
    "windows_x64": {
        "filename": f"fab-agon-emulator-v{EMU_VERSION}-windows-x64.zip",
        "url": (
            f"https://github.com/tomm/fab-agon-emulator/releases/download/"
            f"{EMU_VERSION}/fab-agon-emulator-v{EMU_VERSION}-windows-x64.zip"
        ),
        "sha256": (
            "bf51a5696ecfe9959765d6fb642b4312e1248d455f14a087c699dcd32b229fa2"
        ),
        "extract_dirname": f"fab-agon-emulator-v{EMU_VERSION}-windows-x64",
    },
    "linux_x86_64": {
        "filename": f"fab-agon-emulator-v{EMU_VERSION}-linux-x86_64.tar.bz2",
        "url": (
            f"https://github.com/tomm/fab-agon-emulator/releases/download/"
            f"{EMU_VERSION}/fab-agon-emulator-v{EMU_VERSION}-linux-x86_64.tar.bz2"
        ),
        "sha256": (
            "f274447e3abb5bbb2ff682924eddcb57ccb93d7bf041faa587b9116577bb4eb0"
        ),
        "extract_dirname": f"fab-agon-emulator-v{EMU_VERSION}-linux-x86_64",
    },
}

POPUP_MOS_TARBALL_URL = (
    "https://github.com/tomm/popup-mos/archive/refs/heads/main.tar.gz"
)


def pick_asset() -> dict:
    """Waehlt das passende Release-Asset fuer das aktuelle OS."""
    system = platform.system().lower()
    machine = platform.machine().lower()
    if system == "windows":
        return EMU_ASSETS["windows_x64"]
    if system == "linux" and machine in ("x86_64", "amd64"):
        return EMU_ASSETS["linux_x86_64"]
    raise RuntimeError(
        f"Nicht unterstuetzte Plattform: {system}/{machine}. "
        "Windows x64 und Linux x86_64 werden von den Release-Binaries "
        "abgedeckt. Fuer andere Plattformen bitte aus Source bauen (siehe "
        "docs/SETUP.md)."
    )


def log(msg: str) -> None:
    print(f"[setup] {msg}", flush=True)


def download(url: str, dest: Path, expected_sha256: str) -> None:
    """Laedt url nach dest, verifiziert SHA-256. Idempotent."""
    if dest.exists():
        actual = sha256_file(dest)
        if actual == expected_sha256:
            log(f"Bereits vorhanden und verifiziert: {dest.name}")
            return
        log(f"Vorhandene Datei hat falschen Hash, neu laden: {dest.name}")
        dest.unlink()

    dest.parent.mkdir(parents=True, exist_ok=True)
    log(f"Lade {url}")
    log(f"  -> {dest}")

    req = urllib.request.Request(url, headers={"User-Agent": "AgonBasics-setup"})
    with urllib.request.urlopen(req) as resp:
        total = int(resp.headers.get("Content-Length", 0))
        downloaded = 0
        last_pct = -1
        with dest.open("wb") as fp:
            while True:
                chunk = resp.read(64 * 1024)
                if not chunk:
                    break
                fp.write(chunk)
                downloaded += len(chunk)
                if total:
                    pct = int(downloaded * 100 / total)
                    if pct != last_pct and pct % 10 == 0:
                        log(
                            f"  {pct}% ({downloaded // 1024} / {total // 1024} KiB)"
                        )
                        last_pct = pct

    actual = sha256_file(dest)
    if actual != expected_sha256:
        dest.unlink()
        log(f"SHA-256 mismatch!")
        log(f"  erwartet: {expected_sha256}")
        log(f"  erhalten: {actual}")
        raise SystemExit(2)
    log(f"SHA-256 ok: {actual[:16]}...")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fp:
        for chunk in iter(lambda: fp.read(64 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def extract(archive: Path, target_root: Path) -> Path:
    """Entpackt archive (zip oder tar.bz2) nach target_root.

    Gibt den Pfad des entpackten Top-Level-Ordners zurueck.
    """
    target_root.mkdir(parents=True, exist_ok=True)

    if archive.suffix == ".zip":
        log(f"Entpacke {archive.name} -> {target_root}")
        with zipfile.ZipFile(archive) as zf:
            names = zf.namelist()
            # Top-Level-Ordner ermitteln
            top = _archive_top_dir(names)
            zf.extractall(target_root)
    elif archive.name.endswith(".tar.bz2"):
        log(f"Entpacke {archive.name} -> {target_root}")
        with tarfile.open(archive, "r:bz2") as tf:
            names = tf.getnames()
            top = _archive_top_dir(names)
            # Safety: Python 3.12+ erwartet filter=
            if sys.version_info >= (3, 12):
                tf.extractall(target_root, filter="data")
            else:
                tf.extractall(target_root)
    else:
        raise RuntimeError(f"Unbekanntes Archivformat: {archive.name}")

    extracted = target_root / top
    if not extracted.exists():
        raise RuntimeError(
            f"Erwarteten Ordner {extracted} nicht im Archiv gefunden"
        )
    return extracted


def _archive_top_dir(names: list[str]) -> str:
    """Ermittelt das gemeinsame Top-Level-Verzeichnis."""
    tops = {n.split("/", 1)[0] for n in names if n and "/" in n}
    tops.discard("")
    if len(tops) == 1:
        return next(iter(tops))
    # Falls kein gemeinsames Top-Dir, den Asset-Ordnernamen verwenden
    return ""


def stage_sdcard(emulator_root: Path, sdcard_staged: Path, force: bool) -> None:
    """Kopiert die mit dem Emulator ausgelieferte SD-Karte nach sdcard/staged/."""
    src = emulator_root / "sdcard"
    if not src.exists():
        raise RuntimeError(
            f"SD-Karte nicht im Emulator-Bundle gefunden: {src}"
        )

    if sdcard_staged.exists() and not force:
        log(f"sdcard/staged/ existiert bereits; ueberlagere Popup-MOS-Inhalte")
    else:
        if sdcard_staged.exists():
            log(f"sdcard/staged/ wird geloescht (--force)")
            shutil.rmtree(sdcard_staged)

    sdcard_staged.mkdir(parents=True, exist_ok=True)
    log(f"Kopiere SD-Karten-Inhalt: {src} -> {sdcard_staged}")
    _copy_tree(src, sdcard_staged)


def _copy_tree(src: Path, dst: Path) -> None:
    """Einfaches rekursives Kopieren, ueberschreibt Zieldateien."""
    for item in src.iterdir():
        target = dst / item.name
        if item.is_dir():
            target.mkdir(exist_ok=True)
            _copy_tree(item, target)
        else:
            shutil.copy2(item, target)


def refresh_popup_mos(sdcard_staged: Path) -> None:
    """Holt frischen Popup-MOS-Snapshot und ueberlagert sdcard/staged/."""
    log("Lade frischen Popup-MOS-Snapshot (tomm/popup-mos main)")
    downloads = ROOT / "emulator" / "download"
    downloads.mkdir(parents=True, exist_ok=True)
    tarball = downloads / "popup-mos-main.tar.gz"

    req = urllib.request.Request(
        POPUP_MOS_TARBALL_URL, headers={"User-Agent": "AgonBasics-setup"}
    )
    with urllib.request.urlopen(req) as resp, tarball.open("wb") as fp:
        shutil.copyfileobj(resp, fp)

    temp = downloads / "popup-mos-extract"
    if temp.exists():
        shutil.rmtree(temp)
    temp.mkdir()
    with tarfile.open(tarball, "r:gz") as tf:
        if sys.version_info >= (3, 12):
            tf.extractall(temp, filter="data")
        else:
            tf.extractall(temp)

    # Einziger Top-Level-Ordner: popup-mos-main/
    roots = [p for p in temp.iterdir() if p.is_dir()]
    if not roots:
        raise RuntimeError("Popup-MOS-Tarball leer?")
    popup_root = roots[0]

    log(f"Ueberlagere sdcard/staged/ mit {popup_root.name}")
    _copy_tree(popup_root, sdcard_staged)


def run_deploy() -> None:
    """Ruft tools/deploy.py auf, um beispiele/+lib/ zu kopieren."""
    log("Staged beispiele/ und lib/ in sdcard/staged/")
    cmd = [sys.executable, str(ROOT / "tools" / "deploy.py")]
    subprocess.check_call(cmd, cwd=ROOT)


def print_summary(emulator_root: Path, sdcard_staged: Path) -> None:
    print()
    log("Setup abgeschlossen.")
    log(f"  Emulator:     {emulator_root}")
    log(f"  SD-Karte:     {sdcard_staged}")
    print()
    print("Schnellstart:")
    print("  uv run tools/run.py --program hello.bas")
    print("  uv run tools/run.py --headless --program hello.bas")
    print("  uv run tools/debug.py --program debug_demo.bas")
    print("  uv run tools/test.py")


def main() -> int:
    parser = argparse.ArgumentParser(description="AgonBasics setup")
    parser.add_argument(
        "--force", action="store_true", help="Download und Extraktion erzwingen"
    )
    parser.add_argument(
        "--refresh-sdcard",
        action="store_true",
        help="Zusaetzlich frischen Popup-MOS-Snapshot holen",
    )
    parser.add_argument(
        "--no-interactive",
        action="store_true",
        help="Keine Rueckfragen (fuer CI)",
    )
    parser.add_argument(
        "--skip-deploy",
        action="store_true",
        help="beispiele/ und lib/ nicht stagen",
    )
    args = parser.parse_args()

    try:
        asset = pick_asset()
    except RuntimeError as e:
        log(str(e))
        return 3

    downloads = ROOT / "emulator" / "download"
    archive = downloads / asset["filename"]
    emulator_dir = ROOT / "emulator"

    # Bei --force den entpackten Emulator-Ordner wegwerfen (Download wird in
    # download() anhand Hash entschieden).
    extracted = emulator_dir / asset["extract_dirname"]
    if args.force and extracted.exists():
        log(f"Loesche entpackten Emulator: {extracted}")
        shutil.rmtree(extracted)

    # 1) Download + Hash-Check
    download(asset["url"], archive, asset["sha256"])

    # 2) Entpacken (idempotent: wenn Zielordner schon existiert, ueberspringen)
    if extracted.exists() and not args.force:
        log(f"Bereits entpackt: {extracted}")
    else:
        extract(archive, emulator_dir)

    # 3) SD-Karte staging
    sdcard_staged = ROOT / "sdcard" / "staged"
    stage_sdcard(extracted, sdcard_staged, force=args.force)

    # 4) optional: frischen Popup-MOS ueberlagern
    if args.refresh_sdcard:
        refresh_popup_mos(sdcard_staged)

    # 5) eigene Beispiele stagen
    if not args.skip_deploy:
        run_deploy()

    print_summary(extracted, sdcard_staged)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
