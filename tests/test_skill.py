#!/usr/bin/env python3
"""Regression suite for the lightroom-editor skill.

Every test here corresponds to a bug that reached a user. Each one is
written to go RED against the skill as it stood before the fix, so the
suite proves the fix rather than describing it.

    tests/test_skill.py            run everything
    tests/test_skill.py --pre-fix  run the document tests against git HEAD
"""
import os, re, subprocess, sys, tempfile, xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "lightroom-editor"
REFS = SKILL / "references"
CHECK = ROOT / "scripts" / "preset-check.py"
VOCAB = ROOT / "scripts" / "crs-vocabulary.txt"
CRS = "http://ns.adobe.com/camera-raw-settings/1.0/"

results = []
skipped = []


def check(name, cond, detail=""):
    results.append((name, bool(cond), detail))
    print(f"  {'PASS' if cond else 'FAIL'}  {name}" + (f"\n          {detail}" if not cond and detail else ""))
    return cond


def skip(name, why):
    """Not runnable here. Never counts as a pass; never fails the suite."""
    skipped.append((name, why))
    print(f"  SKIP  {name}\n          {why}")


def read(rel, pre_fix=False):
    if pre_fix:
        out = subprocess.run(["git", "show", f"HEAD:{rel}"], cwd=ROOT,
                             capture_output=True, text=True)
        return out.stdout
    return (ROOT / rel).read_text()


def xml_blocks(md):
    return re.findall(r"```xml\n(.*?)```", md, re.S)


# ---------------------------------------------------------------- layer 1
def layer1_document(pre_fix=False):
    tag = " (pre-fix, at git HEAD)" if pre_fix else ""
    print(f"\nLAYER 1 — document invariants{tag}")
    xmp = read("skills/lightroom-editor/references/09-presets-xmp.md", pre_fix)
    skl = read("skills/lightroom-editor/SKILL.md", pre_fix)
    looks = read("skills/lightroom-editor/references/08-looks.md", pre_fix)
    src = read("skills/lightroom-editor/references/07-sources.md", pre_fix)

    # BUG: template shipped a pre-baked look, so every generated preset
    # inherited a grade nobody asked for.
    tmpl = xml_blocks(xmp)[0] if xml_blocks(xmp) else ""
    sliders = re.findall(r'crs:((?:Hue|Saturation|Luminance)Adjustment\w+|'
                         r'SplitToning\w+|ColorGrade\w+|Grain\w+|PostCropVignette\w+|'
                         r'Contrast2012|Highlights2012|Shadows2012|Whites2012|'
                         r'Blacks2012|Texture|Clarity2012|Dehaze|Vibrance|'
                         r'Saturation|Sharpness|Sharpen\w+|Luminance\w+|Color\w*Noise\w*)'
                         r'="([^"]*)"', tmpl)
    nonzero = [(k, v) for k, v in sliders if v.lstrip("+-").rstrip("0.").strip("0")
               and v not in ("0",) and re.fullmatch(r"[+-]?[\d.]+", v) and float(v) != 0]
    zeros = [(k, v) for k, v in sliders if v == "0"]
    check("template carries no pre-baked slider values", not nonzero,
          f"{len(nonzero)} non-zero sliders in the template: {[k for k,_ in nonzero][:6]}")
    check("template carries no zero-defaults that overwrite user settings", not zeros,
          f"{len(zeros)} attributes set to 0, which the doc's own Common Mistakes forbids")

    # BUG: 0/157 presets set ToneCurveName2012 -> Lightroom discarded every curve.
    check("tone-curve rule is stated as mandatory",
          re.search(r"must also carry\s*\n?\s*`crs:ToneCurveName2012", xmp) or
          re.search(r"ToneCurveName2012.*must", xmp),
          "no mandatory rule tying ToneCurvePV2012 to ToneCurveName2012")
    check("template itself sets ToneCurveName2012",
          'crs:ToneCurveName2012="Custom"' in tmpl)

    # BUG: signs were undocumented; IncrementalTint +6 pushed toward magenta.
    for attr, word in [("IncrementalTint", "magenta"),
                       ("HueAdjustmentYellow", "orange"),
                       ("SplitToningBalance", "shadow")]:
        # any table row that names the attribute and gives its direction
        rows = re.findall(rf"\|[^|\n]*`{attr}`\s*\|([^|\n]*)\|([^|\n]*)\|", xmp)
        check(f"sign direction documented for {attr}",
              any(word in (a + b).lower() for a, b in rows),
              f"no table row giving the direction of {attr}; "
              f"found {len(rows)} row(s) naming it")

    # BUG: hard Color Mix moves on bands the reference did not contain.
    check("looks doc requires measuring the reference's bands first",
          re.search(r"before you touch any of\s*\n?them|which bands the reference actually contains", looks),
          "08-looks.md does not require establishing band content before grading")

    # BUG: negative Green Sat treated as always-wrong, with no creative carve-out.
    check("Green Sat separates corrective from creative use",
          "creative move" in src and "correction only" in src,
          "07-sources.md still reads as a blanket ban on negative Green Sat")

    # BUG: a reference image was assumed to be the target, so a user who
    # wanted "warm leaning golden" got a preset faithful to an orange cover.
    check("intake asks how close to land on the reference",
          "Fidelity" in skl and "starting point" in skl,
          "SKILL.md Step 1 does not ask whether the reference is the target")
    check("intake explains that fidelity cannot be inferred",
          "cannot be inferred" in skl,
          "SKILL.md does not say the deviation must be asked for, not guessed")

    # BUG: a reference 'set' mixing unrelated frames averaged into a range
    # that described none of them, and flipped the ranking of six presets.
    check("looks doc requires pinning a single-look reference set",
          "one primary reference" in looks and "12" in looks,
          "08-looks.md does not define what may go in a reference set")
    check("looks doc requires recording the deviation",
          "--warmer" in looks and "lost the moment" in looks,
          "08-looks.md does not require the deviation to be written down")

    # BUG: skill refused RAW outright even where a shell existed.
    check("RAW-visibility rule is conditional on environment",
          "code environment" in skl and "rawpy" in skl,
          "SKILL.md still claims RAW can never be read")

    # every XML example in the doc must actually parse
    for i, blk in enumerate(xml_blocks(xmp)):
        if not blk.lstrip().startswith("<"):
            continue
        body = blk if blk.lstrip().startswith("<x:xmpmeta") else \
            f'<r xmlns:crs="{CRS}" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">{blk}</r>'
        try:
            ET.fromstring(body)
            ok, err = True, ""
        except ET.ParseError as e:
            ok, err = False, str(e)
        check(f"XML example #{i+1} in 09-presets-xmp.md is well-formed", ok, err)


