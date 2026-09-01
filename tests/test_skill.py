#!/usr/bin/env python3
"""Regression suite for the lightroom-editor skill.

Every test here corresponds to a bug that reached a user. Each one is
written to go RED against the skill as it stood before the fix, so the
suite proves the fix rather than describing it.

    tests/test_skill.py             run everything
    tests/test_skill.py --pre-fix   run the document tests against the commit
                                    before this branch (default: merge-base
                                    with main), proving they go red there
    tests/test_skill.py --pre-fix REF   use an explicit ref
"""
import importlib.util, os, re, subprocess, sys, tempfile, xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "lightroom-editor"
REFS = SKILL / "references"
SCRIPTS = SKILL / "scripts"
CHECK = SCRIPTS / "preset-check.py"
VOCAB = SCRIPTS / "crs-vocabulary.txt"
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


def baseline_ref():
    """The commit this branch forked from — never HEAD, which would compare
    the fix against itself and report a meaningless green."""
    if "--pre-fix" in sys.argv:
        i = sys.argv.index("--pre-fix")
        if i + 1 < len(sys.argv) and not sys.argv[i + 1].startswith("-"):
            return sys.argv[i + 1]
    mb = subprocess.run(["git", "merge-base", "HEAD", "main"], cwd=ROOT,
                        capture_output=True, text=True)
    return mb.stdout.strip() or "main"


def read(rel, pre_fix=False):
    if pre_fix:
        out = subprocess.run(["git", "show", f"{baseline_ref()}:{rel}"], cwd=ROOT,
                             capture_output=True, text=True)
        if out.returncode != 0:
            sys.exit(f"cannot read {rel} at {baseline_ref()}: {out.stderr.strip()}")
        return out.stdout
    return (ROOT / rel).read_text()


def xml_blocks(md):
    return re.findall(r"```xml\n(.*?)```", md, re.S)


