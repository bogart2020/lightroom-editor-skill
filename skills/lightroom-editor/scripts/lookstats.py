#!/usr/bin/env python3
"""Measure what a photograph's colour actually is. One implementation, shared.

This is the measurement core behind `look-match.py` (the reference gate) and
`look-analyze.py` (the report). It measures; it does not decide. Every figure
it returns is either a published quantity (CIE L*a*b*, ITA) or a share of the
image's own colour, and every threshold below is *derived* from a stated
definition rather than chosen to make a case pass.

Two spaces, deliberately, because they answer different questions:

  RGB-wheel hue   the angle Lightroom's own controls speak. `crs:...Hue`
                  attributes and the eight Color Mix bands are degrees on the
                  RGB/HSL wheel, so a hue compared against a slider value must
                  be measured on that wheel. Converting it to Lab hue angle
                  would compare two different angular spaces.

  CIE L*a*b*      everything perceptual: how much colour a pixel carries
                  (chroma), which way a cast leans, where the black point
                  sits, skin tone angle. Lab is uniform enough for these to
                  mean something; HSV is not.

The predecessor of this module weighted colour by HSV saturation, which is
coupled to brightness — a dark navy and a bright orange of the same nominal
"saturation" counted equally, which is wrong, and wrong hardest on the muted
looks `references/08-looks.md` cares most about. Weight is Lab chroma here.
"""
import numpy as np

# --------------------------------------------------------------- constants
# sRGB (IEC 61966-2-1) primaries to CIE XYZ, D65 white, 2 degree observer.
SRGB_TO_XYZ = np.array([
    [0.4124564, 0.3575761, 0.1804375],
    [0.2126729, 0.7151522, 0.0721750],
    [0.0193339, 0.1191920, 0.9503041],
])
# D65 reference white, the same illuminant the matrix above is built for.
D65 = np.array([0.95047, 1.00000, 1.08883])

# The eight Color Mix bands, at their RGB-wheel centres. These are Lightroom's
# own band names and positions, not a choice made here.
BANDS = [("Red", 0), ("Orange", 30), ("Yellow", 60), ("Green", 120),
         ("Aqua", 180), ("Blue", 240), ("Purple", 270), ("Magenta", 300)]

# Below these, a pixel carries no hue worth counting.
#
# Both are the OLD thresholds' intent expressed in the new units, so the gate
# keeps its meaning while the measurement improves. They are derived, not
# picked: `derive_floors()` recomputes them from the definitions below, and
# the regression suite asserts these literals still match what it returns.
#
#   CHROMA_FLOOR  the Lab chroma of an HSV S=0.10 colour at V=0.50, averaged
#                 over the hue circle. HSV S=0.10 was the predecessor's
#                 "near-neutral, carries no hue" line.
#   L_FLOOR       the CIE lightness of sRGB 0.10 grey. HSV V=0.10 was the
#                 predecessor's "near-black, carries no hue" line.
CHROMA_FLOOR = 6.5589
L_FLOOR = 9.0104

# POLICY, not derived — stated here so it is argued with rather than trusted.
# A near-neutral population smaller than this cannot be assumed to stand for
# the frame's neutrals; it is as likely to be one small object. Below it the
# cast is refused rather than guessed. Nothing derives this number: it is a
# judgement about how much of a frame has to agree before a reading means
# anything, and it is the first thing to revisit against real photographs.
NEUTRAL_MIN_SHARE = 0.02

ZONES = 9


# ------------------------------------------------------------------ colour
def srgb_to_linear(a):
    """Undo the sRGB transfer function. IEC 61966-2-1."""
    return np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)


def linear_to_srgb(a):
    a = np.clip(a, 0.0, 1.0)
    return np.where(a <= 0.0031308, a * 12.92, 1.055 * a ** (1 / 2.4) - 0.055)


def rgb_to_lab(rgb):
    """sRGB-encoded float in [0,1], shape (...,3), to CIE L*a*b* (D65, 2 deg).

    Verified against the published CIELAB values for the sRGB primaries; see
    PUBLISHED_LAB in tests/test_skill.py.
    """
    xyz = srgb_to_linear(np.asarray(rgb, dtype=np.float64)) @ SRGB_TO_XYZ.T
    t = xyz / D65
    # CIE 15 piecewise: cube root above the linear toe, straight line below,
    # meeting at t = (6/29)^3 so the function and its slope stay continuous.
    d = 6.0 / 29.0
    f = np.where(t > d ** 3, np.cbrt(t), t / (3 * d ** 2) + 4.0 / 29.0)
    return np.stack([116.0 * f[..., 1] - 16.0,
                     500.0 * (f[..., 0] - f[..., 1]),
                     200.0 * (f[..., 1] - f[..., 2])], axis=-1)


