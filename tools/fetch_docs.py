#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Holt eine lokale Kopie der offiziellen Agon-Platform-Doku.

Quelle: https://github.com/AgonPlatform/agon-docs
Rendered: https://agonplatform.github.io/agon-docs/

Die Markdown-Quellen landen in docs/agon-platform-docs/ (gitignored).
Damit sind die Docs auch offline lesbar und koennen mit Standard-
Markdown-Viewern (VS Code, grip, etc.) durchforstet werden.

Zwei Modi:
  --git        (default, wenn git verfuegbar) klont das Repo
               nach docs/agon-platform-docs/. Spaetere Aufrufe mit
               --git laufen als `git pull --ff-only`.
  --tarball    laedt den GitHub-Tarball von main und entpackt ihn
               (kein git noetig). Jeder Lauf ersetzt den Snapshot.

Beispiele:
    uv run tools/fetch_docs.py                # git clone/pull, default
    uv run tools/fetch_docs.py --tarball      # nur Tarball, ohne git
    uv run tools/fetch_docs.py --prune        # lokalen Stand komplett entfernen
"""

from __future__ import annotations

import argparse
import io
import shutil
import subprocess
import sys
import tarfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "docs" / "agon-platform-docs"
REPO = "https://github.com/AgonPlatform/agon-docs.git"
TARBALL_URL = "https://github.com/AgonPlatform/agon-docs/archive/refs/heads/main.tar.gz"


def log(msg: str) -> None:
    print(f"[fetch_docs] {msg}", flush=True)


def have_git() -> bool:
    try:
        subprocess.check_call(
            ["git", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        return True
    except (OSError, subprocess.CalledProcessError):
        return False


def clone_or_pull() -> int:
    if (TARGET / ".git").exists():
        log(f"Aktualisiere bestehenden Clone in {TARGET}")
        try:
            subprocess.check_call(["git", "-C", str(TARGET), "fetch", "--all"])
            subprocess.check_call(
                ["git", "-C", str(TARGET), "pull", "--ff-only"]
            )
        except subprocess.CalledProcessError as e:
            log(f"git pull fehlgeschlagen: {e}")
            return 1
        log(f"Aktueller Commit:")
        subprocess.check_call(
            ["git", "-C", str(TARGET), "log", "-1", "--oneline"]
        )
        return 0

    if TARGET.exists() and any(TARGET.iterdir()):
        log(
            f"{TARGET} ist nicht leer und kein Git-Repo. "
            "Bitte vorher --prune ausfuehren oder --tarball nutzen."
        )
        return 1

    log(f"Klone {REPO} -> {TARGET}")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    try:
        subprocess.check_call(
            ["git", "clone", "--depth", "1", REPO, str(TARGET)]
        )
    except subprocess.CalledProcessError as e:
        log(f"git clone fehlgeschlagen: {e}")
        return 1
    return 0


def fetch_tarball() -> int:
    log(f"Lade Tarball: {TARBALL_URL}")
    req = urllib.request.Request(
        TARBALL_URL, headers={"User-Agent": "AgonBasics-fetch_docs"}
    )
    with urllib.request.urlopen(req) as resp:
        data = resp.read()
    log(f"  {len(data) // 1024} KiB empfangen")

    if TARGET.exists():
        log(f"Loesche alten Snapshot: {TARGET}")
        shutil.rmtree(TARGET)
    TARGET.mkdir(parents=True, exist_ok=True)

    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tf:
        members = tf.getmembers()
        # Top-level-Ordner: agon-docs-main/
        roots = {m.name.split("/", 1)[0] for m in members if "/" in m.name}
        top = next(iter(roots)) if len(roots) == 1 else ""

        for m in members:
            if "/" not in m.name:
                continue
            if top and not m.name.startswith(top + "/"):
                continue
            rel = m.name.split("/", 1)[1] if top else m.name
            if not rel:
                continue
            if m.isdir():
                (TARGET / rel).mkdir(parents=True, exist_ok=True)
                continue
            dst = TARGET / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            f = tf.extractfile(m)
            if f is None:
                continue
            dst.write_bytes(f.read())
    log(f"Snapshot entpackt: {TARGET}")
    return 0


def prune() -> int:
    if not TARGET.exists():
        log(f"Nichts zu tun: {TARGET} existiert nicht.")
        return 0
    log(f"Loesche {TARGET}")
    shutil.rmtree(TARGET)
    return 0


def summary() -> None:
    if not TARGET.exists():
        return
    md_files = sorted(TARGET.rglob("*.md"))
    log(f"Lokale Doku-Dateien: {len(md_files)}")
    for p in md_files[:10]:
        log(f"  {p.relative_to(TARGET)}")
    if len(md_files) > 10:
        log(f"  ... ({len(md_files) - 10} weitere)")
    print()
    print("Schnellzugriff:")
    print(f"  VS Code:  code {TARGET}")
    print(f"  Browser:  file:///{TARGET.as_posix()}/README.md")
    print("  Online:   https://agonplatform.github.io/agon-docs/")


def main() -> int:
    parser = argparse.ArgumentParser(description="AgonBasics fetch_docs")
    parser.add_argument("--git", action="store_true", help="Git clone/pull (default)")
    parser.add_argument(
        "--tarball", action="store_true", help="Tarball-Snapshot (kein git)"
    )
    parser.add_argument(
        "--prune", action="store_true", help="Lokalen Doku-Ordner loeschen"
    )
    args = parser.parse_args()

    if args.prune:
        return prune()

    use_tarball = args.tarball and not args.git
    use_git = args.git or (not args.tarball and have_git())

    if use_git:
        rc = clone_or_pull()
    elif use_tarball or not have_git():
        rc = fetch_tarball()
    else:
        log("Weder --git noch --tarball ausgewaehlt und git nicht gefunden.")
        return 1

    if rc == 0:
        summary()
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