# ---------------------------------------------------------------- layer 1
def layer1_document(pre_fix=False):
    tag = f" (baseline {baseline_ref()[:8]})" if pre_fix else ""
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

    # BUG: Step 1 "interviewed" so softly that it never ran. The skill went
    # straight to numbers on assumptions it never stated, because any
    # hesitation counted as a decline and the escape hatch was unconditional.
    step1 = skl.split("## Step 2")[0]
    check("intake states that no number leaves Step 1 until the gate opens",
          re.search(r"[Nn]o slider number leaves this step", step1),
          "Step 1 does not block Step 2; intake is advisory again")
    check("the fail-open decline clause is gone",
          "Missing answers are fine if the user declines" not in skl,
          "the clause that let any hesitation skip intake is still present")
    check("the adaptive one-at-a-time/block clause is gone",
          "when they clearly want speed" not in skl,
          "intake still leaves the asking mode to a judgement call")
    check("the gate opens only on a literal token",
          "`skip intake`" in step1,
          "Step 1 names no explicit override phrase, so the hatch is model-judged")
    check("silence and impatience are named as not opening the gate",
          re.search(r"silence.*vague.*impatien|impatien.*silence", step1, re.S | re.I),
          "Step 1 does not say what fails to open the gate")

    # BUG: a fact the agent could measure was being asked of the user, and a
    # decision the user owned was being assumed. The gate splits them.
    check("gate separates measured facts from user decisions",
          "Measurement" in step1 and "The user only" in step1,
          "Step 1 does not say which gates may be settled by measurement")
    check("Fidelity gates only when a reference is attached",
          re.search(r"only when a reference image is attached", step1),
          "Fidelity is not stated as a conditional gate")

    # BUG: a vague look word was accepted as an Intent and silently guessed at.
    check("vague look words must be decomposed and ratified",
          "ratified" in step1 and "Silence is not ratification" in step1,
          "Step 1 still lets a vague word stand as an Intent")
    check("Intent-vs-source conflicts stop for the user to resolve",
          "conflict, not a\nbrief" in step1 or "conflict, not a brief" in step1,
          "Step 1 does not treat an incoherent Intent as a blocking conflict")

    # BUG: the gate existed only in Step 1, so nothing downstream enforced it.
    check("a red flag catches a number emitted with a gate unanswered",
          re.search(r"gate still unanswered", skl),
          "Red flags do not cover emitting a number before the gate opens")
    check("a red flag catches a vague word accepted as an Intent",
          re.search(r"vague look word as an Intent", skl),
          "Red flags do not cover accepting a vague look word")
    check("the Verdict opens with a receipt of what the gate settled",
          "receipt" in skl and "(measured)" in skl,
          "Step 2 does not surface the settled gate in the answer itself")

    # BUG: presets shipped unverified, and 'accuracy' was never measured at all.
    check("a Verify step exists and gates delivery",
          "## Step 5 — Verify" in skl,
          "there is no verification stage between Look and Deliver")
    check("the verify gate is stated in dE, not in a percentage",
          re.search(r"mean ΔE00 ≤ 1\.0", skl),
          "no measurable stopping threshold is stated for the loop")
    check("the tunable slider set is restricted to the modellable ones",
          re.search(r"Temperature, Tint, Exposure, the tone-curve\s*\n?\s*points", skl),
          "Step 5 does not restrict what the optimiser may move")
    check("unmodelled sliders are named as held, not tuned",
          "is reported as unmodelled" in skl,
          "Step 5 does not say which sliders it cannot represent")
    check("coverage is required alongside the score",
          "Coverage is part of the result" in skl,
          "a score could be reported without saying how much it covered")
    check("the score is not allowed to claim Lightroom fidelity",
          'Never say "matches Lightroom"' in skl,
          "Step 5 does not bound what the score may be claimed to mean")
    check("chat-only degrades loudly instead of implying a score",
          "Never imply a score you did not measure" in skl,
          "the no-shell case does not state its own limits")
    check("Deliver is Step 6 and carries five parts",
          "## Step 6 — Deliver" in skl and "these five parts" in skl and
          "all five parts are present" in skl,
          "Deliver was not renumbered, or still promises four parts")
    check("the recipe shows what tuning earned",
          re.search(r"seed −8, −0\.4 ΔE", skl),
          "Deliver does not require the seed->tuned delta to be shown")
    check("intake reference is routed",
          re.search(r"\|\s*A vague look word to decompose.*\|\s*`references/11-intake\.md`\s*\|", skl),
          "SKILL.md routing table has no row for references/11-intake.md")

    # BUG (live use): 08-looks.md's own worked recipes built warmth with a
    # negative Yellow Hue — the exact move 09-presets-xmp.md documents as the
    # signature failure. A model routed only to 08-looks.md shipped it.
    colr = read("skills/lightroom-editor/references/02-color.md", pre_fix)
    fx = read("skills/lightroom-editor/references/03-effects.md", pre_fix)
    check("no look recipe builds warmth with a negative Yellow Hue",
          not re.search(r"Yellow Hue\s*[−-]\s*\d", looks),
          "a recipe still drags HueAdjustmentYellow negative, which rotates "
          "yellows to orange and then red")
    check("the warm recipes point at the sign table",
          looks.count("never by dragging `Yellow Hue` negative") >= 2,
          "the warm-look recipes do not warn against the negative Yellow Hue move")

    # BUG (live use): 02-color.md's only Green Hue example was the corrective
    # direction, so the far more common olive/film move was set backwards.
    check("Green Hue documents the creative direction as well as the corrective",
          "Foliage — going the other way" in colr and
          re.search(r"Green Hue\s*[−-]10 to [−-]25", colr),
          "02-color.md still shows only the 'away from yellow-green' direction")
    check("Green Hue states its sign inline",
          "negative Green Hue → toward yellow" in colr,
          "the reader must open another file to decode the Green Hue sign")

    # BUG (live use): 'Size is resolution-relative' with no relationship given,
    # so grain size across a two-body preset family was a guess.
    check("grain Size gives an actual scaling rule",
          "√(MP_target / 24)" in fx,
          "03-effects.md still states the dependency without a formula")
    check("grain Size gives resolution-indexed values",
          "| 12 MP | 24 MP | 48 MP |" in fx.replace(" 60 MP |", ""),
          "no per-resolution grain Size table")

    # BUG (live use): every look route assumed a single source, so building one
    # look for two bodies meant re-deriving the correction/creative split.
    check("a route exists for one look across several sources",
          "## Route 5 — One look, several sources" in looks,
          "08-looks.md has no guidance for preset families")
    check("Route 5 is routed from SKILL.md",
          "a preset family" in skl,
          "SKILL.md routing table does not mention the multi-source case")

    # BUG (live use): Route 1 measured reference images with no word on
    # provenance, leaving the copyright boundary to be re-decided each session.
    check("reference-image provenance boundary is stated",
          "Measure freely; hand back slider values, never the file." in looks,
          "Route 1 does not say measuring is fine but redistribution is not")

    # BUG (live use): the Fidelity gate demanded a number, but the question as
    # asked collects a qualitative bucket, which nothing mapped to a deviation.
    check("Fidelity buckets carry their own numbers",
          "Ask Fidelity with the numbers already attached" in skl and
          "`±3°`" in skl and "`±10°`" in skl,
          "nothing converts a qualitative Fidelity answer into a deviation")

    # BUG (live use): scripts/ was mandatory in Red flags but lived outside the
    # packaged skill, so no install could satisfy the gate.
    check("Step 5 handles an install with no scripts directory",
          "but no `scripts/` directory" in skl,
          "Step 5 branches only on the code environment, not on missing scripts")
    check("the scripts red flag tolerates their absence without faking a check",
          "never report a check you did not run" in skl,
          "the red flag still demands scripts that an install may not carry")

    if not pre_fix:
        for s in ("preset-check.py", "look-match.py", "crs-render.py",
                  "tune.py", "crs-vocabulary.txt"):
            check(f"{s} ships inside the packaged skill",
                  (SKILL / "scripts" / s).exists(),
                  f"{s} is referenced by the skill but outside skills/lightroom-editor/")
        intake = read("skills/lightroom-editor/references/11-intake.md")
        check("11-intake.md carries the decomposition ladders",
              "Moody" in intake and "Cinematic" in intake and "Vintage" in intake,
              "the vague-word ladders are missing")
        check("11-intake.md carries the conflict archetypes",
              "Conflict archetypes" in intake and "8-bit JPEG" in intake and
              "ProRAW" in intake,
              "the Intent-vs-source conflict costs are missing")

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

    # NOTE: this corpus lives outside the repo and is mutable, so it cannot
    # anchor a regression assertion — the immutable anchor for the tone-curve
    # bug is the mutation test in layer 2. What is asserted here is the durable
    # invariant the repair established: no preset carries a curve that
    # Lightroom would discard.
    old = sorted(Path.home().glob("Desktop/creatives/presets/*.xmp"))
    if not old:
        skip("local preset corpus", "no ~/Desktop/creatives/presets on this machine")
    else:
        orphaned = []
        for p in old:
            t = p.read_text()
            if "ToneCurvePV2012" in t and "ToneCurveName2012" not in t:
                orphaned.append(p.name)
        check(f"no preset in the {len(old)}-file corpus has a discarded tone curve",
              not orphaned,
              f"{len(orphaned)} preset(s) carry a curve Lightroom would drop: "
              f"{orphaned[:4]}")
        rc, out = run_check(*old)
        n = re.search(r"(\d+) of (\d+) preset", out)
        remaining = int(n.group(1)) if n else 0
        print(f"          (informational: {remaining}/{len(old)} still fail on "
              f"other grounds — per-photo settings baked into older presets)")


