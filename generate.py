#!/usr/bin/env python3
"""HORIZON: deterministic mathematical space art, rendered pixel-by-pixel.

Not a physically accurate general-relativity simulation. No AI or stock imagery.
Requires: numpy, pillow. Usage: python generate.py --output artwork.png
"""
from __future__ import annotations

import argparse
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter


def smooth_noise(width: int, height: int, gx: int, gy: int, rng: np.random.Generator) -> np.ndarray:
    """Continuous noise from bilinear/cubic interpolation of a random lattice."""
    base = rng.random((gy, gx), dtype=np.float32)
    image = Image.fromarray(np.uint8(np.round(base * 255)), mode="L")
    resized = image.resize((width, height), Image.Resampling.BICUBIC)
    return np.asarray(resized, dtype=np.float32) / 255


def layer(img: np.ndarray, color: tuple[float, float, float], intensity: np.ndarray) -> None:
    for channel in range(3):
        img[..., channel] += intensity * color[channel]


def glow_star_overlay(width: int, height: int, rng: np.random.Generator) -> Image.Image:
    stars = Image.new("RGB", (width, height), (0, 0, 0))
    draw = ImageDraw.Draw(stars)
    count = max(600, int(width * height / 580))
    for _ in range(count):
        px, py = int(rng.integers(width)), int(rng.integers(height))
        rank = rng.random()
        if rank < 0.86:
            brightness, radius = int(rng.integers(28, 126)), 0
        elif rank < 0.985:
            brightness, radius = int(rng.integers(100, 235)), 1
        else:
            brightness, radius = int(rng.integers(180, 256)), int(rng.choice([2, 3]))
        col = (int(brightness * rng.uniform(.75, 1)), int(brightness * rng.uniform(.85, 1)), brightness)
        draw.ellipse((px-radius, py-radius, px+radius, py+radius), fill=col)
        if radius >= 3 and rng.random() < .35:
            draw.line((px-9, py, px+9, py), fill=(95, 111, 148), width=1)
            draw.line((px, py-9, px, py+9), fill=(95, 111, 148), width=1)
    return stars


