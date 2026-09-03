#!/usr/bin/env python3
"""Generate a small, valid, decodable Bayer DNG for use as a test fixture.

Deterministic: a fixed seed and fixed geometry, so re-running reproduces the
same bytes. Nothing photographic in it, which is the point -- it exercises the
RAW decode path without carrying anybody's licence or anybody's likeness.
"""
from pathlib import Path

import numpy as np
from pidng.core import RAW2DNG, DNGTags, Tag
from pidng.defs import CFAPattern, CalibrationIlluminant, PhotometricInterpretation

W, H = 640, 480          # even dimensions; RGGB tiles cleanly
BPP = 16
MAXV = (1 << BPP) - 1

# A scene with known structure: a vertical luminance ramp, a horizontal colour
# ramp, and a few flat patches. Enough variety that a decode which silently
# clipped, inverted or mismatched channels would show up.
y = np.linspace(0.05, 0.95, H)[:, None]
x = np.linspace(0.0, 1.0, W)[None, :]
r = np.clip(y * (0.35 + 0.65 * x), 0, 1)
g = np.clip(np.broadcast_to(y * 0.75, (H, W)), 0, 1).copy()
b = np.clip(y * (1.0 - 0.6 * x), 0, 1)

# Flat patches, so a mean is checkable by eye if this ever needs debugging.
for i, (cy, cx, val) in enumerate([(60, 60, 0.9), (60, 200, 0.5), (60, 340, 0.15)]):
    r[cy:cy + 60, cx:cx + 100] = val
    g[cy:cy + 60, cx:cx + 100] = val
    b[cy:cy + 60, cx:cx + 100] = val

rng = np.random.default_rng(20260903)
noise = rng.normal(0, 0.004, (H, W))

# Mosaic to RGGB: R at (0,0), G at (0,1) and (1,0), B at (1,1).
bayer = np.zeros((H, W), dtype=np.float64)
bayer[0::2, 0::2] = r[0::2, 0::2]
bayer[0::2, 1::2] = g[0::2, 1::2]
bayer[1::2, 0::2] = g[1::2, 0::2]
bayer[1::2, 1::2] = b[1::2, 1::2]
bayer = np.clip(bayer + noise, 0, 1)
raw = (bayer * MAXV).astype(np.uint16)

t = DNGTags()
t.set(Tag.ImageWidth, W)
t.set(Tag.ImageLength, H)
t.set(Tag.TileWidth, W)
t.set(Tag.TileLength, H)
t.set(Tag.Orientation, 1)
t.set(Tag.PhotometricInterpretation, PhotometricInterpretation.Color_Filter_Array)
t.set(Tag.SamplesPerPixel, 1)
t.set(Tag.BitsPerSample, BPP)
t.set(Tag.CFARepeatPatternDim, [2, 2])
t.set(Tag.CFAPattern, CFAPattern.RGGB)
t.set(Tag.BlackLevel, 0)
t.set(Tag.WhiteLevel, MAXV)
t.set(Tag.ColorMatrix1, [[19549, 10000], [-7877, 10000], [-2582, 10000],
                         [-5724, 10000], [10121, 10000], [1917, 10000],
                         [-1267, 10000], [-110, 10000], [6621, 10000]])
t.set(Tag.CalibrationIlluminant1, CalibrationIlluminant.D65)
t.set(Tag.AsShotNeutral, [[1, 1], [1, 1], [1, 1]])
t.set(Tag.DNGVersion, [1, 4, 0, 0])
t.set(Tag.PreviewColorSpace, 2)
# Deliberately no Make/Model/Serial/Artist: the fixture identifies no device
# and no person.

out = str(Path(__file__).resolve().parent / "synthetic-bayer-decodable")
c = RAW2DNG()
c.options(t, path="", compress=False)
c.convert(raw, filename=out)
print("written")