# ---------------------------------------------------------------- layer 4
LOOK = SCRIPTS / "look-match.py"

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
        import numpy  # noqa: F401
    except ImportError:
        skip("look gate (11 checks)",
             "Pillow/numpy not installed — pip install -r tests/requirements.txt")
        return
    import colorsys as _colorsys
    import numpy as _np
    from PIL import Image as _Image
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

        # BUG (found on real photographs): every frame of a warm amber set
        # measured band "Orange" at 85-93%, but its actual hue centre sat at
        # 36-41 deg while the Orange band centre is 30 deg. Reading the band
        # NAME and grading at the band centre landed 6-11 deg too red — the
        # "why is my warm yellow reference coming out orange" failure. The
        # band label names a 30-degree-wide bucket; it is not a target.
        wide = Path(d) / "amber.png"
        _rr = _np.random.default_rng(21)
        _px = [tuple(int(v * 255) for v in
                     _colorsys.hsv_to_rgb(((40 + _rr.normal(0, 7)) % 360) / 360,
                                          0.42, 0.30 + 0.45 * _rr.random()))
               for _ in range(60000)]
        _im = _Image.new("RGB", (300, 200))
        _im.putdata(_px)
        _im.save(wide)

        rc, out = run_look(wide, preset(
            'crs:SplitToningShadowHue="30" crs:ColorGradeMidtoneHue="30" '
            'crs:SaturationAdjustmentOrange="+12" '
            'crs:SaturationAdjustmentYellow="+6"', "bandcentre"))
        check("the reference's hue centre is reported, not just its range",
              "centre" in out and "grade here" in out, out.strip()[-500:])
        check("a grade at the band centre is flagged as off the reference's centre",
              "off the reference's centre" in out and "band's centre" in out,
              out.strip()[-500:])

        rc, out = run_look(wide, preset(
            'crs:SplitToningShadowHue="40" crs:ColorGradeMidtoneHue="40" '
            'crs:SaturationAdjustmentOrange="+12" '
            'crs:SaturationAdjustmentYellow="+6"', "measuredcentre"))
        check("a grade at the measured centre is not flagged",
              rc == 0 and "off the reference's centre" not in out, out.strip()[-500:])

        # REGRESSION: a reference with no dominant hue must not silently skip
        # the Color Grading check and report a clean GREEN. The gate has to
        # say which checks actually ran.
        noise = Path(d) / "noise.png"
        _Image.fromarray(_np.random.default_rng(11)
                        .integers(60, 200, (200, 200, 3), dtype=_np.uint8)).save(noise)
        rc, out = run_look(noise, preset(
            'crs:SplitToningShadowHue="38" crs:SaturationAdjustmentOrange="+8"', "noise"))
        check("a reference with no measurable hue range says the check did not run",
              "NOT MEASURABLE" in out and "did NOT run" in out
              and "hue check could not run" in out,
              out.strip()[-400:])

        # the reference's dominant band must be addressed
        rc, out = run_look(ref, preset('crs:SaturationAdjustmentBlue="-30"', "ignore"))
        check("leaving the dominant band untouched fails",
              rc == 1 and "does not touch it" in out, out.strip()[-300:])


# ---------------------------------------------------------------- layer 5
def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def synth_linear(np):
    """A synthetic linear image: luminance ramp with chroma. No file needed."""
    y, x = np.mgrid[0:48, 0:48]
    lum = (0.02 + 0.96 * (y / 47.0)) ** 2.2
    r = lum * (0.85 + 0.30 * (x / 47.0))
    g = lum * 0.80
    b = lum * (1.15 - 0.30 * (x / 47.0))
    return np.clip(np.stack([r, g, b], axis=-1), 0.0, 1.0)


