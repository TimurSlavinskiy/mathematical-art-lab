#!/usr/bin/env python3
"""Render the 3 RGB equations in my_formula.py into a PNG (no AI)."""
import argparse
from pathlib import Path
import numpy as np
from PIL import Image
from my_formula import rgb


def main() -> None:
    parser = argparse.ArgumentParser(description='Turn your own RGB math formulas into a picture.')
    parser.add_argument('--size', type=int, default=1200, help='Square image dimensions in pixels')
    parser.add_argument('--output', type=Path, default=Path('my_formula.png'))
    args = parser.parse_args()
    if not 128 <= args.size <= 8000:
        parser.error('--size must be between 128 and 8000')
    grid = np.linspace(-1.15, 1.15, args.size, dtype=np.float32)
    x, y = np.meshgrid(grid, grid)
    channels = rgb(x, y)
    if len(channels) != 3:
        raise ValueError('rgb(x, y) must return exactly three arrays (red, green, blue)')
    image = np.stack(np.broadcast_arrays(*channels), axis=-1)
    pixels = np.uint8(np.clip(np.nan_to_num(image), 0, 255))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(pixels, 'RGB').save(args.output)
    print(f'Saved {args.output.resolve()} — calculated from your formulas!')


if __name__ == '__main__':
    main()
