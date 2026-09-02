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
import collections, os, re, sys, xml.etree.ElementTree as ET

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lookstats as ls

CRS = "http://ns.adobe.com/camera-raw-settings/1.0/"
BANDS = ls.BANDS

# Band shares changed meaning underneath these two. Under the old HSV-
# saturation weighting a share meant "how much of the frame's saturation sits
# here"; under chroma weighting it means "how much of the frame's colour sits
# here". The values are UNCHANGED because the eleven behaviours in
# tests/test_skill.py — the contract — all still hold at 25 and 5.
#
# CALIBRATED 2 Sep 2026 against 17 real frames — 11 Sony a6400 ARW and 6 iPhone
# ProRAW — which is the check the note that stood here used to ask for. Both
# numbers survived; what did not survive was the assumption that one of them
# always has something to say.
#
# DOMINANT sits just under its empirical ceiling. Every one of the 17 frames
# has a band clearing 25%, so the check always had something to test — but the
# flattest frame's strongest band measured 25.9%, a margin of 0.9 points. At 26
# that frame has no dominant band at all; at 30, two frames do not; at 40, four.
# The threshold is NOT raised, because 25% is 2x an even eight-band split and
# that is what makes it mean "dominant" rather than "biggest". It is also not
# lowered: 20% is 1.6x even, which is not dominance, and it would demand a
# preset touch 1.73 bands per frame instead of 1.27.
#
# The real finding was the failure mode at the edge. A reference where no band
# clears DOMINANT used to produce a silent pass, and the output positively
# asserted "the band checks above did [run]". That is now announced. The margin
# is thin and the sample is 17 frames from two cameras, so expect a flat
# reference to hit it — that case is now reported rather than mistaken for a
# clean result.
#
# NEGLIGIBLE is UNCHANGED and, honestly, unvalidated. Across the 11 ARWs it
# calls 42 of 88 bands negligible and leaves one frame with none, which is a
# sane-looking spread — but "sane-looking" is not calibration. Moving it needs
# reference/preset pairs with known-good and known-bad verdicts to score
# against, and no such labelled set exists here. Photographs alone cannot
# settle it. Left where it is, deliberately, rather than tuned against nothing.
DOMINANT = 25.0     # a band carrying >= this much of the colour must be addressed
NEGLIGIBLE = 5.0    # a band carrying <= this much should not be pushed hard

# Unchanged, and deliberately so: both are angles on the RGB wheel, compared
# against crs: hue attributes which are angles on the same wheel. The unit did
# not move, so the number does not either.
HARD = 20           # |value| above this counts as a hard push
SPREAD_LIMIT = 12   # max degrees the reference frames' means may differ by
TOLERANCE = 3       # degrees a grading hue may sit outside the range


def band_profile(path):
    """Share of the reference's colour carried by each Color Mix band."""
    return ls.band_profile(ls.load_rgb(path))


