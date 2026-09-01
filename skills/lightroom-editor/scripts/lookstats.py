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

# POLICY, both of them, for the same reason as above.
#   SKIN_MIN_SHARE     below this there is not enough warm content to read.
#   SKIN_SPREAD_LIMIT  one face under one light is a tight population. A gap
#                      wider than this between the halves of the warm
#                      distribution means more than one thing is being
#                      measured -- a face and a wooden wall, most often -- and
#                      no single skin figure describes both.
SKIN_MIN_SHARE = 0.02
SKIN_SPREAD_LIMIT = 15.0

# DERIVED, by measurement, against the gate's own tolerance.
#
# hue_range's bounds are what look-match.py FAILS presets on, so bounds that
# move between samples produce random verdicts. How far they move depends on
# how concentrated the frame's hue is -- the chroma-weighted circular resultant
# length R, which is 1.0 for a single hue and 0.0 for hue spread evenly round
# the wheel.
#
# Measured: ten independent samples of the same frame at a range of hue
# spreads, comparing the drift in the reported bounds against look-match's
# TOLERANCE of 3 degrees.
#
#     R 0.99  drift 0.00 deg      R 0.56  drift  3.75 deg
#     R 0.94  drift 0.94 deg      R 0.37  drift  4.69 deg
#     R 0.87  drift 0.94 deg      R 0.08  drift 12.19 deg
#     R 0.72  drift 2.81 deg      R 0.03  drift 58.12 deg
#
# The crossover sits between 0.56 and 0.72. This takes the conservative end:
# the lowest concentration actually proven stable. Below it hue_range returns
# None and the hue check is skipped rather than decided on noise.
HUE_CONCENTRATION_MIN = 0.72

RAW_SUFFIXES = {".arw", ".cr2", ".cr3", ".nef", ".raf", ".dng", ".rw2", ".orf"}

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
    from pathlib import Path
    p = Path(path)
    if p.suffix.lower() in RAW_SUFFIXES:
        # As Shot white balance applied, matching crs-render.py exactly. That
        # is the state Lightroom opens the file in, and every slider value
        # this skill emits is relative to it, so a cast measured here is the
        # residual the user actually sees rather than the sensor's raw
        # imbalance -- which is dominated by the illuminant, not the camera.
        import rawpy
        with rawpy.imread(str(p)) as raw:
            rgb = raw.postprocess(gamma=(1, 1), no_auto_bright=True,
                                  output_bps=16, use_camera_wb=True)
        a = linear_to_srgb(rgb.astype(np.float64) / 65535.0).reshape(-1, 3)
    else:
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


def hue_concentration(rgb):
    """How concentrated this frame's hue is: 1.0 one hue, 0.0 spread evenly.

    The chroma-weighted circular resultant length. It answers whether "the
    hue of this image" is a thing that exists before anything tries to
    measure it.
    """
    c, h = _coloured(rgb)
    if c.size == 0:
        return 0.0
    x = float((c * np.cos(np.radians(h))).sum())
    y = float((c * np.sin(np.radians(h))).sum())
    return float(np.hypot(x, y) / c.sum())


def hue_range(rgb, lo_pct=10.0, hi_pct=90.0, min_concentration=HUE_CONCENTRATION_MIN):
    """Chroma-weighted 10th-90th percentile of hue, in RGB-wheel degrees.

    The distribution is rotated so its circular mean sits at 180 before the
    percentiles are taken, then rotated back. Without that, a red reference
    spanning 350-10 degrees would be split across the wrap and measured as
    covering the entire wheel.

    Returns None when the frame's hue is too spread out for a range to mean
    anything. The bounds this returns are what look-match.py fails presets on,
    and on a frame with no dominant hue they move by tens of degrees depending
    on which pixels are sampled -- so the honest answer there is that this
    image does not have a hue range, not a pair of numbers that will not
    reproduce.
    """
    c, h = _coloured(rgb)
    if c.size == 0 or hue_concentration(rgb) < min_concentration:
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


