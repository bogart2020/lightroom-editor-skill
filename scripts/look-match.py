#!/usr/bin/env python3
"""Does this preset grade the colour the reference is actually made of?

Two checks, both measured off the reference image rather than assumed:

  bands  — RED when a preset spends hard Color Mix moves on hue bands that
           carry almost none of the reference's colour, or leaves the
           reference's dominant band untouched.
  hues   — RED when a Color Grading hue sits outside the reference's own
           hue range. A golden-hour reference measures ~35-48 deg; grading
           its shadows at 30 deg lands orange, not gold, and Balance
           negative weights that shadow hue hardest.

The reference set must be ONE look. Frames from different shoots or grades
average into a range that describes nothing; the gate refuses a set whose
frames disagree by more than SPREAD_LIMIT degrees rather than silently
averaging them.

When the user wants the reference's family but not its exact temperature,
state the deviation with --warmer/--cooler so the gate checks intent rather
than fidelity. Record the number next to the preset; it is not recoverable
from the files afterwards.

Usage:
  scripts/look-match.py REFERENCE.jpg [MORE.jpg ...] PRESET.xmp
  scripts/look-match.py --warmer 8 REF.jpg PRESET.xmp
"""
import collections, colorsys, math, os, re, sys, xml.etree.ElementTree as ET
from PIL import Image

CRS = "http://ns.adobe.com/camera-raw-settings/1.0/"
BANDS = [("Red", 0), ("Orange", 30), ("Yellow", 60), ("Green", 120),
         ("Aqua", 180), ("Blue", 240), ("Purple", 270), ("Magenta", 300)]
DOMINANT = 25.0     # a band carrying >= this much of the colour must be addressed
NEGLIGIBLE = 5.0    # a band carrying <= this much should not be pushed hard
HARD = 20           # |value| above this counts as a hard push
SPREAD_LIMIT = 12   # max degrees the reference frames' means may differ by
TOLERANCE = 3       # degrees a grading hue may sit outside the range


def _hue_samples(path):
    im = Image.open(path).convert("RGB").resize((200, 200))
    out = []
    for r, g, b in im.getdata():
        h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        if s < 0.10 or v < 0.10:
            continue
        out.append((h * 360, s))
    return out


def _pct_range(samples):
    """Saturation-weighted 10th-90th percentile of hue, in degrees."""
    if not samples:
        return None
    samples = sorted(samples)
    tot = sum(s for _, s in samples)
    lo = hi = samples[0][0]
    acc = 0.0
    for deg, s in samples:
        acc += s
        if acc <= 0.10 * tot:
            lo = deg
        if acc <= 0.90 * tot:
            hi = deg
    return lo, hi


def _mean(samples):
    x = sum(s * math.cos(math.radians(d)) for d, s in samples)
    y = sum(s * math.sin(math.radians(d)) for d, s in samples)
    return math.degrees(math.atan2(y, x)) % 360


def hue_range(paths):
    """Measured range, plus per-frame means so a mixed set can be refused."""
    per = [(p, _hue_samples(p)) for p in paths]
    per = [(p, s) for p, s in per if s]
    if not per:
        return None, []
    means = [(os.path.basename(p), _mean(s)) for p, s in per]
    allsamples = [x for _, s in per for x in s]
    return _pct_range(allsamples), means


def band_profile(path):
    im = Image.open(path).convert("RGB").resize((200, 200))
    w = collections.Counter()
    total = 0.0
    for r, g, b in im.getdata():
        h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        if s < 0.10 or v < 0.10:      # near-neutral and near-black carry no hue
            continue
        deg = h * 360
        name = min(BANDS, key=lambda t: min(abs(deg - t[1]), 360 - abs(deg - t[1])))[0]
        w[name] += s
        total += s
    return {n: (100 * w[n] / total if total else 0.0) for n, _ in BANDS}


def preset_moves(path):
    top = [e for e in ET.parse(path).getroot().iter()
           if e.tag.endswith("Description")][0]
    moves = collections.defaultdict(dict)
    for k, v in top.attrib.items():
        m = re.fullmatch(r"\{.*\}(Hue|Saturation|Luminance)Adjustment(\w+)", k)
        if m and v.lstrip("+-").isdigit() and int(v) != 0:
            moves[m.group(2)][m.group(1)] = int(v)
    return moves


def grade_hues(path):
    top = [e for e in ET.parse(path).getroot().iter()
           if e.tag.endswith("Description")][0]
    def n(a, d=0):
        try:
            return int(top.get("{%s}%s" % (CRS, a)))
        except (TypeError, ValueError):
            return d
    return {
        "shadows":    n("SplitToningShadowHue", -1),
        "midtones":   n("ColorGradeMidtoneHue", -1),
        "highlights": n("SplitToningHighlightHue", -1),
    }, n("SplitToningBalance")