def render(width: int, height: int, seed: int) -> Image.Image:
    rng = np.random.default_rng(seed)
    # Coordinates are normalized so the same formulas work at any resolution.
    yy, xx = np.mgrid[:height, :width].astype(np.float32)
    u, v = xx / width, yy / height
    scale = min(width, height) * .37
    x = (xx - width * .50) / scale
    y = (yy - height * .515) / scale
    radius = np.sqrt(x*x + y*y)
    angle = np.arctan2(y, x)

    # Deep-space background: multiple continuous random fields, sinusoidal wisps,
    # and Gaussian cloud envelopes. All pixels are calculated, not painted.
    low = smooth_noise(width, height, 16, 10, rng)
    mid = smooth_noise(width, height, 49, 31, rng)
    fine = smooth_noise(width, height, 140, 88, rng)
    clouds = np.clip(.58*low + .32*mid + .1*fine, 0, 1)
    waves = .54 + .46*np.sin(17*u + 9*v + 4.0*low + 2.8*np.sin(8*v - 7*u))
    cloudshape1 = np.exp(-(((u-.27)/.29)**2 + ((v-.43)/.45)**2)*1.3)
    cloudshape2 = np.exp(-(((u-.80)/.37)**2 + ((v-.74)/.37)**2)*1.4)
    cloudshape3 = np.exp(-(((u-.70)/.36)**2 + ((v-.15)/.28)**2)*1.7)
    img = np.zeros((height, width, 3), dtype=np.float32)
    img[...] = (2.5, 4.5, 13.5)
    layer(img, (36, 19, 71), 2.1 * cloudshape1 * clouds * waves)
    layer(img, (10, 50, 93), 1.7 * cloudshape2 * clouds * (1-waves*.6))
    layer(img, (45, 14, 63), 1.1 * cloudshape3 * (clouds**2))
    # Subtle thin filament-like structures in the background.
    tendrils = np.power(np.maximum(0, np.cos(36*v + 7*np.sin(9*u+4*low) + 15*u)), 18)
    layer(img, (12, 18, 35), cloudshape1 * tendrils)

    # A tilted accretion disk. The sum of radial Gaussian profiles makes bands;
    # sinusoids (with a nonuniform angular phase) produce turbulent filaments.
    ellipticity = .265
    r_disk = np.sqrt(x*x + (y/ellipticity)**2)
    theta_disk = np.arctan2(y / ellipticity, x)
    spiral_phase = 58*theta_disk - 25*r_disk + 9*np.sin(6*theta_disk + r_disk*8)
    turbulence = (
        .78 + .18*np.sin(spiral_phase) + .12*np.sin(spiral_phase*2.09+3*r_disk)
        + .10*np.cos(151*theta_disk-71*r_disk)
    )
    beam = 1 + .60*np.clip(-x/(r_disk+1e-6), -1, 1)
    outer = np.exp(-((r_disk-1.27)/.46)**2)
    inner = np.exp(-((r_disk-.77)/.23)**2)
    disk_density = np.maximum(0, (1.00*outer + .65*inner)*turbulence*beam)
    # Accretion disk runs behind the silhouette; the foreground becomes brighter.
    density = disk_density * np.clip((r_disk-.58)/.16, 0, 1)
    layer(img, (93, 23, 42), density * .29)
    layer(img, (239, 63, 23), density * .62)
    layer(img, (255, 155, 52), density * .37 * np.exp(-((r_disk-.93)/.39)**2))
    hot = density * np.exp(-((r_disk-.82)/.22)**2)
    layer(img, (255, 232, 173), hot * .42)

    # Refracted-looking halo and an Einstein-ring-inspired photon arc.
    # These are artistic approximations, NOT solved geodesics.
    halo = np.exp(-((radius-.56)/.18)**2)
    ring = np.exp(-((radius-(.448+.015*np.sin(3*angle)))/.019)**2)
    thin_ring = np.exp(-((radius-.513)/.018)**2)
    backlight = .7 + .3*np.maximum(0, -y/(radius+1e-5))
    layer(img, (130, 51, 35), .23*halo)
    layer(img, (255, 132, 51), .70*ring*backlight)
    layer(img, (255, 207, 105), .47*thin_ring*backlight)
    layer(img, (255, 237, 192), .25*np.exp(-((radius-.458)/.006)**2))

    # Event-horizon-like shadow, with a very dark interior and a soft edge.
    # Smoothness eliminates jagged pixel boundaries at all render sizes.
    shadow = np.clip((radius-.433)/.032, 0, 1)
    smooth_shadow = shadow*shadow*(3-2*shadow)
    img *= smooth_shadow[..., None]
    # Delicate inner rim just beyond the dark edge.
    inner_rim = np.exp(-((radius-.477)/.013)**2)
    layer(img, (244, 133, 62), inner_rim*.28)

    # Additive bloom is calculated from the rendered light sources; it gives
    # the image a photographic glow, without replacing the mathematical render.
    hdr = np.uint8(np.clip(img, 0, 255))
    core = Image.fromarray(hdr, 'RGB')
    bloom = core.filter(ImageFilter.GaussianBlur(max(8, width//110)))
    bloom_arr = np.asarray(bloom, dtype=np.float32)
    result = np.clip(img * .95 + bloom_arr * .27, 0, 255).astype(np.uint8)
    final = Image.fromarray(result, 'RGB')

    # Seeded point lights: stars are mathematical positions, circles and lines.
    # Add stars after the opaque black silhouette, masking those behind it.
    stars = glow_star_overlay(width, height, rng)
    star_arr = np.array(stars, dtype=np.uint8, copy=True)
    silhouette = radius < .44
    star_arr[silhouette] = 0
    background_stars = Image.fromarray(star_arr)
    stars_glow = background_stars.filter(ImageFilter.GaussianBlur(max(1, width//350)))
    final = Image.fromarray(np.uint8(np.clip(
        np.asarray(final, dtype=np.float32)
        + np.asarray(background_stars, dtype=np.float32)*.85
        + np.asarray(stars_glow, dtype=np.float32)*.30,
        0, 255)))
    return final


def main() -> None:
    parser = argparse.ArgumentParser(description='Render mathematical space art to PNG (no AI).')
    parser.add_argument('--width', type=int, default=1600, help='Image width in pixels')
    parser.add_argument('--height', type=int, default=1000, help='Image height in pixels')
    parser.add_argument('--seed', type=int, default=27, help='Reproducible random seed')
    parser.add_argument('--output', type=Path, default=Path('horizon.png'))
    args = parser.parse_args()
    if not (320 <= args.width <= 8000 and 240 <= args.height <= 8000):
        parser.error('Choose width 320..8000 and height 240..8000')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    render(args.width, args.height, args.seed).save(args.output, optimize=True)
    print(f'Saved: {args.output.resolve()} ({args.width} x {args.height}; seed={args.seed})')


if __name__ == '__main__':
    main()
