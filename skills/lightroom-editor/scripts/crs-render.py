#!/usr/bin/env python3
"""Render the modellable part of a Lightroom preset onto a photo.

This is an APPROXIMATION of Camera Raw, not a reproduction of it. Adobe's
published DNG SDK implements none of the PV2012 develop pipeline, and the math
behind Clarity, Texture, Dehaze and Color Grading is unpublished. So this
renderer deliberately models only the controls whose behaviour is derivable
from the DNG specification and Adobe's own rendering code:

    IncrementalTemperature   channel gains around the file's own white balance
    IncrementalTint          channel gains around the file's own white balance
    Exposure2012             multiplicative gain in linear light, soft-clipped
    Blacks2012 / Whites2012  endpoint remap
    ToneCurvePV2012          the preset carries the control points; we interpolate

Every other crs: attribute is IGNORED here and reported as unmodelled. A score
computed from this renderer says "agrees with our renderer", never "matches
Lightroom".

Usage:
  scripts/crs-render.py SOURCE.{ARW,CR3,NEF,DNG,jpg,png} PRESET.xmp -o OUT.png
"""
import argparse, sys, xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np

CRS = "http://ns.adobe.com/camera-raw-settings/1.0/"

# The only attributes this renderer models. Anything else in the preset is
# carried by the recipe but not represented in the pixels.
MODELLED = ("IncrementalTemperature", "IncrementalTint", "Exposure2012",
            "Blacks2012", "Whites2012", "ToneCurvePV2012")

RAW_SUFFIXES = {".arw", ".cr2", ".cr3", ".nef", ".raf", ".dng", ".rw2", ".orf"}


# ------------------------------------------------------------------ colour
def srgb_to_linear(a):
    return np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)


def linear_to_srgb(a):
    a = np.clip(a, 0.0, 1.0)
    return np.where(a <= 0.0031308, a * 12.92, 1.055 * a ** (1 / 2.4) - 0.055)


# ------------------------------------------------------------------ loading
def load_image(path):
    """Return (linear float RGB in [0,1], depth label).

    RAW is decoded to linear by LibRaw, which is the data Lightroom grades.
    An 8-bit file is only un-gamma'd — that undoes the sRGB transfer function,
    it does not invent headroom the file never had. The label travels with the
    score so nobody reads an 8-bit result as a RAW one.
    """
    p = Path(path)
    if p.suffix.lower() in RAW_SUFFIXES:
        try:
            import rawpy
        except ImportError:
            sys.exit("rawpy is needed to decode RAW — pip install -r tests/requirements.txt")
        try:
            with rawpy.imread(str(p)) as raw:
                rgb = raw.postprocess(gamma=(1, 1), no_auto_bright=True,
                                      output_bps=16, use_camera_wb=True)
            return rgb.astype(np.float64) / 65535.0, "RAW, linear"
        except rawpy.LibRawError:
            # LibRaw opened it and then refused to unpack it — current iPhone
            # ProRAW (DNG 1.7 / JPEG-XL) needs Adobe's DNG SDK, which the
            # rawpy wheel is not built with. Fall back to the camera's
            # embedded preview, exactly as lookstats.load_source does; the two
            # must stay in step or a Tint probed here is measured against a
            # different image than the cast it corrects. See
            # research/06-proraw-dng-decode.md.
            import io
            from PIL import Image
            with rawpy.imread(str(p)) as raw:
                thumb = raw.extract_thumb()
            if thumb.format == rawpy.ThumbFormat.JPEG:
                im = Image.open(io.BytesIO(thumb.data)).convert("RGB")
                a = np.asarray(im, dtype=np.float64) / 255.0
            else:
                a = np.asarray(thumb.data, dtype=np.float64)[..., :3] / 255.0
            return srgb_to_linear(a), "RAW preview, already rendered"

    from PIL import Image
    im = Image.open(p).convert("RGB")
    a = np.asarray(im, dtype=np.float64) / 255.0
    return srgb_to_linear(a), "8-bit, recovery headroom not represented"


