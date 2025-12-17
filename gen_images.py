#!/usr/bin/env python3
"""
Generate BMP images until total output size exceeds a target (default 2 GB).

Why BMP:
- Uncompressed, predictable size, fast to write
- Most viewers can open them

Install (if needed):
  python3 -m pip install pillow
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from PIL import Image


def human(n: int) -> str:
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if n < 1024:
            return f"{n:.1f} {unit}" if unit != "B" else f"{n} B"
        n /= 1024
    return f"{n:.1f} PB"


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--out", default="generated_images", help="Output directory")
    p.add_argument("--target-gb", type=float, default=2.0, help="Target total size in GB (GiB units)")
    p.add_argument("--width", type=int, default=12000, help="Image width in pixels")
    p.add_argument("--height", type=int, default=12000, help="Image height in pixels")
    p.add_argument("--max-files", type=int, default=10_000, help="Safety cap")
    args = p.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    target_bytes = int(args.target_gb * 1024 * 1024 * 1024)

    # Create one image and reuse it to avoid RAM churn.
    # Solid color still produces big BMPs because BMP is uncompressed.
    img = Image.new("RGB", (args.width, args.height), color=(123, 45, 67))

    total = 0
    i = 0

    print(f"Output: {out_dir.resolve()}")
    print(f"Target: {human(target_bytes)}")
    print(f"Each BMP approx: {human(args.width * args.height * 3)} (plus small header)")

    while total <= target_bytes and i < args.max_files:
        fname = out_dir / f"img_{i:05d}.bmp"
        img.save(fname, format="BMP")

        size = fname.stat().st_size
        total += size
        i += 1

        if i == 1 or i % 10 == 0 or total >= target_bytes:
            print(f"Files: {i:5d}  Total: {human(total)}  Last: {fname.name} ({human(size)})")

    if total > target_bytes:
        print(f"Done. Generated {i} images totaling {human(total)}")
    else:
        print(f"Stopped at safety cap ({args.max_files} files). Total: {human(total)}")


if __name__ == "__main__":
    main()