def main():
    argv = sys.argv[1:]
    shift = 0
    for flag, sign in (("--warmer", +1), ("--cooler", -1)):
        if flag in argv:
            i = argv.index(flag)
            shift = sign * int(argv[i + 1])
            del argv[i:i + 2]
    if len(argv) < 2:
        sys.exit(__doc__)
    refs, preset = argv[:-1], argv[-1]
    prof, moves = band_profile(refs[0]), preset_moves(preset)
    fails, warns = [], []

    print(f"reference: {', '.join(refs)}")
    print(f"preset:    {preset}\n")
    print(f"  {'band':<9}{'in reference':>13}   {'preset moves':<28}")
    for name, _ in BANDS:
        pct = prof[name]
        mv = ", ".join(f"{k[:3]}{v:+d}" for k, v in sorted(moves.get(name, {}).items()))
        print(f"  {name:<9}{pct:11.1f}%   {mv or '-':<28}")
        mv_d = moves.get(name, {})
        # Draining a band the reference lacks is how a look comes to lack it —
        # correct, not a mismatch. Only ADDING colour the reference does not
        # have, or rotating a hue that is not there, is a real mismatch.
        # Only INVENTING colour the reference lacks is a reference-match
        # failure. Draining an absent band is how the look came to lack it,
        # and rotating an absent band's hue is inert on the reference — both
        # are generalisation risks on the user's own photos, not mismatches.
        adds = [v for k, v in mv_d.items() if k == "Saturation" and v > HARD]
        if pct <= NEGLIGIBLE and adds:
            fails.append(f"{name} is {pct:.1f}% of the reference but the preset "
                         f"adds saturation {max(adds):+d} — that invents colour "
                         "the reference does not have")
        risky = [f"{k} {v:+d}" for k, v in sorted(mv_d.items())
                 if (k == "Saturation" and v < -HARD) or (k == "Hue" and abs(v) > HARD)]
        if pct <= NEGLIGIBLE and risky:
            warns.append(f"{name} ({', '.join(risky)}) — inert on the reference, "
                         "but will collapse or shift that colour on any subject "
                         "that has it")
        if pct >= DOMINANT and not moves.get(name):
            fails.append(f"{name} carries {pct:.1f}% of the reference's colour "
                         "and the preset does not touch it")

    rng, means = hue_range(refs)
    if len(means) > 1:
        spread = max(m for _, m in means) - min(m for _, m in means)
        print(f"\n  reference set: {len(means)} frames, means "
              + ", ".join(f"{n[:18]} {m:.0f}°" for n, m in means))
        if spread > SPREAD_LIMIT:
            fails.append(f"reference set spans {spread:.0f}° of hue "
                         f"(limit {SPREAD_LIMIT}°) — these frames are not one look. "
                         "Averaging them produces a range that describes none of "
                         "them. Pin a single primary reference instead.")
    if rng:
        lo, hi = rng
        lo, hi = lo + shift, hi + shift
        if shift:
            print(f"\n  stated deviation: {shift:+d}° "
                  f"({'warmer' if shift > 0 else 'cooler'} than the reference)")
        hues, bal = grade_hues(preset)
        print(f"\n  reference hue range (10th-90th pct): {lo:.0f}-{hi:.0f}°"
              f"    Balance {bal:+d}"
              f" ({'favours shadows' if bal < 0 else 'favours highlights' if bal else 'even'})")
        for zone, h in hues.items():
            if h < 0:
                continue
            if h > 180:                     # a deliberate cool/complementary grade
                print(f"  {zone:<11}{h:4d}°   complementary, not checked")
                continue
            off = lo - h if h < lo else (h - hi if h > hi else 0)
            target = "target" if shift else "reference"
            mark = "ok" if not off else f"{off:.0f}° {'below' if h < lo else 'above'} the {target}"
            print(f"  {zone:<11}{h:4d}°   {mark}")
            if off >= TOLERANCE:
                weight = " — and Balance weights it hardest" if (
                    zone == "shadows" and bal < 0) else ""
                fails.append(f"Color Grading {zone} at {h}° is {off:.0f}° outside "
                             f"the {'target' if shift else 'reference'} "
                             f"{lo:.0f}-{hi:.0f}° range{weight}")

    print()
    for f in fails:
        print(f"    FAIL: {f}")
    for w in warns:
        print(f"    warn: {w}")
    print()
    print("RED — the preset grades colour the reference does not have" if fails
          else "GREEN — preset moves line up with the reference")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
