#!/usr/bin/env python3
"""What colour is this photograph actually made of?

Measures a file and prints what it finds. It does not choose sliders — that
is the reading of the numbers, and it belongs to whoever is holding the
recipe. The one exception is Tint, and only because the mapping is measured
off the file itself rather than assumed; see --source below.

Two things to point it at, and they answer different questions:

  a REFERENCE       the look you are trying to land on. Bands, hue range,
                    per-zone cast, black point: the decomposition Step 4
                    needs before it writes a recipe.

  your SOURCE file  --source. Adds the cast measured off this frame, which
                    turns "Sony ARW runs green" from a stored profile into a
                    number read off the photograph in front of you. With
                    crs-render.py present it also probes what Tint does to
                    THIS file and prints the correction that follows.

Every figure is measured or withheld. Where the frame cannot support a
reading — no neutral content, two warm populations, nothing colourful — it
says so and gives no number, and the verdict line counts how many. A refusal
is a result: fall back to the camera profile and label it unmeasured.

Usage:
  scripts/look-analyze.py REFERENCE.jpg
  scripts/look-analyze.py --source photo.ARW
  scripts/look-analyze.py --source photo.ARW --portrait
  scripts/look-analyze.py --source photo.ARW --profile "Sony ARW, green bias"
"""
import importlib.util, os, sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lookstats as ls

HERE = Path(__file__).resolve().parent


