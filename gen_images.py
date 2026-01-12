#!/usr/bin/env python3
"""
Generate JPEG images until total output size exceeds a target.

- Each image contains random pixels to prevent heavy compression.
- Defaults set to produce fewer, large images (~several hundred MB each).
"""

from __future__ import annotations
import argparse
from pathlib import Path
import shutil
import numpy as np
from PIL import Image

def human(n: int) -> str:
    """Convert bytes to human-readable format."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if n < 1024:
            return f"{n:.1f} {unit}" if unit != "B" else f"{n} B"
        n /= 1024
    return f"{n:.1f} PB"

def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--out", default="generated_images", help="Output directory")
    p.add_argument("--target-gb", type=float, default=2.0, help="Target total size in GB")
    p.add_argument("--width", type=int, default=16000, help="Image width in pixels")
    p.add_argument("--height", type=int, default=16000, help="Image height in pixels")
    p.add_argument("--quality", type=int, default=95, help="JPEG quality (1-100)")
    p.add_argument("--max-files", type=int, default=50, help="Safety cap to avoid too many files")
    args = p.parse_args()

    out_dir = Path(args.out)
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    target_bytes = int(args.target_gb * 1024 * 1024 * 1024)
    total = 0
    i = 0

    print(f"Output: {out_dir.resolve()}")
    print(f"Target: {human(target_bytes)}")
    print(f"Each JPEG approx: {args.width}x{args.height}px at quality={args.quality} (random noise)")

    while total <= target_bytes and i < args.max_files:
        fname = out_dir / f"img_{i:03d}.jpg"

        # Generate random pixel data to avoid compressing too much
        array = np.random.randint(0, 256, (args.height, args.width, 3), dtype=np.uint8)
        img = Image.fromarray(array)
        img.save(fname, format="JPEG", quality=args.quality, optimize=False)

        size = fname.stat().st_size
        total += size
        i += 1

        if i == 1 or i % 2 == 0 or total >= target_bytes:
            print(f"Files: {i:2d}  Total: {human(total)}  Last: {fname.name} ({human(size)})")

    if total > target_bytes:
        print(f"Done. Generated {i} images totaling {human(total)}")
    else:
        print(f"Stopped at safety cap ({args.max_files} files). Total: {human(total)}")

if __name__ == "__main__":
    main()