def chroma(lab):
    """C* — how much colour a pixel carries, independent of how bright it is."""
    return np.hypot(lab[..., 1], lab[..., 2])


def wheel_hue(rgb):
    """Hue in degrees on the RGB/HSL wheel — the wheel Lightroom's sliders use.

    Same definition as colorsys.rgb_to_hsv, vectorised. Kept on this wheel so
    the result is directly comparable with `crs:...Hue` attributes and with
    the Color Mix band centres.
    """
    rgb = np.asarray(rgb, dtype=np.float64)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    mx, mn = rgb.max(axis=-1), rgb.min(axis=-1)
    d = mx - mn
    safe = np.where(d == 0, 1.0, d)
    h = np.where(mx == r, (g - b) / safe % 6.0,
        np.where(mx == g, (b - r) / safe + 2.0,
                          (r - g) / safe + 4.0))
    return np.where(d == 0, 0.0, h * 60.0) % 360.0


def derive_floors():
    """Recompute CHROMA_FLOOR and L_FLOOR from their stated definitions.

    Exists so the constants above can be proven rather than trusted. The
    regression suite calls this and asserts the literals still match.
    """
    import colorsys
    hues = np.arange(360)
    patches = np.array([colorsys.hsv_to_rgb(h / 360.0, 0.10, 0.50) for h in hues])
    c = float(chroma(rgb_to_lab(patches)).mean())
    l = float(rgb_to_lab(np.array([(0.10, 0.10, 0.10)]))[0, 0])
    return c, l


# ----------------------------------------------------------------- sampling
def load_rgb(path, max_pixels=1_000_000, seed=0):
    """Return an unbiased sample of the image's pixels as sRGB float (N,3).

    A measurement needs a fair sample of the colours in the file, not a
    resized picture. Every resampling filter that averages neighbouring
    pixels — Pillow's default BICUBIC included — blends across hard colour
    edges and manufactures hues the file never contained: two-pixel red and
    blue stripes average to magenta. So an oversized image is subsampled by
    drawing pixels at random, seeded so the result is reproducible.
    """
    from PIL import Image
    im = Image.open(path).convert("RGB")
    a = np.asarray(im, dtype=np.float64).reshape(-1, 3) / 255.0
    if a.shape[0] > max_pixels:
        idx = np.random.default_rng(seed).choice(a.shape[0], max_pixels, replace=False)
        a = a[idx]
    return a


# ------------------------------------------------------------- measurement
def band_profile(rgb):
    """Share of the image's colour carried by each Color Mix band, in percent.

    Weighted by Lab chroma: a band's share is the fraction of the image's
    total colourfulness that sits in it, so a large dull region cannot
    outvote a small vivid one the way an area count would.
    """
    lab = rgb_to_lab(rgb)
    c, l, h = chroma(lab), lab[..., 0], wheel_hue(rgb)
    keep = (c >= CHROMA_FLOOR) & (l >= L_FLOOR)
    c, h = c[keep], h[keep]
    total = c.sum()
    if total == 0:
        return {n: 0.0 for n, _ in BANDS}
    centres = np.array([deg for _, deg in BANDS], dtype=np.float64)
    d = np.abs(h[:, None] - centres[None, :])
    nearest = np.minimum(d, 360.0 - d).argmin(axis=1)
    return {n: float(100.0 * c[nearest == i].sum() / total)
            for i, (n, _) in enumerate(BANDS)}


def hue_mean(h, w):
    """Chroma-weighted circular mean of hue, in degrees.

    Circular because hue wraps: the ordinary mean of 350 and 10 degrees is
    180, the opposite colour.
    """
    x = float((w * np.cos(np.radians(h))).sum())
    y = float((w * np.sin(np.radians(h))).sum())
    return float(np.degrees(np.arctan2(y, x)) % 360.0)


def _coloured(rgb):
    """Pixels carrying hue worth measuring, with their chroma and wheel hue."""
    lab = rgb_to_lab(rgb)
    c, l, h = chroma(lab), lab[..., 0], wheel_hue(rgb)
    keep = (c >= CHROMA_FLOOR) & (l >= L_FLOOR)
    return c[keep], h[keep]


