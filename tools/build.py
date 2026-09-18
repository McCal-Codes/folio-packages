#!/usr/bin/env python3
"""Builds the site Folio reads: a package file per folder, an index that pins them, and a signed pointer to it.

    python3 tools/build.py                 # build site/ without signing (what a pull request gets)
    python3 tools/build.py --key key.pem   # build and sign, which is what CI does with the repo's secret

The result is `site/`, ready to serve:

    site/entry.json        timestamp, maxAge and the index's hash
    site/entry.json.sig    detached signature over entry.json's exact bytes
    site/index.json        the package list, each with a copy of its manifest, its sha256 and its size
    site/key.pub           the public key, base64 SPKI, shown to the user as a fingerprint
    site/packages/*.foliopkg
    site/assets/<id>/...   the pictures each package names

This is a stand-in for `folio-pkg`, the Kotlin tool that will share the app's own parser. It does the mechanical part
faithfully - the same zip layout, the same hashes, the same signature - and leaves real validation to CI and the app.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import pathlib
import shutil
import subprocess
import sys
import time
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
PACKAGES = ROOT / "packages"
SITE = ROOT / "site"

# A week. Folio refuses an index older than this, so CI has to publish at least that often.
MAX_AGE = 7 * 24 * 60 * 60

NAME = "Folio packages"
DESCRIPTION = "Themes and tweaks for Folio, published from github.com/McCal-Codes/folio-packages."
ISSUES = "https://github.com/McCal-Codes/folio-packages/issues/new"

PICTURE_SUFFIXES = {".png", ".webp", ".jpg", ".jpeg"}
IN_PACKAGE = {"manifest.json", "depiction.json", "tweaks.json", "theme.json", "layout.json", "iconpack.json"}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def text_of(value) -> str:
    return value if isinstance(value, str) else (value or {}).get("en", "")


def pack(folder: pathlib.Path) -> bytes:
    """Zips the files that belong inside a package. Pictures stay out: they're served from the site."""
    buffer = SITE / f".{folder.name}.zip"
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for name in sorted(p.name for p in folder.iterdir() if p.name in IN_PACKAGE):
            zf.write(folder / name, name)
    data = buffer.read_bytes()
    buffer.unlink()
    return data


def copy_pictures(folder: pathlib.Path, package_id: str) -> None:
    source = folder / "assets"
    if not source.is_dir():
        return
    target = SITE / "assets" / package_id
    target.mkdir(parents=True, exist_ok=True)
    for picture in sorted(source.iterdir()):
        if picture.suffix.lower() in PICTURE_SUFFIXES:
            shutil.copy2(picture, target / picture.name)


def site_path(package_id: str, path: str) -> str:
    """`assets/icon.png` inside a package becomes `assets/<id>/icon.png` on the site."""
    return f"assets/{package_id}/{path.split('/')[-1]}" if path.startswith("assets/") else path


def rewrite_depiction(depiction: dict, package_id: str) -> dict:
    for block in depiction.get("blocks", []):
        if block.get("type") == "hero" and "image" in block:
            block["image"] = site_path(package_id, block["image"])
        if block.get("type") == "screenshots":
            block["images"] = [site_path(package_id, image) for image in block.get("images", [])]
    return depiction


def build() -> dict:
    if SITE.exists():
        shutil.rmtree(SITE)
    (SITE / "packages").mkdir(parents=True)

    entries = []
    for folder in sorted(p for p in PACKAGES.iterdir() if p.is_dir()):
        manifest_file = folder / "manifest.json"
        if not manifest_file.exists():
            print(f"skipping {folder.name}: no manifest.json", file=sys.stderr)
            continue
        manifest = json.loads(manifest_file.read_text())
        package_id = manifest["id"]
        manifest.pop("$schema", None)
        if "icon" in manifest:
            manifest["icon"] = site_path(package_id, manifest["icon"])

        data = pack(folder)
        url = f"packages/{package_id}_{manifest['version']}.foliopkg"
        (SITE / url).write_bytes(data)
        copy_pictures(folder, package_id)

        depiction_file = folder / "depiction.json"
        if depiction_file.exists():
            depiction = rewrite_depiction(json.loads(depiction_file.read_text()), package_id)
            depiction.pop("$schema", None)
            (SITE / "assets" / package_id).mkdir(parents=True, exist_ok=True)
            (SITE / "assets" / package_id / "depiction.json").write_text(json.dumps(depiction, indent=2))

        entries.append({
            "id": package_id,
            "version": manifest["version"],
            "url": url,
            "sha256": sha256(data),
            "size": len(data),
            "manifest": manifest,
        })
        print(f"packed {package_id} {manifest['version']} ({len(data):,} bytes)")

    index = {
        "format": 1,
        "name": NAME,
        "description": DESCRIPTION,
        "issuesUrl": ISSUES,
        "featured": [],
        "packages": entries,
    }
    index_bytes = json.dumps(index, indent=2).encode()
    (SITE / "index.json").write_bytes(index_bytes)

    revoked = ROOT / "revoked.json"
    revocations = json.loads(revoked.read_text()) if revoked.exists() else {"format": 1, "packages": []}
    revocations["timestamp"] = int(time.time())
    (SITE / "revoked.json").write_bytes(json.dumps(revocations, indent=2).encode())

    entry = {
        "format": 1,
        "keyId": "",  # filled in when a key is given; unsigned builds are for reading, not for Folio
        "timestamp": int(time.time()),
        "maxAge": MAX_AGE,
        "index": {"path": "index.json", "sha256": sha256(index_bytes), "size": len(index_bytes)},
    }
    return entry


def key_id(spki: bytes) -> str:
    return hashlib.sha256(spki).hexdigest()[:16].upper()


def sign(entry: dict, key: pathlib.Path) -> None:
    """ECDSA P-256 over entry.json's exact bytes, which is what Folio's SourceKey verifies (SHA256withECDSA)."""
    spki = subprocess.run(
        ["openssl", "ec", "-in", str(key), "-pubout", "-outform", "DER"],
        check=True, capture_output=True,
    ).stdout
    entry["keyId"] = key_id(spki)
    entry_bytes = json.dumps(entry, indent=2).encode()
    (SITE / "entry.json").write_bytes(entry_bytes)
    (SITE / "key.pub").write_text(base64.b64encode(spki).decode())

    for name in ("entry.json", "revoked.json"):
        signature = subprocess.run(
            ["openssl", "dgst", "-sha256", "-sign", str(key)],
            input=(SITE / name).read_bytes(), check=True, capture_output=True,
        ).stdout
        (SITE / f"{name}.sig").write_text(base64.b64encode(signature).decode())
    print(f"signed with key {entry['keyId']}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--key", type=pathlib.Path, help="private key in PEM form; without it the site is unsigned")
    args = parser.parse_args()

    entry = build()
    if args.key:
        sign(entry, args.key)
    else:
        (SITE / "entry.json").write_bytes(json.dumps(entry, indent=2).encode())
        print("built unsigned: Folio will refuse this site until CI signs it")


if __name__ == "__main__":
    main()