def layer5_render():
    """Properties the renderer and the tuner must hold regardless of whether
    they agree with Adobe. Adobe fidelity is explicitly NOT claimed (the
    develop math is unpublished), so these are what can honestly be pinned."""
    print("\nLAYER 5 — renderer and tuner invariants")
    try:
        import numpy as np
    except ImportError:
        skip("renderer and tuner invariants (12 checks)",
             "numpy not installed — pip install -r tests/requirements.txt")
        return
    crs = _load("crs_render", SCRIPTS / "crs-render.py")
    tune = _load("tune", SCRIPTS / "tune.py")
    img = synth_linear(np)

    # deterministic: a score you cannot reproduce is not a measurement.
    a = crs.render(img, {"Exposure2012": 0.3, "Blacks2012": 10.0})
    b = crs.render(img, {"Exposure2012": 0.3, "Blacks2012": 10.0})
    check("rendering is deterministic", bool(np.array_equal(a, b)),
          "two identical renders differed")

    # monotonic in the expected direction, per slider.
    base = crs.render(img, {})
    for name, val, probe, direction in [
            ("Exposure2012", 0.5, lambda o: o.mean(), "raises"),
            ("Blacks2012", 40.0, lambda o: o.mean(), "raises"),
            ("Whites2012", 40.0, lambda o: o.mean(), "raises"),
            ("IncrementalTemperature", 50.0, lambda o: o[..., 0].mean(), "raises"),
            ("IncrementalTint", 50.0, lambda o: o[..., 1].mean(), "lowers")]:
        out = crs.render(img, {name: val})
        moved = probe(out) - probe(base)
        ok = moved > 1e-6 if direction == "raises" else moved < -1e-6
        check(f"{name} {direction} its measure monotonically", ok,
              f"moved by {moved:+.6f}, expected to {direction[:-1]}")

    # an image scored against itself is a perfect match, or the metric is broken.
    enc = crs.render(img, {})
    mean_de, worst = tune.score_against_reference(enc, tune.zone_means(enc))
    check("an image scored against itself returns zero dE",
          mean_de < 1e-6 and worst < 1e-6, f"mean {mean_de:.6f}, worst {worst:.6f}")

    # dE2000 against a known-different colour must be non-trivial and symmetric.
    d1 = tune.delta_e_2000((50.0, 2.6, -79.7), (50.0, 0.0, -82.7))
    d2 = tune.delta_e_2000((50.0, 0.0, -82.7), (50.0, 2.6, -79.7))
    check("dE2000 is symmetric and non-degenerate",
          abs(d1 - d2) < 1e-9 and 0.5 < d1 < 10.0, f"{d1:.4f} vs {d2:.4f}")

    # the optimiser may never leave its bounds, even chasing an unbounded score.
    greedy = lambda o: (-float(o.mean()), 0.0)     # rewards infinite brightness
    p, m, w, iters, why = tune.tune(img, {}, greedy)
    out_of_bounds = [k for k, v in p.items()
                     if not (tune.PARAMS[k][0] - 1e-9 <= v <= tune.PARAMS[k][1] + 1e-9)]
    check("the optimiser never leaves its bounds", not out_of_bounds,
          f"out of bounds: {out_of_bounds}")
    check("the optimiser terminates within the cap",
          iters <= tune.MAX_ITERS, f"ran {iters} iterations")
    check("termination reports why it stopped",
          why in ("plateaued", "reached the gate", "hit the iteration cap"), why)

    # tuning must never return a worse result than the seed it started from.
    target = crs.render(img, {"Exposure2012": 0.25, "IncrementalTemperature": 15.0})
    zones = tune.zone_means(target)
    obj = lambda o: tune.score_against_reference(o, zones)
    seed_mean, _ = obj(crs.render(img, {}))
    p2, tuned_mean, _, _, _ = tune.tune(img, {}, obj)
    check("the best score never worsens against the seed",
          tuned_mean <= seed_mean + 1e-9,
          f"seed {seed_mean:.4f} -> tuned {tuned_mean:.4f}")
    check("tuning measurably closes a known gap",
          tuned_mean < seed_mean, f"no improvement: {seed_mean:.4f} -> {tuned_mean:.4f}")

    # the printed percentage must follow the formula the docs state.
    check("the percentage follows its stated formula",
          abs(tune.as_percent(1.0) - 90.0) < 1e-9 and abs(tune.as_percent(0.2) - 98.0) < 1e-9,
          f"dE 1.0 -> {tune.as_percent(1.0)}, dE 0.2 -> {tune.as_percent(0.2)}")

    # coverage must count what the renderer cannot represent.
    moved, modelled = crs.moved_sliders(
        {"Exposure2012": "+0.30", "Clarity2012": "+12", "Dehaze": "+8",
         "Contrast2012": "0", "UUID": "A" * 32})
    check("coverage counts unmodelled sliders as unverified",
          set(moved) == {"Exposure2012", "Clarity2012", "Dehaze"}
          and modelled == ["Exposure2012"],
          f"moved={moved} modelled={modelled}")

    # BUG: the tuner wrote its tuned Exposure into the .xmp, so every preset it
    # produced carried one photo's exposure correction — the portability
    # failure the skill's own red flag forbids.
    with tempfile.TemporaryDirectory() as d:
        seed = Path(d) / "seed.xmp"
        seed.write_text(PRESET.format(
            attrs='crs:IncrementalTemperature="+0" crs:IncrementalTint="+0" '
                  'crs:Exposure2012="+0.00" crs:Blacks2012="+0" '
                  'crs:Whites2012="+0" crs:Clarity2012="+12"'))
        out = Path(d) / "tuned.xmp"
        base, _ = crs.parse_settings(seed)
        tune.write_tuned(seed, out, base,
                         {"IncrementalTemperature": 40.0, "IncrementalTint": -10.0,
                          "Exposure2012": 0.6, "Blacks2012": 8.0, "Whites2012": 12.0})
        written = out.read_text()
        check("the tuned preset never carries per-photo settings",
              all(f"crs:{k}=" not in written for k in tune.PER_PHOTO),
              f"per-photo settings survived into the preset: {written}")
        check("the tuned preset carries the tuned portable values",
              'crs:IncrementalTemperature="+40"' in written
              and 'crs:Whites2012="+12"' in written,
              "portable tuned values were not written back")
        check("the tuned preset preserves unmodelled sliders untouched",
              'crs:Clarity2012="+12"' in written,
              "an unmodelled slider was altered or dropped by the tuner")

    # BUG: coverage was read off the seed, so a recipe whose modelled sliders
    # started at zero reported "0 of N verified" however much the loop tuned.
    seeded = {"Clarity2012": "+12", "IncrementalTemperature": "0"}
    seeded.update({"IncrementalTemperature": "60", "Whites2012": "12"})
    moved2, modelled2 = crs.moved_sliders(seeded)
    check("coverage credits sliders the tuner moved off zero",
          set(modelled2) == {"IncrementalTemperature", "Whites2012"},
          f"modelled={modelled2}; tuned sliders were not counted as verified")