# Published ITA classification (Del Bino & Bernerd), used only to name the
# number this module measures. The boundaries are theirs, not ours.
ITA_CLASSES = [(55.0, "very light"), (41.0, "light"), (28.0, "intermediate"),
               (10.0, "tan"), (-30.0, "brown")]


def ita_class(angle):
    for edge, name in ITA_CLASSES:
        if angle > edge:
            return name
    return "dark"


def skin(rgb, min_share=SKIN_MIN_SHARE, spread_limit=SKIN_SPREAD_LIMIT):
    """Skin tone of the warm population in this frame, or a refusal and why.

    There is no face detector here, so nothing in this module can say which
    pixels are a face. What it can say is whether the frame contains ONE warm
    population tight enough that a single skin reading would mean something.
    A portrait against a wooden wall contains two, and terracotta, sand and
    bare wood all sit where skin sits; in those frames this returns a refusal
    rather than a number, and the caller should look at the picture instead.

    Only run this where the Subject gate has already settled on a portrait.
    Nothing below can tell a face from a sand dune.
    """
    lab = rgb_to_lab(rgb)
    L, a, b = lab[..., 0], lab[..., 1], lab[..., 2]
    # All six published ITA classes sit at positive a* and positive b*: skin
    # is warm. This admits wood and sand too, which is why the tests below it
    # matter more than the test above it.
    warm = (a > 0) & (b > 0) & (L >= L_FLOOR) & (chroma(lab) >= CHROMA_FLOOR)
    share = float(np.count_nonzero(warm)) / rgb.shape[0]
    if share < min_share:
        return {"ok": False, "share": share,
                "reason": f"warm content is {share * 100:.1f}% of the frame — "
                          "too little to read a skin tone from"}
    h = np.degrees(np.arctan2(b[warm], a[warm]))
    # Split at the median and compare the halves. One face under one light is
    # a single tight population; a face plus a wooden wall is two, and the gap
    # between the halves is what shows it.
    med = float(np.median(h))
    lo, hi = h[h <= med], h[h > med]
    gap = abs(float(hi.mean()) - float(lo.mean())) if lo.size and hi.size else 0.0
    if gap > spread_limit:
        return {"ok": False, "share": share, "spread": gap,
                "reason": f"two warm populations {gap:.0f} deg apart (spread "
                          f"limit {spread_limit:.0f} deg) — cannot tell skin "
                          "from surround by colour alone"}
    mL, mb = float(L[warm].mean()), float(b[warm].mean())
    angle = ita(mL, mb)
    return {"ok": True, "share": share, "spread": gap, "ita": angle,
            "ita_class": ita_class(angle), "L": mL,
            "a": float(a[warm].mean()), "b": mb}


def probe_tint(crs, lin, step=10.0, rounds=5, settle=0.05):
    """Tint units that undo this file's measured a* cast, measured off THIS file.

    Adobe publishes no mapping from CIELAB chroma to a Tint unit, so none is
    assumed. The renderer is asked instead: move Tint by a known step, see how
    far a* actually travels on this image, and invert that.

    One step is not enough. Tint acts as channel gains, so its effect on a* is
    not linear across the range, and a single secant lands roughly two thirds
    of the way. So the probe repeats from the accumulated value until the
    residual settles, always rendering from the original file rather than
    stacking renders, since the renderer's moves do not compose.

    The answer is our renderer's Tint, not Adobe's, and it is only as good as
    crs-render.py -- which models Tint as channel gains around the file's own
    white balance and says plainly that it approximates Camera Raw rather than
    reproducing it.
    """
    def cast_at(t):
        x = crs.render(lin, {"IncrementalTint": t}) if t else lin
        c = measure_cast(crs.linear_to_srgb(x).reshape(-1, 3))
        return None if c is None else c["a"]

    total = 0.0
    for _ in range(rounds):
        base = cast_at(total)
        if base is None or abs(base) < settle:
            break
        moved = cast_at(total + step)
        if moved is None or abs(moved - base) < 1e-9:
            break
        total += -base * step / (moved - base)
    return total
