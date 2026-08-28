#!/usr/bin/env python3
"""Preset validator for generated Lightroom .xmp files.

RED (exit 1) if a preset would silently misbehave in Lightroom.
Catches the failure class where Lightroom imports the file without error
but drops settings on the floor: unknown crs: attribute names, values
outside a slider's real range, a custom curve with no ToneCurveName2012,
a reused UUID, or per-photo settings that break portability.

Usage: scripts/preset-check.py FILE.xmp [FILE.xmp ...]
"""
import re, sys, xml.etree.ElementTree as ET
from pathlib import Path

CRS = "http://ns.adobe.com/camera-raw-settings/1.0/"
ROOT = Path(__file__).resolve().parent.parent
VOCAB = ROOT / "scripts" / "crs-vocabulary.txt"

# Slider ranges as Camera Raw actually clamps them. Anything outside is a
# value the user typed by hand that Lightroom will silently clip.
BAND = "Red Orange Yellow Green Aqua Blue Purple Magenta".split()
RANGES = {}
for k in ("Contrast2012 Highlights2012 Shadows2012 Whites2012 Blacks2012 "
          "Texture Clarity2012 Dehaze Vibrance Saturation SplitToningBalance "
          "ColorGradeShadowLum ColorGradeMidtoneLum ColorGradeHighlightLum "
          "ColorGradeGlobalLum PostCropVignetteAmount PostCropVignetteRoundness").split():
    RANGES[k] = (-100, 100)
for b in BAND:
    for p in ("HueAdjustment", "SaturationAdjustment", "LuminanceAdjustment", "GrayMixer"):
        RANGES[p + b] = (-100, 100)
for k in ("SplitToningShadowHue SplitToningHighlightHue ColorGradeMidtoneHue "
          "ColorGradeGlobalHue").split():
    RANGES[k] = (0, 360)
for k in ("SplitToningShadowSaturation SplitToningHighlightSaturation "
          "ColorGradeMidtoneSat ColorGradeGlobalSat ColorGradeBlending "
          "SharpenDetail SharpenEdgeMasking LuminanceSmoothing "
          "LuminanceNoiseReductionDetail LuminanceNoiseReductionContrast "
          "ColorNoiseReduction ColorNoiseReductionDetail "
          "ColorNoiseReductionSmoothness GrainAmount GrainSize GrainFrequency "
          "PostCropVignetteMidpoint PostCropVignetteFeather").split():
    RANGES[k] = (0, 100)
RANGES["Sharpness"] = (0, 150)
RANGES["SharpenRadius"] = (0.5, 3.0)
RANGES["Exposure2012"] = (-5.0, 5.0)
RANGES["Temperature"] = (2000, 50000)
RANGES["Tint"] = (-150, 150)

# House limits from SKILL.md. Exceeding one is not invalid XMP — it is the
# skill breaking its own restraint rule, which is what "looks overcooked" is.
HOUSE = {"Clarity2012": 15, "Dehaze": 10}

NOT_PORTABLE = {"Exposure2012", "Temperature", "Tint"}


def load_vocab():
    if not VOCAB.exists():
        sys.exit(f"missing vocabulary file: {VOCAB}")
    return {l.strip() for l in VOCAB.read_text().splitlines()
            if l.strip() and not l.startswith("#")}


def num(v):
    try:
        return float(v)
    except ValueError:
        return None


def check(path, vocab, seen_uuids):
    fails = []
    warns = []
    try:
        tree = ET.parse(path)
    except ET.ParseError as e:
        return [f"not well-formed XML: {e}"], []
    root = tree.getroot()

    desc = root.find(f".//{{{CRS}}}Look/..")
    descs = [e for e in root.iter() if e.tag.endswith("Description")]
    if not descs:
        fails.append("no rdf:Description element")
        return fails, warns
    top = descs[0]

    # 1. every crs: attribute name must be a real Camera Raw attribute
    for k, v in top.attrib.items():
        if not k.startswith(f"{{{CRS}}}"):
            continue
        name = k.split("}")[1]
        if name not in vocab:
            fails.append(f"unknown crs attribute {name!r} — Lightroom drops it silently")
            continue
        lo_hi = RANGES.get(name)
        n = num(v.lstrip("+"))
        if lo_hi and n is not None and not (lo_hi[0] <= n <= lo_hi[1]):
            fails.append(f"{name}={v} outside Camera Raw range {lo_hi[0]}..{lo_hi[1]}")
        if name in HOUSE and n is not None and abs(n) > HOUSE[name]:
            warns.append(f"{name}={v} exceeds the skill's house limit of {HOUSE[name]}")
        if name in NOT_PORTABLE:
            fails.append(f"{name} is per-photo — a portable preset must omit it")

    # 2. custom curve present but curve mode not set -> curve is ignored
    curve = top.find(f"{{{CRS}}}ToneCurvePV2012")
    pts = []
    if curve is not None:
        pts = [li.text.strip() for li in curve.iter()
               if li.tag.endswith("li") and li.text]
    nontrivial = [p for p in pts if p not in ("0, 0", "255, 255")]
    mode = top.get(f"{{{CRS}}}ToneCurveName2012")
    if nontrivial and mode != "Custom":
        fails.append(f'custom tone curve present but ToneCurveName2012={mode!r} '
                     "— Lightroom ignores the curve")

    # 3. curve points must be int pairs on 0..255, strictly increasing in x
    for cname in ("ToneCurvePV2012", "ToneCurvePV2012Red",
                  "ToneCurvePV2012Green", "ToneCurvePV2012Blue"):
        el = top.find(f"{{{CRS}}}{cname}")
        if el is None:
            continue
        xs = []
        for li in el.iter():
            if not li.tag.endswith("li") or not li.text:
                continue
            m = re.fullmatch(r"\s*(\d+),\s*(\d+)\s*", li.text)
            if not m:
                fails.append(f"{cname}: malformed point {li.text.strip()!r} "
                             "(want 'in, out')")
                continue
            x, y = int(m.group(1)), int(m.group(2))
            if not (0 <= x <= 255 and 0 <= y <= 255):
                fails.append(f"{cname}: point {x},{y} outside 0..255")
            xs.append(x)
        if xs != sorted(set(xs)):
            fails.append(f"{cname}: input values not strictly increasing: {xs}")

    # 4. UUID must be fresh 32-hex uppercase, unique across the run
    uuid = top.get(f"{{{CRS}}}UUID")
    if uuid is None:
        warns.append("no crs:UUID")
    elif not re.fullmatch(r"[0-9A-F]{32}", uuid):
        fails.append(f"crs:UUID={uuid!r} is not 32 uppercase hex characters")
    elif uuid in seen_uuids:
        fails.append(f"crs:UUID {uuid} reused — Lightroom treats these as one preset")
    else:
        seen_uuids.add(uuid)

    # 5. a preset must announce itself as one
    if top.get(f"{{{CRS}}}PresetType") is None:
        warns.append("no crs:PresetType — may import as a settings file, not a preset")

    return fails, warns


def main():
    files = sys.argv[1:]
    if not files:
        sys.exit(__doc__)
    vocab, seen, bad = load_vocab(), set(), 0
    for f in files:
        fails, warns = check(f, vocab, seen)
        status = "RED " if fails else "green"
        print(f"{status} {f}")
        for m in fails:
            print(f"    FAIL: {m}")
        for m in warns:
            print(f"    warn: {m}")
        bad += bool(fails)
    print()
    print(f"RED — {bad} of {len(files)} preset(s) would misbehave" if bad
          else f"GREEN — {len(files)} preset(s) valid")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