# ---------------------------------------------------------------- layer 6
# The measurement core. Every check here is ground truth: either a published
# CIELAB value, or a known transform applied to a synthetic image which the
# core must recover. Nothing is asserted against a number this repo invented.

STATS = SCRIPTS / "lookstats.py"


def load_lookstats():
    spec = importlib.util.spec_from_file_location("lookstats", STATS)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# CIE L*a*b* (D65, 2 deg observer) for the sRGB primaries. These are published
# reference values, not measurements taken from this code — they are what any
# correct sRGB->CIELAB implementation must produce.
PUBLISHED_LAB = {
    "white": ((1.0, 1.0, 1.0), (100.0, 0.0, 0.0)),
    "red":   ((1.0, 0.0, 0.0), (53.2408, 80.0925, 67.2032)),
    "green": ((0.0, 1.0, 0.0), (87.7347, -86.1827, 83.1793)),
    "blue":  ((0.0, 0.0, 1.0), (32.2970, 79.1875, -107.8602)),
}


def layer6_lookstats():
    print("\nLAYER 6 — measurement core (lookstats)")
    try:
        import numpy as np
        from PIL import Image
    except ImportError:
        skip("measurement core", "numpy/Pillow not installed")
        return
    import colorsys
    ls = load_lookstats()

    # --- colour conversion, pinned to published values -------------------
    worst, detail = 0.0, ""
    for name, (rgb, want) in PUBLISHED_LAB.items():
        got = ls.rgb_to_lab(np.array([rgb], dtype=np.float64))[0]
        err = max(abs(g - w) for g, w in zip(got, want))
        if err > worst:
            worst, detail = err, f"{name}: got {tuple(round(float(v), 4) for v in got)}, published {want}"
    check("sRGB primaries convert to the published CIELAB values",
          worst < 0.05, detail)

    # The thresholds must be what their stated derivation produces. Written
    # after a hand-typed literal was found to be wrong by 2.1 chroma units:
    # a constant nobody can recompute is a constant that drifts.
    dc, dl = ls.derive_floors()
    check("the hue floors match their stated derivation",
          abs(dc - ls.CHROMA_FLOOR) < 5e-4 and abs(dl - ls.L_FLOOR) < 5e-4,
          f"CHROMA_FLOOR literal {ls.CHROMA_FLOOR} vs derived {dc:.4f}; "
          f"L_FLOOR literal {ls.L_FLOOR} vs derived {dl:.4f}")

    # Not exactly zero, and it cannot be: the published sRGB->XYZ matrix is
    # rounded to seven decimals, so its Y row sums to 1.0000001 rather than 1.
    # That 1e-7 excess propagates to about 1e-5 of a*. Anything larger would
    # mean a genuinely skewed matrix, which is what this bound catches.
    grey = ls.rgb_to_lab(np.array([(0.5, 0.5, 0.5)], dtype=np.float64))[0]
    check("mid grey sits on the neutral axis",
          abs(grey[1]) < 1e-4 and abs(grey[2]) < 1e-4,
          f"grey measured a*={grey[1]:.6f} b*={grey[2]:.6f} — a neutral input "
          "must not carry colour beyond the matrix's own rounding")

    with tempfile.TemporaryDirectory() as d:
        # --- weight follows chroma, not HSV saturation -------------------
        # Both halves have HSV S=0.5, so the old S-weighted path scores them
        # equally. A light orange carries far more actual colour than a dark
        # desaturated blue, and Lab chroma says so.
        p = Path(d) / "chroma.png"
        im = Image.new("RGB", (200, 200))
        px = []
        for y in range(200):
            for x in range(200):
                h, s, v = (40 / 360, 0.5, 0.9) if x < 100 else (200 / 360, 0.5, 0.25)
                r, g, b = colorsys.hsv_to_rgb(h, s, v)
                px.append((round(r * 255), round(g * 255), round(b * 255)))
        im.putdata(px)
        im.save(p)
        prof = ls.band_profile(ls.load_rgb(p))
        check("colour weight follows Lab chroma, not HSV saturation",
              prof["Orange"] > 2 * prof["Aqua"],
              f"Orange {prof['Orange']:.1f}% vs Aqua {prof['Aqua']:.1f}% — "
              "equal shares mean the weight is still HSV S")

        # --- downsampling must not invent hues ---------------------------
        # 2px red/blue stripes. Any averaging filter blends them into magenta,
        # a hue present nowhere in the file.
        p = Path(d) / "stripes.png"
        im = Image.new("RGB", (1200, 1200))
        im.putdata([(255, 0, 0) if (x // 2) % 2 == 0 else (0, 0, 255)
                    for _ in range(1200) for x in range(1200)])
        im.save(p)
        prof = ls.band_profile(ls.load_rgb(p, max_pixels=10_000))
        invented = prof["Magenta"] + prof["Purple"]
        check("downsampling does not invent hues at a hard edge",
              invented < 1.0 and prof["Red"] > 30 and prof["Blue"] > 30,
              f"Red {prof['Red']:.1f}% Blue {prof['Blue']:.1f}% "
              f"Magenta+Purple {invented:.1f}% — the file contains only red and blue")

        # --- round-trip ground truth -------------------------------------
        # Build images FROM known Lab values and require the core to recover
        # them. lab_to_srgb below is the inverse of the conversion pinned to
        # published values above, and the first check proves the inverse.
        def lab_to_srgb(L, a, b):
            fy = (L + 16.0) / 116.0
            fx, fz = fy + a / 500.0, fy - b / 200.0
            d = 6.0 / 29.0
            finv = lambda t: t ** 3 if t > d else 3 * d * d * (t - 4.0 / 29.0)
            xyz = ls.D65 * np.array([finv(fx), finv(fy), finv(fz)])
            lin = xyz @ np.linalg.inv(ls.SRGB_TO_XYZ).T
            return ls.linear_to_srgb(np.clip(lin, 0, 1))

        want = (52.0, -2.8, 0.4)
        back = ls.rgb_to_lab(np.array([lab_to_srgb(*want)]))[0]
        check("the test's Lab inverse round-trips through the pinned forward",
              max(abs(g - w) for g, w in zip(back, want)) < 1e-6,
              f"round-trip gave {tuple(round(float(v), 5) for v in back)}, wanted {want}")

        def solid(path, L, a, b, size=200):
            v = np.clip(np.round(lab_to_srgb(L, a, b) * 255), 0, 255).astype(np.uint8)
            im = Image.new("RGB", (size, size), tuple(int(x) for x in v))
            im.save(path)
            return path

        # --- cast: recovered when neutrals exist, refused when they do not -
        p = Path(d) / "cast.png"
        cast = ls.measure_cast(ls.load_rgb(solid(p, 52.0, -2.8, 0.4)))
        check("a known cast is recovered from near-neutral content",
              cast is not None and abs(cast["a"] + 2.8) < 0.6 and abs(cast["b"] - 0.4) < 0.6,
              f"measured {cast}, built from a*=-2.8 b*=+0.4")

        p = Path(d) / "nocast.png"
        # A fully saturated red frame: nothing in it is near neutral, so there
        # is no cast to be read and the engine must say so rather than guess.
        Image.new("RGB", (200, 200), (255, 0, 0)).save(p)
        check("cast measurement abstains when nothing is near neutral",
              ls.measure_cast(ls.load_rgb(p)) is None,
              "a frame with no neutral content returned a cast figure")

        # The doctrine case: a forest is not a green cast. Varied foliage
        # greens, no neutral content. Gray-world would call this a heavy green
        # cast and prescribe a magenta correction that ruins the picture.
        p = Path(d) / "foliage.png"
        rng = np.random.default_rng(7)
        greens = np.stack([rng.uniform(0.10, 0.35, 40000),
                           rng.uniform(0.35, 0.70, 40000),
                           rng.uniform(0.08, 0.30, 40000)], axis=1)
        Image.fromarray((np.clip(greens, 0, 1) * 255).astype(np.uint8)
                        .reshape(200, 200, 3)).save(p)
        got = ls.measure_cast(ls.load_rgb(p))
        check("a forest is not reported as a green cast",
              got is None,
              f"foliage returned {got} — gray-world would prescribe magenta "
              "against a scene that is simply green")

        # --- black point: a known lift in linear light --------------------
        p = Path(d) / "lift.png"
        lift = 0.05
        ramp = np.linspace(0.0, 1.0, 512) * (1 - lift) + lift
        rows = ls.linear_to_srgb(np.repeat(ramp[:, None], 3, axis=1))
        im = Image.fromarray(np.clip(np.round(rows * 255), 0, 255)
                             .astype(np.uint8)[None, :, :].repeat(512, axis=0))
        im.save(p)
        bp = ls.black_point(ls.load_rgb(p))
        check("a known black lift is recovered in linear light",
              abs(bp - lift) < 0.01, f"measured black point {bp:.4f}, built with {lift}")

        # --- hue range stays in RGB-wheel degrees -------------------------
        # The unit must match crs: hue attributes, so a 40 deg reference must
        # measure ~40, not its Lab hue angle (which is nearer 60).
        p = Path(d) / "amber.png"
        golden_ref(p, hue_deg=40)
        lo, hi = ls.hue_range(ls.load_rgb(p))
        check("hue range is measured in RGB-wheel degrees",
              36 <= lo <= 42 and 38 <= hi <= 44,
              f"a 40 deg reference measured {lo:.1f}-{hi:.1f} deg")

        p = Path(d) / "gold.png"
        golden_ref(p, hue_deg=52)
        lo2, hi2 = ls.hue_range(ls.load_rgb(p))
        check("hue range tracks a known 12 deg shift",
              abs(((lo2 + hi2) / 2 - (lo + hi) / 2) - 12) < 2.0,
              f"40 deg ref measured {(lo+hi)/2:.1f}, 52 deg ref measured {(lo2+hi2)/2:.1f}")

        # --- a hue range nothing supports must not be reported ------------
        # look-match FAILS presets on this number, so an unstable one produces
        # random verdicts. Hue-less noise has no hue range; saying so beats
        # returning bounds that move 85 deg between samples.
        p = Path(d) / "huelessnoise.png"
        rr = np.random.default_rng(11)
        Image.fromarray(rr.integers(60, 200, (200, 200, 3), dtype=np.uint8)).save(p)
        check("a frame with no coherent hue reports no hue range",
              ls.hue_range(ls.load_rgb(p)) is None,
              f"returned {ls.hue_range(ls.load_rgb(p))} for uniform noise")

        # And the flip side: whatever DOES pass the concentration gate has to
        # be stable, or the gate is still deciding on noise. This is the
        # property HUE_CONCENTRATION_MIN was derived to guarantee.
        p = Path(d) / "spread.png"
        rr = np.random.default_rng(12)
        px = [tuple(int(v * 255) for v in
                    colorsys.hsv_to_rgb(((48 + rr.normal(0, 45)) % 360) / 360, 0.5, 0.5))
              for _ in range(40000)]
        im = Image.new("RGB", (200, 200))
        im.putdata(px)
        im.save(p)
        rs = [ls.hue_range(ls.load_rgb(p, max_pixels=8000, seed=k)) for k in range(10)]
        drift = 0.0 if any(r is None for r in rs) else max(
            max(x[0] for x in rs) - min(x[0] for x in rs),
            max(x[1] for x in rs) - min(x[1] for x in rs))
        check("a reported hue range is stable to within the gate's tolerance",
              drift < 3.0,
              f"bounds moved {drift:.2f} deg across ten samples, more than the "
              "3 deg TOLERANCE the gate judges against")

        # --- zones separate the grade by tone -----------------------------
        p = Path(d) / "zones.png"
        top = np.clip(np.round(lab_to_srgb(25.0, 4.0, 14.0) * 255), 0, 255).astype(np.uint8)
        bot = np.clip(np.round(lab_to_srgb(80.0, -2.0, -12.0) * 255), 0, 255).astype(np.uint8)
        arr = np.zeros((200, 200, 3), dtype=np.uint8)
        arr[:100], arr[100:] = top, bot
        Image.fromarray(arr).save(p)
        zs = [z for z in ls.zones(ls.load_rgb(p)) if z["share"] > 0]
        check("zones report the cast of each tonal region separately",
              zs[0]["b"] > 8 and zs[-1]["b"] < -8,
              f"darkest zone b*={zs[0]['b']:.1f} (built +14), "
              f"brightest b*={zs[-1]['b']:.1f} (built -12)")

        # --- ITA follows its published definition -------------------------
        # ITA = arctan((L* - 50) / b*) in degrees (Del Bino & Bernerd).
        check("ITA follows its published definition",
              abs(ls.ita(70.0, 20.0) - 45.0) < 1e-9,
              f"ita(L=70, b=20) returned {ls.ita(70.0, 20.0)}, must be 45")

        # --- skin: one warm population reads, two refuse ------------------
        p = Path(d) / "skin.png"
        solid(p, 65.0, 12.0, 18.0)
        want_ita = ls.ita(65.0, 18.0)
        # Withheld by default: on real warm-graded frames this reported a
        # flatly wrong tone as fact on six of eight images.
        check("skin tone is withheld by default and says why",
              not ls.skin(ls.load_rgb(p))["ok"]
              and "colour alone cannot locate a face" in ls.skin(ls.load_rgb(p))["reason"],
              f"{ls.skin(ls.load_rgb(p))}")
        got = ls.skin(ls.load_rgb(p), allow_unreliable=True)
        check("the underlying measurement is still correct when opted into",
              got["ok"] and abs(got["ita"] - want_ita) < 1.5,
              f"measured {got}, built from L=65 b=18 (ITA {want_ita:.1f})")

        # A face against a wooden wall: two warm populations, far apart in
        # hue. Without a face detector nothing here can say which is skin, so
        # the engine must decline rather than average them into a number.
        p = Path(d) / "skin-wall.png"
        face = np.clip(np.round(lab_to_srgb(65.0, 12.0, 18.0) * 255), 0, 255).astype(np.uint8)
        wood = np.clip(np.round(lab_to_srgb(50.0, 8.0, 40.0) * 255), 0, 255).astype(np.uint8)
        arr = np.zeros((200, 200, 3), dtype=np.uint8)
        arr[:100], arr[100:] = face, wood
        Image.fromarray(arr).save(p)
        got = ls.skin(ls.load_rgb(p), allow_unreliable=True)
        check("skin measurement refuses two separated warm populations",
              not got["ok"] and "spread" in got["reason"],
              f"returned {got} — a face and a wooden wall cannot be told apart "
              "by colour alone, so no figure should be given")

        # --- the Tint probe is proven by round trip -----------------------
        # No published CIELAB-to-Tint mapping exists, so the mapping is
        # measured off this file with crs-render and then required to WORK:
        # apply the Tint it derives, and the cast it was derived from must go.
        spec = importlib.util.spec_from_file_location(
            "crs_render", SCRIPTS / "crs-render.py")
        crs = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(crs)

        p = Path(d) / "greencast.png"
        solid(p, 55.0, -3.0, 0.0)
        lin, _ = crs.load_image(p)
        before = ls.measure_cast(crs.linear_to_srgb(lin).reshape(-1, 3))
        tint = ls.probe_tint(crs, lin)
        after = ls.measure_cast(
            crs.linear_to_srgb(crs.render(lin, {"IncrementalTint": tint}))
            .reshape(-1, 3))
        check("the probed Tint neutralises the cast it was derived from",
              after is not None and abs(after["a"]) < 0.5,
              f"cast a* {before['a']:.2f} -> Tint {tint:+.1f} -> "
              f"a* {after['a'] if after else None}")


# ---------------------------------------------------------------- layer 7
ANALYZE = SCRIPTS / "look-analyze.py"


def run_analyze(*args):
    r = subprocess.run([sys.executable, str(ANALYZE), *map(str, args)],
                       capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def layer7_analyze():
    print("\nLAYER 7 — look-analyze front door")
    try:
        import numpy as np
        from PIL import Image
    except ImportError:
        skip("look-analyze front door (4 checks)", "Pillow/numpy not installed")
        return
    with tempfile.TemporaryDirectory() as d:
        ref = Path(d) / "ref.png"
        golden_ref(ref, hue_deg=40)
        rc, out = run_analyze(ref)
        check("the report prints bands, hue range, black point and zones",
              rc == 0 and all(k in out for k in
                              ("band", "hue range", "black point", "zone", "Orange")),
              out.strip()[-400:])

        # A refusal must be visible in the verdict, not buried.
        rc, out = run_analyze("--source", ref)
        check("a source with no neutral content withholds the cast and says so",
              rc == 0 and "WITHHELD" in out and "AMBER" in out,
              out.strip()[-400:])

        # And the fallback must name what it is falling back to.
        rc, out = run_analyze("--source", ref, "--profile", "Sony ARW, green bias")
        check("the withheld cast names the profile it falls back to",
              "Sony ARW, green bias" in out and "UNMEASURED" in out,
              out.strip()[-400:])

        grey = Path(d) / "grey.png"
        Image.new("RGB", (200, 200), (128, 130, 128)).save(grey)
        rc, out = run_analyze("--source", grey)
        check("a source with neutral content reports a measured cast",
              rc == 0 and "measured cast" in out and "WITHHELD" not in out.split("band")[0],
              out.strip()[-400:])


def main():
    if "--pre-fix" in sys.argv:
        layer1_document(pre_fix=True)
    else:
        layer1_document()
        layer2_mutations()
        layer3_corpora()
        layer4_look()
        layer5_render()
        layer6_lookstats()
        layer7_analyze()
    passed = sum(1 for _, ok, _ in results if ok)
    total = len(results)
    tail = f"  ({len(skipped)} skipped)" if skipped else ""
    print(f"\n{'GREEN' if passed == total else 'RED'} — {passed}/{total} checks passed{tail}")
    for name, why in skipped:
        print(f"  skipped: {name} — {why}")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
