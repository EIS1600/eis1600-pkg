#!/usr/bin/env python3
"""Replace temporal annotations in an existing book without loading BERT.

eis1600_retag_dates original.json.gz corrected.json.gz
"""

import argparse
import gzip
import os
from pathlib import Path
from tempfile import NamedTemporaryFile

import ijson
import ujson

from eis1600.dates.temporal import apply_temporal


def retag_book(source: Path, output: Path) -> int:
    """Stream the input MIUs and atomically install the completed gzip file."""
    output.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with NamedTemporaryFile(dir=output.parent, delete=False) as tmp:
        path = Path(tmp.name)
    try:
        with (
            gzip.open(source, "rb") as src,
            gzip.open(path, "wt", encoding="utf-8", compresslevel=3) as dst,
        ):
            dst.write("[")
            for row in ijson.items(src, "item", use_float=True):
                if count:
                    dst.write(",")
                dst.write(ujson.dumps(apply_temporal(row), ensure_ascii=False))
                count += 1
            dst.write("]")
        os.chmod(path, source.stat().st_mode & 0o777)
        path.replace(output)
    finally:
        path.unlink(missing_ok=True)
    return count


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("source", type=Path, help="Original package JSON gzip")
    parser.add_argument("output", type=Path, help="Destination JSON gzip")
    args = parser.parse_args()
    print(f"{retag_book(args.source, args.output)} text units written to {args.output}")