# ---------------------------------------------------------------- layer 2
GOOD = """<x:xmpmeta xmlns:x="adobe:ns:meta/"><rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
<rdf:Description rdf:about="" xmlns:crs="http://ns.adobe.com/camera-raw-settings/1.0/"
 crs:PresetType="Normal" crs:UUID="{uuid}" crs:Contrast2012="+8"
 crs:SaturationAdjustmentOrange="+10" crs:SplitToningHighlightHue="45"
 crs:ToneCurveName2012="Custom" crs:HasSettings="True">
 <crs:ToneCurvePV2012><rdf:Seq><rdf:li>0, 12</rdf:li><rdf:li>128, 128</rdf:li><rdf:li>255, 248</rdf:li></rdf:Seq></crs:ToneCurvePV2012>
</rdf:Description></rdf:RDF></x:xmpmeta>"""

MUTATIONS = [
    ("drops ToneCurveName2012 (the 157-preset bug)",
     lambda s: s.replace(' crs:ToneCurveName2012="Custom"', ''), "ignores the curve"),
    ("uses ColorGradeShadowHue (does not exist)",
     lambda s: s.replace('crs:Contrast2012="+8"', 'crs:ColorGradeShadowHue="220"'), "unknown crs attribute"),
    ("uses GrainRoughness (real name is GrainFrequency)",
     lambda s: s.replace('crs:Contrast2012="+8"', 'crs:GrainRoughness="50"'), "unknown crs attribute"),
    ("Contrast beyond Camera Raw's range",
     lambda s: s.replace('crs:Contrast2012="+8"', 'crs:Contrast2012="+140"'), "outside Camera Raw range"),
    ("carries Exposure2012 (breaks portability)",
     lambda s: s.replace('crs:Contrast2012="+8"', 'crs:Exposure2012="+0.35"'), "per-photo"),
    ("carries Temperature (breaks portability)",
     lambda s: s.replace('crs:Contrast2012="+8"', 'crs:Temperature="5400"'), "per-photo"),
    ("lowercase UUID",
     lambda s: s.replace("{uuid}", "a" * 32), "32 uppercase hex"),
    ("non-monotonic tone curve",
     lambda s: s.replace("<rdf:li>128, 128</rdf:li>", "<rdf:li>64, 60</rdf:li><rdf:li>32, 20</rdf:li>"),
     "not strictly increasing"),
    ("curve point outside 0..255",
     lambda s: s.replace("<rdf:li>255, 248</rdf:li>", "<rdf:li>300, 248</rdf:li>"), "outside 0..255"),
    ("malformed curve point",
     lambda s: s.replace("<rdf:li>128, 128</rdf:li>", "<rdf:li>128</rdf:li>"), "malformed point"),
    ("not well-formed XML",
     lambda s: s.replace("</rdf:Description>", ""), "not well-formed"),
]