# ------------------------------------------------------------------ preset
def parse_settings(xmp_path):
    """Pull the modelled attributes out of a .xmp. Returns floats and a curve."""
    root = ET.fromstring(Path(xmp_path).read_text())
    s, curve = {}, None
    for el in root.iter():
        for k, v in el.attrib.items():
            if k.startswith(f"{{{CRS}}}"):
                s[k.split("}")[1]] = v
        if el.tag == f"{{{CRS}}}ToneCurvePV2012":
            pts = [li.text for li in el.iter() if li.text and "," in li.text]
            curve = [tuple(float(n) for n in t.split(",")) for t in pts]
    out = {k: float(s[k]) for k in MODELLED if k in s and k != "ToneCurvePV2012"}
    if curve:
        out["ToneCurvePV2012"] = curve
    return out, s


def moved_sliders(all_attrs):
    """Every slider the preset actually moves, split into modelled and not.

    Coverage is reported from this: a high score across two of eleven moved
    sliders is not a verified preset.
    """
    skip = {"PresetType", "UUID", "HasSettings", "ToneCurveName2012",
            "SupportsAmount", "SupportsColor", "SupportsMonochrome",
            "SupportsHighDynamicRange", "SupportsNormalDynamicRange",
            "SupportsSceneReferred", "SupportsOutputReferred", "Version",
            "ProcessVersion", "Name", "ShortName", "SortName", "Group",
            "Cluster", "ClusterGroup"}
    moved = []
    for k, v in all_attrs.items():
        if k in skip:
            continue
        try:
            if float(v) == 0:
                continue
        except ValueError:
            pass
        moved.append(k)
    modelled = [k for k in moved if k in MODELLED]
    return moved, modelled


# ------------------------------------------------------------------ render
def _soft_clip(x, knee=0.8):
    """Monotone highlight rolloff, C1-continuous at the knee, asymptotic to 1."""
    hi = 1.0 - (1.0 - knee) * np.exp(-(x - knee) / (1.0 - knee))
    return np.where(x <= knee, x, hi)


def render(lin, s):
    """Apply the modelled settings, in the skill's own pipeline order."""
    img = np.clip(lin, 0.0, None).astype(np.float64)

    # 1. white balance — channel gains around the file's own as-shot balance.
    t = s.get("IncrementalTemperature", 0.0) / 100.0   # + is warmer
    g = s.get("IncrementalTint", 0.0) / 100.0          # + is toward magenta
    img = img * np.array([1.0 + 0.30 * t, 1.0 - 0.20 * g, 1.0 - 0.30 * t])

    # 2. exposure — multiplicative in linear light, with a highlight rolloff.
    ev = s.get("Exposure2012", 0.0)
    if ev:
        img = img * (2.0 ** ev)
    img = _soft_clip(np.clip(img, 0.0, None))

    # everything below is an encoded-domain operation, as in Camera Raw.
    enc = linear_to_srgb(img)

    # 3. endpoints.
    b = s.get("Blacks2012", 0.0)
    if b > 0:                                  # lift the floor
        floor = b * 0.0012
        enc = floor + (1.0 - floor) * enc
    elif b < 0:                                # pull the floor down
        pivot = -b * 0.0012
        enc = np.clip((enc - pivot) / (1.0 - pivot), 0.0, 1.0)
    w = s.get("Whites2012", 0.0)
    if w:
        enc = np.clip(enc * (1.0 + w * 0.0015), 0.0, 1.0)

    # 4. tone curve — the preset carries the control points, so this is the one
    #    control that is literally specified rather than inferred. Piecewise
    #    linear through the points: monotone by construction, and honest about
    #    not being Adobe's spline.
    pts = s.get("ToneCurvePV2012")
    if pts:
        p = sorted(pts)
        xs = np.array([q[0] for q in p]) / 255.0
        ys = np.array([q[1] for q in p]) / 255.0
        enc = np.interp(enc, xs, ys)

    return np.clip(enc, 0.0, 1.0)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source")
    ap.add_argument("preset")
    ap.add_argument("-o", "--out", required=True)
    a = ap.parse_args()

    lin, depth = load_image(a.source)
    settings, all_attrs = parse_settings(a.preset)
    enc = render(lin, settings)

    from PIL import Image
    Image.fromarray((enc * 255).round().astype(np.uint8)).save(a.out)

    moved, modelled = moved_sliders(all_attrs)
    print(f"rendered {a.source} ({depth}) -> {a.out}")
    print(f"modelled {len(modelled)} of {len(moved)} moved sliders: "
          f"{', '.join(modelled) or 'none'}")
    unmodelled = [m for m in moved if m not in modelled]
    if unmodelled:
        print(f"NOT modelled, NOT represented in these pixels: "
              f"{', '.join(unmodelled)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