def hue_range(paths):
    """Measured range, its centre and core, plus per-frame means.

    The centre matters as much as the range. A band NAME covers roughly
    thirty degrees -- everything from about 15 to 45 degrees is "Orange" --
    so a reference measuring 40 degrees is reported as Orange, and a grade
    placed at the Orange band centre of 30 lands ten degrees redder than the
    reference actually is. That is how a warm amber look comes out orange.

    The core is the 25th-75th percentile: the half of the reference's colour
    closest to its centre. A grading hue inside the full range but outside
    the core is legal and still a warning, because it sits at the edge of
    what the reference contains rather than at the middle of it.
    """
    per = [(p, ls.load_rgb(p)) for p in paths]
    means = [(os.path.basename(p), m) for p, rgb in per
             if (m := ls.frame_hue_mean(rgb)) is not None]
    stacked = np.concatenate([rgb for _, rgb in per], axis=0)
    return (ls.hue_range(stacked), ls.frame_hue_mean(stacked),
            ls.hue_range(stacked, 25.0, 75.0), means)


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

    # A reference flat enough that no band clears DOMINANT gets no opinion out
    # of the check above: the loop appends nothing and the gate returns 0,
    # which is indistinguishable from a preset that addressed everything it
    # should have. Measured, not hypothetical -- see the calibration note on
    # DOMINANT. Say it, exactly as the hue check below says it.
    strongest = max(prof.items(), key=lambda kv: kv[1])
    dominant_ran = strongest[1] >= DOMINANT
    if not dominant_ran:
        print(f"\n  dominant band: NONE — no band carries {DOMINANT:.0f}% of this "
              f"reference's\n  colour; the strongest is {strongest[0]} at "
              f"{strongest[1]:.1f}%. The check that a\n  dominant band must be "
              f"addressed did NOT run, so a preset can leave\n  every band alone "
              f"and still come back clean. Pin a reference with a\n  dominant "
              f"colour to close it.")

    rng, centre, core, means = hue_range(refs)
    if len(means) > 1:
        spread = max(m for _, m in means) - min(m for _, m in means)
        print(f"\n  reference set: {len(means)} frames, means "
              + ", ".join(f"{n[:18]} {m:.0f}°" for n, m in means))
        if spread > SPREAD_LIMIT:
            fails.append(f"reference set spans {spread:.0f}° of hue "
                         f"(limit {SPREAD_LIMIT}°) — these frames are not one look. "
                         "Averaging them produces a range that describes none of "
                         "them. Pin a single primary reference instead.")
    if rng is None:
        # Not a pass. The reference's hue is too spread out for a range to be
        # measured, so the Color Grading check below cannot run at all. Saying
        # so beats deciding it on bounds that would not reproduce.
        # Only claim the band checks ran when they did — and do not repeat the
        # advice the dominant-band message above has already given.
        also = ("the band\n  checks above did. Pin a reference with a dominant "
                "colour to close it." if dominant_ran else
                "and neither did\n  the dominant-band check above.")
        print(f"\n  reference hue range: NOT MEASURABLE — this reference's colour "
              f"is spread\n  too evenly round the wheel (concentration below "
              f"{ls.HUE_CONCENTRATION_MIN}) for a range\n  to mean anything. The "
              f"Color Grading hue check did NOT run; {also}")
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
        if centre is not None:
            print(f"  reference hue centre: {centre + shift:.0f}° — grade here. The band "
                  f"name above\n  covers about thirty degrees and its centre is not this one.")
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
            if off < TOLERANCE and core and centre is not None:
                # How far off the reference's centre this grade sits, against
                # an allowance taken from the reference itself: the half-width
                # of its middle half, floored at the gate's own TOLERANCE so a
                # very tightly concentrated reference does not warn on every
                # grade. No new threshold -- both numbers already exist.
                clo, chi = core[0] + shift, core[1] + shift
                half = ((chi - clo) % 360) / 2.0
                allow = max(half, TOLERANCE)
                dev = abs(((h - (centre + shift)) + 180) % 360 - 180)
                if dev > allow:
                    warns.append(f"Color Grading {zone} at {h}° sits {dev:.0f}° off "
                                 f"the reference's centre of {centre + shift:.0f}° "
                                 f"(its middle half runs {clo:.0f}-{chi:.0f}°). Inside "
                                 f"the range, so not a failure — but it grades the "
                                 f"edge of the look rather than the look. A band NAME "
                                 f"spans about thirty degrees; do not grade at the "
                                 f"band's centre, grade at the measured one.")
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
    # Name what actually ran. A green that does not say which checks were
    # inoperative reads as a stronger result than it is.
    didnt = ([] if rng else ["the hue check"]) + \
            ([] if dominant_ran else ["the dominant-band check"])
    partial = f" ({' and '.join(didnt)} could not run)" if didnt else ""
    print(f"RED — the preset grades colour the reference does not have{partial}" if fails
          else f"GREEN — preset moves line up with the reference{partial}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