def run_check(*paths):
    r = subprocess.run([sys.executable, str(CHECK), *map(str, paths)],
                       capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def layer2_mutations():
    print("\nLAYER 2 — mutation testing (is every check load-bearing?)")
    with tempfile.TemporaryDirectory() as d:
        base = Path(d) / "good.xmp"
        base.write_text(GOOD.replace("{uuid}", "A1B2C3D4E5F60718293A4B5C6D7E8F90"))
        rc, out = run_check(base)
        check("unmutated control preset passes", rc == 0, out.strip()[-300:])

        for i, (name, mutate, expect) in enumerate(MUTATIONS):
            p = Path(d) / f"mut{i}.xmp"
            p.write_text(mutate(GOOD).replace("{uuid}", f"{i:032X}"))
            rc, out = run_check(p)
            check(f"caught: {name}", rc == 1 and expect in out,
                  f"expected {expect!r} in output; got:\n{out.strip()[:400]}")

        # duplicate UUID only detectable across files
        a, b = Path(d) / "a.xmp", Path(d) / "b.xmp"
        dup = GOOD.replace("{uuid}", "DEADBEEF" * 4)
        a.write_text(dup); b.write_text(dup)
        rc, out = run_check(a, b)
        check("caught: duplicate UUID across two presets", rc == 1 and "reused" in out,
              out.strip()[:300])


# ---------------------------------------------------------------- layer 3
def layer3_corpora():
    print("\nLAYER 3 — real corpora")
    real = sorted((ROOT / "references").glob("*/*.xmp"))
    if real:
        rc, out = run_check(*real)
        check(f"{len(real)} real Lightroom-exported presets all pass", rc == 0,
              out.strip()[-400:])
    else:
        skip("real Lightroom-exported preset corpus",
             "references/ is gitignored private material (leak-check enforces "
             "this) — clone-only checkouts cannot run it")

    old = sorted(Path.home().glob("Desktop/creatives/presets/*.xmp"))
    if not old:
        skip("pre-fix preset corpus", "no ~/Desktop/creatives/presets on this machine")
    if old:
        rc, out = run_check(*old)
        n = re.search(r"RED — (\d+) of (\d+)", out)
        check(f"the {len(old)} pre-fix presets are still detected as broken",
              rc == 1 and n and int(n.group(1)) == int(n.group(2)),
              "expected every pre-fix preset to fail; " + out.strip()[-200:])


# ---------------------------------------------------------------- layer 4
LOOK = ROOT / "scripts" / "look-match.py"

PRESET = """<x:xmpmeta xmlns:x="adobe:ns:meta/"><rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
<rdf:Description rdf:about="" xmlns:crs="http://ns.adobe.com/camera-raw-settings/1.0/"
 crs:UUID="0123456789ABCDEF0123456789ABCDEF" {attrs}/>
</rdf:RDF></x:xmpmeta>"""


def golden_ref(path, hue_deg=40):
    """A synthetic reference of known hue, so the test needs no external image."""
    from PIL import Image
    import colorsys
    im = Image.new("RGB", (64, 64))
    px = []
    for y in range(64):
        for x in range(64):
            h = ((hue_deg + (x % 5) - 2) % 360) / 360
            r, g, b = colorsys.hsv_to_rgb(h, 0.55, 0.35 + 0.5 * (y / 64))
            px.append((int(r * 255), int(g * 255), int(b * 255)))
    im.putdata(px)
    im.save(path)


def run_look(ref, preset):
    return run_look_flags([], ref, preset)


def run_look_flags(flags, ref, preset):
    r = subprocess.run([sys.executable, str(LOOK), *flags, str(ref), str(preset)],
                       capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def run_look_multi(refs, preset):
    r = subprocess.run([sys.executable, str(LOOK), *map(str, refs), str(preset)],
                       capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def layer4_look():
    print("\nLAYER 4 — look gate (reference-vs-preset)")
    try:
        import PIL  # noqa: F401
    except ImportError:
        skip("look gate (7 checks)",
             "Pillow not installed — pip install -r tests/requirements.txt")
        return
    with tempfile.TemporaryDirectory() as d:
        ref = Path(d) / "ref.png"
        golden_ref(ref, hue_deg=40)          # amber reference, ~40 deg

        def preset(attrs, name="p"):
            p = Path(d) / f"{name}.xmp"
            p.write_text(PRESET.format(attrs=attrs))
            return p

        # grading inside the reference's own hue range
        rc, out = run_look(ref, preset(
            'crs:SplitToningShadowHue="38" crs:ColorGradeMidtoneHue="40" '
            'crs:SplitToningHighlightHue="42" crs:SaturationAdjustmentOrange="+8"', "inrange"))
        check("in-range grading hues pass", rc == 0, out.strip()[-300:])

        # grading well below the reference -> orange instead of gold
        rc, out = run_look(ref, preset(
            'crs:SplitToningShadowHue="12" crs:ColorGradeMidtoneHue="14" '
            'crs:SplitToningBalance="-25" crs:SaturationAdjustmentOrange="+8"', "below"))
        check("grading hue far below the reference fails",
              rc == 1 and "outside the reference" in out, out.strip()[-300:])
        check("shadow-weighted Balance is reported",
              "weights it hardest" in out, out.strip()[-300:])

        # REGRESSION: draining an absent band is how a look comes to lack it.
        rc, out = run_look(ref, preset(
            'crs:SaturationAdjustmentBlue="-45" crs:SaturationAdjustmentOrange="+8"', "drain"))
        check("draining an absent band warns, does not fail",
              rc == 0 and "warn:" in out, out.strip()[-300:])

        # REGRESSION: rotating an absent band's hue is inert on the reference.
        rc, out = run_look(ref, preset(
            'crs:HueAdjustmentBlue="-40" crs:SaturationAdjustmentOrange="+8"', "rot"))
        check("rotating an absent band's hue warns, does not fail",
              rc == 0 and "warn:" in out, out.strip()[-300:])

        # adding colour the reference does not have IS a mismatch
        rc, out = run_look(ref, preset(
            'crs:SaturationAdjustmentBlue="+45" crs:SaturationAdjustmentOrange="+8"', "add"))
        check("adding saturation to an absent band fails",
              rc == 1 and "invents colour" in out, out.strip()[-300:])

        # REGRESSION: a mixed reference set must be refused, not averaged.
        wide = Path(d) / "wide.png"
        golden_ref(wide, hue_deg=75)
        rc, out = run_look_multi([ref, wide], preset(
            'crs:SplitToningShadowHue="38" crs:SaturationAdjustmentOrange="+8"', "mixed"))
        check("reference set spanning >12 deg is refused, not averaged",
              rc == 1 and "not one look" in out, out.strip()[-300:])

        near = Path(d) / "near.png"
        golden_ref(near, hue_deg=45)
        rc, out = run_look_multi([ref, near], preset(
            'crs:SplitToningShadowHue="42" crs:ColorGradeMidtoneHue="42" '
            'crs:SaturationAdjustmentOrange="+8"', "coherent"))
        check("coherent reference set is accepted", rc == 0, out.strip()[-300:])

        # a stated deviation moves the target, so intent is checked not fidelity
        p_warm = preset('crs:SplitToningShadowHue="52" crs:ColorGradeMidtoneHue="54" '
                        'crs:SaturationAdjustmentOrange="+8"', "warm")
        rc, out = run_look(ref, p_warm)
        check("grading warmer than the reference fails without a stated deviation",
              rc == 1 and "outside the reference" in out, out.strip()[-300:])
        rc, out = run_look_flags(["--warmer", "12"], ref, p_warm)
        check("the same preset passes once the deviation is stated",
              rc == 0 and "stated deviation: +12" in out, out.strip()[-300:])

        # the reference's dominant band must be addressed
        rc, out = run_look(ref, preset('crs:SaturationAdjustmentBlue="-30"', "ignore"))
        check("leaving the dominant band untouched fails",
              rc == 1 and "does not touch it" in out, out.strip()[-300:])


def main():
    if "--pre-fix" in sys.argv:
        layer1_document(pre_fix=True)
    else:
        layer1_document()
        layer2_mutations()
        layer3_corpora()
        layer4_look()
    passed = sum(1 for _, ok, _ in results if ok)
    total = len(results)
    tail = f"  ({len(skipped)} skipped)" if skipped else ""
    print(f"\n{'GREEN' if passed == total else 'RED'} — {passed}/{total} checks passed{tail}")
    for name, why in skipped:
        print(f"  skipped: {name} — {why}")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