def load_crs():
    """crs-render.py, if it is installed beside us. Only needed for the probe."""
    p = HERE / "crs-render.py"
    if not p.exists():
        return None
    spec = importlib.util.spec_from_file_location("crs_render", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_segment():
    """segment.py, if it is installed beside us. Optional, like crs-render."""
    p = HERE / "segment.py"
    if not p.exists():
        return None
    spec = importlib.util.spec_from_file_location("segment", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def report(path, as_source=False, portrait=False, profile=None):
    rgb, provenance = ls.load_source(path)
    preview = provenance == ls.PREVIEW
    withheld = []

    print(f"{'source' if as_source else 'reference'}:    {path}")
    print(f"pixels:       {provenance}")
    if preview:
        print("              LibRaw could not unpack this file, so these are the")
        print("              camera's own embedded preview — its finished render,")
        print("              not its sensor data. The look figures below still")
        print("              hold: the render IS the look. The baseline figures")
        print("              do not, and are withheld rather than guessed.")
    print()

    if as_source:
        cast = None if preview else ls.measure_cast(rgb)
        if preview:
            withheld.append("cast")
            print("  measured cast       WITHHELD — the camera already made this")
            print("                      white-balance call, so a cast measured here")
            print("                      is the cast of its render. Correcting the")
            print("                      render with a number read off the render is")
            print("                      circular, and the number would look fine.")
            print(f"  falling back to     {profile or 'the camera profile for this source'}"
                  "\n                      (from profile, UNMEASURED)")
        elif cast is None:
            withheld.append("cast")
            print("  neutral content     too little, or nothing near neutral")
            print("  measured cast       WITHHELD — this frame does not contain")
            print("                      enough near-neutral content to read a")
            print("                      cast from. A green scene is not a green")
            print("                      cast, and guessing here is how that")
            print("                      mistake gets made.")
            print(f"  falling back to     {profile or 'the camera profile for this source'}"
                  "\n                      (from profile, UNMEASURED)")
        else:
            lean = ("green" if cast["a"] < 0 else "magenta") if abs(cast["a"]) >= abs(cast["b"]) \
                else ("blue" if cast["b"] < 0 else "yellow")
            print(f"  neutral content     {cast['neutral_fraction'] * 100:.1f}% of frame")
            print(f"  measured cast       a {cast['a']:+.2f}  b {cast['b']:+.2f}   leans {lean}")
            crs = load_crs()
            if crs is None:
                print("  Tint                not probed — crs-render.py is not installed")
            else:
                lin, depth = crs.load_image(path)
                pr = ls.probe_tint(crs, lin)
                sens = pr["sensitivity"]
                print(f"  Tint                {pr['tint']:+.0f}"
                      f"   (sensitivity {sens:.3f} a* per unit)" if sens
                      else f"  Tint                {pr['tint']:+.0f}")
                print("                      probed on THIS file with crs-render.py:")
                print("                      Tint was moved a known step and the a*")
                print("                      shift measured, then inverted. This is")
                print("                      our renderer's Tint, not Adobe's.")
                print("                      A lean that needs a large Tint to remove is")
                print("                      often the subject's own colour rather than a")
                print("                      cast -- a wall of cyan glass reads exactly like")
                print("                      a green camera. Nothing here can tell those")
                print("                      apart. Look at the picture before typing it.")
        print()

    prof = ls.band_profile(rgb)
    print(f"  {'band':<9}{'share':>9}")
    for name, _ in ls.BANDS:
        print(f"  {name:<9}{prof[name]:8.1f}%")

    rng = ls.hue_range(rgb)
    if rng is None:
        withheld.append("hue range")
        print(f"\n  hue range           WITHHELD — this frame's colour is spread too")
        print(f"                      evenly round the wheel (concentration below")
        print(f"                      {ls.HUE_CONCENTRATION_MIN}) for a range to mean anything, or")
        print(f"                      nothing in it carries enough colour at all.")
        print(f"                      look-match.py cannot run its hue check here.")
    else:
        lo, hi = rng
        core = ls.hue_range(rgb, 25.0, 75.0)
        centre = ls.frame_hue_mean(rgb)
        print(f"\n  hue range (10th-90th pct)   {lo:.0f}-{hi:.0f}°   on the RGB wheel,")
        print( "                              the same wheel crs: hue values use")
        print(f"  hue centre                  {centre:.0f}°   GRADE HERE")
        if core:
            print(f"  middle half                 {core[0]:.0f}-{core[1]:.0f}°")
        top = max(prof.items(), key=lambda kv: kv[1])
        band_centre = dict(ls.BANDS)[top[0]]
        off = abs(((centre - band_centre) + 180) % 360 - 180)
        print(f"\n  The dominant band is {top[0]} at {top[1]:.1f}%, and its centre is "
              f"{band_centre}°.\n  The measured centre is {centre:.0f}°, {off:.0f}° away. A band "
              f"name covers about\n  thirty degrees, so it is a label, not a target: grading at "
              f"the band\n  centre is what turns a warm amber reference into an orange one.")

    if preview:
        withheld.append("black point")
        print( "  black point                 WITHHELD — the camera has already placed")
        print( "                              these blacks. A preview says nothing about")
        print( "                              the recovery headroom the RAW still holds.")
    else:
        print(f"  black point                 {ls.black_point(rgb):.4f}   "
              "relative luminance, linear")

    print(f"\n  {'zone':<7}{'L':>6}{'a':>8}{'b':>8}{'share':>9}")
    for z in ls.zones(rgb):
        if z["share"] == 0:
            continue
        lo_l = z["zone"] * 100 // ls.ZONES
        print(f"  {f'{lo_l}-{lo_l + 100 // ls.ZONES}':<7}{z['L']:6.0f}"
              f"{z['a']:+8.1f}{z['b']:+8.1f}{z['share'] * 100:8.1f}%")

    if portrait:
        print()
        # Try the segmenter first. It answers the one question colour cannot —
        # which pixels are a face — and where it can, the reading is taken off
        # the face instead of off the frame's warm content. Absent the model
        # or its runtime, this falls straight back to the colour-only path,
        # which withholds by default. See segment.py.
        seg = load_segment()
        s = seg.skin(path) if seg is not None else {"ok": False, "reason": "", "confidence": None}
        if s.get("ok"):
            print(f"  skin tone           ITA {s['ita']:.1f}°  ({s['ita_class']})")
            print(f"                      L {s['L']:.1f}  a {s['a']:+.1f}  b {s['b']:+.1f}")
            print(f"                      measured on the segmented face — "
                  f"{s['face_share'] * 100:.1f}% of frame,")
            print(f"                      segmenter confidence {s['confidence']:.2f}. Not the")
            print( "                      frame's warm content. Look at the picture:")
            print( "                      a mask is not a judgement.")
        elif s.get("confidence") is not None:
            # The segmenter ran and declined. That is a stronger statement than
            # the colour-only refusal, so it is the one worth printing.
            withheld.append("skin tone")
            print(f"  skin tone           WITHHELD — {s['reason']}")
        else:
            s = ls.skin(rgb)
            if s["ok"]:
                print(f"  skin tone           ITA {s['ita']:.1f}°  ({s['ita_class']})")
                print(f"                      L {s['L']:.1f}  a {s['a']:+.1f}  b {s['b']:+.1f}"
                      f"   over {s['share'] * 100:.1f}% of frame")
                print("                      warm population only — nothing here can")
                print("                      tell a face from wood or sand, so read it")
                print("                      against the picture.")
            else:
                withheld.append("skin tone")
                print(f"  skin tone           WITHHELD — {s['reason']}")

    print()
    if withheld:
        print(f"AMBER — measured, except {', '.join(withheld)}: "
              f"{len(withheld)} figure(s) withheld above, with the reason given")
    else:
        print("GREEN — every figure above was measured on this frame")
    return withheld


def main():
    argv = sys.argv[1:]
    as_source = "--source" in argv
    portrait = "--portrait" in argv
    profile = None
    if "--profile" in argv:
        i = argv.index("--profile")
        profile = argv[i + 1]
        del argv[i:i + 2]
    argv = [a for a in argv if a not in ("--source", "--portrait")]
    if len(argv) != 1:
        sys.exit(__doc__)
    if not Path(argv[0]).exists():
        sys.exit(f"no such file: {argv[0]}")
    report(argv[0], as_source, portrait, profile)
    return 0


if __name__ == "__main__":
    sys.exit(main())