def hue_range(rgb, lo_pct=10.0, hi_pct=90.0):
    """Chroma-weighted 10th-90th percentile of hue, in RGB-wheel degrees.

    The distribution is rotated so its circular mean sits at 180 before the
    percentiles are taken, then rotated back. Without that, a red reference
    spanning 350-10 degrees would be split across the wrap and measured as
    covering the entire wheel.
    """
    c, h = _coloured(rgb)
    if c.size == 0:
        return None
    m = hue_mean(h, c)
    rel = (h - m + 180.0) % 360.0
    order = np.argsort(rel)
    rel, w = rel[order], c[order]
    cum = np.cumsum(w) / w.sum()
    pick = lambda p: float(rel[min(int(np.searchsorted(cum, p / 100.0)), rel.size - 1)])
    return ((pick(lo_pct) + m - 180.0) % 360.0,
            (pick(hi_pct) + m - 180.0) % 360.0)


def frame_hue_mean(rgb):
    """This frame's own dominant hue, in RGB-wheel degrees, or None.

    Used to tell whether a set of reference frames is one look or several:
    frames from different shoots average into a range that describes none of
    them.
    """
    c, h = _coloured(rgb)
    return hue_mean(h, c) if c.size else None


def measure_cast(rgb, min_share=NEUTRAL_MIN_SHARE):
    """The colour of the things in this frame that ought to be grey.

    Returns None rather than a number when the frame does not contain enough
    near-neutral content to say. A forest is not a green cast, and gray-world
    -- averaging the whole frame -- cannot tell the difference. So instead of
    assuming the average is neutral, this finds the densest low-chroma cluster
    by mean shift on the a*/b* plane and reports where it actually sits.

    The search is seeded from the least colourful tenth of the frame rather
    than from the origin, so a strong cast is still found: seeding at zero
    would abstain precisely when the cast is worst.
    """
    lab = rgb_to_lab(rgb)
    lit = lab[..., 0] >= L_FLOOR      # near-black chroma is unreliable
    a, b = lab[..., 1][lit], lab[..., 2][lit]
    if a.size == 0:
        return None
    c = np.hypot(a, b)
    seed = c <= np.percentile(c, 10.0)
    ca, cb = float(a[seed].mean()), float(b[seed].mean())
    for _ in range(12):
        sel = np.hypot(a - ca, b - cb) < CHROMA_FLOOR
        if not sel.any():
            return None
        na, nb = float(a[sel].mean()), float(b[sel].mean())
        if abs(na - ca) < 1e-4 and abs(nb - cb) < 1e-4:
            ca, cb = na, nb
            break
        ca, cb = na, nb
    # The cluster is only a CAST if it is itself near neutral. Seeding from
    # the least colourful tenth finds a cluster in every frame, including one
    # that is uniformly red -- there the least colourful tenth is still vivid
    # red, and calling that a cast is the gray-world mistake in disguise.
    # CHROMA_FLOOR is already the line below which a pixel carries no hue
    # worth counting, so a centre above it is a colour, not a cast.
    #
    # The stated limit that follows: a residual cast stronger than
    # CHROMA_FLOOR cannot be distinguished from subject colour by this
    # method, and is refused rather than guessed at. The camera profile
    # covers that case, labelled as unmeasured.
    if np.hypot(ca, cb) >= CHROMA_FLOOR:
        return None
    share = float(np.count_nonzero(np.hypot(a - ca, b - cb) < CHROMA_FLOOR)) / rgb.shape[0]
    if share < min_share:
        return None
    return {"a": ca, "b": cb, "neutral_fraction": share}


def black_point(rgb, pct=0.1):
    """Where the blacks actually sit, as relative luminance in linear light.

    The darkest tenth of a percent is skipped: a handful of dead pixels or a
    speck of true black would otherwise report a black point of zero for an
    image whose shadows are plainly lifted.
    """
    lin = srgb_to_linear(np.asarray(rgb, dtype=np.float64))
    return float(np.percentile(lin @ SRGB_TO_XYZ[1], pct))


def zones(rgb, n=ZONES):
    """Mean colour of each tonal zone, bucketed by L*.

    Zones rather than pixels because a grade is a function of tone: what the
    shadows are doing is a different question from what the highlights are
    doing, and a whole-frame average answers neither.
    """
    lab = rgb_to_lab(rgb)
    L = lab[..., 0]
    idx = np.clip((L / 100.0 * n).astype(int), 0, n - 1)
    total = L.size
    out = []
    for i in range(n):
        m = idx == i
        k = int(m.sum())
        out.append({
            "zone": i,
            "L": float(L[m].mean()) if k else 0.0,
            "a": float(lab[..., 1][m].mean()) if k else 0.0,
            "b": float(lab[..., 2][m].mean()) if k else 0.0,
            "share": k / total,
        })
    return out


def ita(L, b):
    """Individual Typology Angle, in degrees: arctan((L* - 50) / b*).

    The published skin-tone metric (Chardon et al.). Higher is lighter.
    """
    return float(np.degrees(np.arctan2(np.asarray(L) - 50.0, np.asarray(b))))
