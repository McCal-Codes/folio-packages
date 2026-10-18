#!/usr/bin/env python3
"""House rules for packages in this repository, on top of Folio's own validator.

    python3 tools/check-submission.py            # every folder in packages/

folio-pkg checks that a package is well formed. This checks what a schema can't: that a community package doesn't
borrow a name that belongs to Folio or to the template, that its folder is named after it, and that nothing in it is
too big or of a kind a package has no business carrying. No dependencies beyond python3.
"""

from __future__ import annotations

import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PACKAGES = ROOT / "packages"

# Ids Folio and its own sources use. A community package claiming one is claiming to be Folio's.
RESERVED_PREFIXES = ("com.mccal.",)
# The template's id: a copy that was never renamed would collide with every other unrenamed copy.
TEMPLATE_IDS = {"dev.example.hello-tweak"}
ALLOWED_SUFFIXES = {".json", ".png", ".webp", ".jpg", ".jpeg"}
MAX_FILE_BYTES = 2 * 1024 * 1024
MAX_PACKAGE_BYTES = 20 * 1024 * 1024
URL = re.compile(r"\b[a-z][a-z0-9+.-]*://[^\s\"']+", re.IGNORECASE)


def check(folder: pathlib.Path) -> list[str]:
    errors: list[str] = []
    where = f"packages/{folder.name}"
    manifest_file = folder / "manifest.json"
    if not manifest_file.is_file():
        return [f"{where}: no manifest.json"]
    try:
        manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        return [f"{where}/manifest.json: not valid JSON ({e})"]

    package_id = str(manifest.get("id", ""))
    if folder.name != package_id:
        errors.append(f"{where}: the folder must be named after the package id ({package_id or 'missing'})")
    if package_id.startswith(RESERVED_PREFIXES):
        errors.append(f"{where}: {package_id} is in a namespace reserved for Folio; use your own reverse domain")
    if package_id in TEMPLATE_IDS:
        errors.append(f"{where}: {package_id} is the template's id; give the package an id of its own")

    total = 0
    for path in sorted(p for p in folder.rglob("*") if p.is_file()):
        rel = f"{where}/{path.relative_to(folder)}"
        size = path.stat().st_size
        total += size
        if path.name.startswith("."):
            errors.append(f"{rel}: hidden files don't belong in a package")
        elif path.suffix.lower() not in ALLOWED_SUFFIXES:
            errors.append(f"{rel}: only JSON and pictures (png, webp, jpg) may be in a package")
        if size > MAX_FILE_BYTES:
            errors.append(f"{rel}: {size:,} bytes; each file must be under {MAX_FILE_BYTES:,}")
        if path.suffix.lower() == ".json":
            for url in URL.findall(path.read_text(encoding="utf-8", errors="replace")):
                if not url.lower().startswith("https://"):
                    errors.append(f"{rel}: {url} must be an https:// link")
    if total > MAX_PACKAGE_BYTES:
        errors.append(f"{where}: {total:,} bytes in all; a package must stay under {MAX_PACKAGE_BYTES:,}")
    return errors


def main() -> int:
    folders = sorted(p for p in PACKAGES.iterdir() if p.is_dir()) if PACKAGES.is_dir() else []
    errors = [e for folder in folders for e in check(folder)]
    for e in errors:
        print(f"✗ {e}")
    print(f"{len(folders)} package(s), {len(errors)} problem(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
