#!/usr/bin/env python3
"""
Generate images (JPEG or BMP) until total output size exceeds a target.

- JPEG: random noise + configurable quality to avoid ZIP compression
- BMP: uncompressed, very predictable size
"""

from __future__ import annotations
import argparse
from pathlib import Path

import numpy as np
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
    p.add_argument("--target-gb", type=float, default=2.0, help="Target total size in GB")
    p.add_argument("--width", type=int, default=8000, help="Image width in pixels")
    p.add_argument("--height", type=int, default=8000, help="Image height in pixels")
    p.add_argument(
        "--format",
        choices=["jpeg", "bmp"],
        default="jpeg",
        help="Image format to generate",
    )
    p.add_argument(
        "--quality",
        type=int,
        default=95,
        help="JPEG quality (only used when --format=jpeg)",
    )
    p.add_argument("--max-files", type=int, default=20, help="Safety cap")
    args = p.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    target_bytes = int(args.target_gb * 1024 * 1024 * 1024)
    total = 0
    i = 0

    print(f"Output: {out_dir.resolve()}")
    print(f"Target: {human(target_bytes)}")
    print(f"Format: {args.format.upper()}")
    print(f"Image size: {args.width}x{args.height}px")

    while total <= target_bytes and i < args.max_files:
        ext = "jpg" if args.format == "jpeg" else "bmp"
        fname = out_dir / f"img_{i:03d}.{ext}"

        if args.format == "jpeg":
            # Random noise to avoid ZIP compression
            array = np.random.randint(
                0, 256, (args.height, args.width, 3), dtype=np.uint8
            )
            img = Image.fromarray(array)
            img.save(
                fname,
                format="JPEG",
                quality=args.quality,
                optimize=False,
            )
        else:
            # BMP: uncompressed, predictable size
            img = Image.new("RGB", (args.width, args.height), color=(123, 45, 67))
            img.save(fname, format="BMP")

        size = fname.stat().st_size
        total += size
        i += 1

        if i == 1 or i % 2 == 0 or total >= target_bytes:
            print(
                f"Files: {i:2d}  Total: {human(total)}  "
                f"Last: {fname.name} ({human(size)})"
            )

    if total > target_bytes:
        print(f"Done. Generated {i} images totaling {human(total)}")
    else:
        print(f"Stopped at safety cap ({args.max_files} files). Total: {human(total)}")


if __name__ == "__main__":
    main()
