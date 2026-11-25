#!/usr/bin/env python3
"""Stage externally distributed resources in a clean release checkout.

    python -m pip download --no-deps --only-binary=:all: eis1600==1.7.4 -d /tmp
    python scripts/prepare_release.py /tmp/eis1600-1.7.4-py3-none-any.whl
    python -m build

Copy the six CSV gazetteers from the evaluated installation into
eis1600/gazetteers/data before running this script.
"""
import argparse
import hashlib
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
OLD_WHEEL_SHA256 = "847baab09c16175a9b4fac0e9573e724374f7809e35af45757fb34cb4835d1d7"
GAZETTEERS = ("days", "months", "onomastic", "spelling", "toponyms", "years")
# These public command modules and ID tables shipped in 1.7.4 outside Git.
LEGACY = (
    "eis1600/helper/data/__init__.py",
    "eis1600/processing/short_miu_generation.py",
    "eis1600/processing/persistent_ids/__init__.py",
    "eis1600/processing/persistent_ids/deprecated_long_short_ids_mapping.json",
    "eis1600/processing/persistent_ids/long_short_ids_mapping.json",
    "eis1600/statistics/__init__.py",
    "eis1600/statistics/count_categories.py",
    "eis1600/statistics/count_tokens_per_miu.py",
    "eis1600/statistics/methods.py",
)


def main() -> None:
    """Restore the pinned public resources and check the production gazetteers."""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("wheel", type=Path, help="Official PyPI wheel for eis1600 1.7.4")
    wheel = parser.parse_args().wheel
    if hashlib.sha256(wheel.read_bytes()).hexdigest() != OLD_WHEEL_SHA256:
        parser.error("The wheel does not match the published 1.7.4 SHA-256.")
    gazetteers = ROOT / "eis1600/gazetteers/data"
    for name in GAZETTEERS:
        if not (gazetteers / f"{name}_gazetteer.csv").is_file():
            parser.error(f"Missing production gazetteer: {name}")
    with ZipFile(wheel) as archive:
        for name in LEGACY:
            target = ROOT / name
            content = archive.read(name)
            if target.exists() and target.read_bytes() != content:
                parser.error(f"Existing resource differs: {target}")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
    (gazetteers / "__init__.py").touch()


if __name__ == "__main__":
    main()
