#!/usr/bin/env python3
"""Score a rendered recipe, and tune the modellable sliders toward the target.

Scoring is CIEDE2000, computed between TONAL ZONES rather than pixel-for-pixel:
a reference image is usually a different photograph, so a pixel-wise comparison
would measure the difference in subject, not in grade. Both images are bucketed
by luminance into zones, and the zone mean colours are compared. That measures
the grade and ignores the content, which is the thing being asked.

  gate:  mean dE00 <= 1.0 with no zone above 2.0
         (the published perceptibility thresholds: <1 imperceptible,
          1-2 perceptible on close inspection, >2 obvious)

A percentage is printed for readability, by the stated formula
`100 * max(0, 1 - mean_dE / 10)`. It is a convenience, not the gate. There is
no standard convention mapping dE to a percentage, so the number means only
what that formula says it means.

Only the sliders scripts/crs-render.py can model are tuned. Everything else
holds what the recipe chose and is reported as unmodelled.

Usage:
  scripts/tune.py SOURCE.ARW PRESET.xmp --reference REF.jpg [--out TUNED.xmp]
  scripts/tune.py SOURCE.jpg PRESET.xmp            # no reference: correctness targets
  scripts/tune.py SOURCE.ARW PRESET.xmp --reference REF.jpg --warmer 8
"""
import argparse, importlib.util, math, sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location(
    "crs_render", ROOT / "scripts" / "crs-render.py")
crs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(crs)

ZONES = 9
GATE_MEAN = 1.0
GATE_WORST = 2.0
MAX_ITERS = 12
PLATEAU_ROUNDS = 3
PLATEAU_EPS = 0.01

# name -> (low, high, step). These are the only controls the renderer models,
# so they are the only ones the optimiser may move. The skill's house limits
# live on sliders that are not in this table and therefore cannot be crossed.
PARAMS = {
    "IncrementalTemperature": (-100.0, 100.0, 5.0),
    "IncrementalTint":        (-100.0, 100.0, 5.0),
    "Exposure2012":           (-2.0, 2.0, 0.10),
    "Blacks2012":             (-100.0, 100.0, 4.0),
    "Whites2012":             (-100.0, 100.0, 4.0),
    "CurveStrength":          (0.0, 1.5, 0.10),
}


# ------------------------------------------------------------------ CIELAB
def to_lab(srgb):
    """sRGB in [0,1] -> CIELAB (D65)."""
    lin = crs.srgb_to_linear(np.clip(srgb, 0.0, 1.0))
    m = np.array([[0.4124564, 0.3575761, 0.1804375],
                  [0.2126729, 0.7151522, 0.0721750],
                  [0.0193339, 0.1191920, 0.9503041]])
    xyz = lin @ m.T / np.array([0.95047, 1.0, 1.08883])
    e, k = 216 / 24389, 24389 / 27
    f = np.where(xyz > e, np.cbrt(xyz), (k * xyz + 16) / 116)
    return np.stack([116 * f[..., 1] - 16,
                     500 * (f[..., 0] - f[..., 1]),
                     200 * (f[..., 1] - f[..., 2])], axis=-1)


def delta_e_2000(lab1, lab2):
    """CIEDE2000 between two Lab triples (Sharma/Wu/Dalal formulation)."""
    L1, a1, b1 = lab1
    L2, a2, b2 = lab2
    C1, C2 = math.hypot(a1, b1), math.hypot(a2, b2)
    Cb = (C1 + C2) / 2
    G = 0.5 * (1 - math.sqrt(Cb ** 7 / (Cb ** 7 + 25 ** 7))) if Cb > 0 else 0.5
    a1p, a2p = (1 + G) * a1, (1 + G) * a2
    C1p, C2p = math.hypot(a1p, b1), math.hypot(a2p, b2)
    h1p = math.degrees(math.atan2(b1, a1p)) % 360 if (a1p or b1) else 0.0
    h2p = math.degrees(math.atan2(b2, a2p)) % 360 if (a2p or b2) else 0.0

    dLp = L2 - L1
    dCp = C2p - C1p
    if C1p * C2p == 0:
        dhp = 0.0
    elif abs(h2p - h1p) <= 180:
        dhp = h2p - h1p
    else:
        dhp = h2p - h1p - 360 if h2p > h1p else h2p - h1p + 360
    dHp = 2 * math.sqrt(C1p * C2p) * math.sin(math.radians(dhp) / 2)

    Lbp = (L1 + L2) / 2
    Cbp = (C1p + C2p) / 2
    if C1p * C2p == 0:
        hbp = h1p + h2p
    elif abs(h1p - h2p) <= 180:
        hbp = (h1p + h2p) / 2
    elif h1p + h2p < 360:
        hbp = (h1p + h2p + 360) / 2
    else:
        hbp = (h1p + h2p - 360) / 2

    T = (1 - 0.17 * math.cos(math.radians(hbp - 30))
         + 0.24 * math.cos(math.radians(2 * hbp))
         + 0.32 * math.cos(math.radians(3 * hbp + 6))
         - 0.20 * math.cos(math.radians(4 * hbp - 63)))
    dTh = 30 * math.exp(-(((hbp - 275) / 25) ** 2))
    Rc = 2 * math.sqrt(Cbp ** 7 / (Cbp ** 7 + 25 ** 7)) if Cbp > 0 else 0.0
    Sl = 1 + (0.015 * (Lbp - 50) ** 2) / math.sqrt(20 + (Lbp - 50) ** 2)
    Sc = 1 + 0.045 * Cbp
    Sh = 1 + 0.015 * Cbp * T
    Rt = -math.sin(math.radians(2 * dTh)) * Rc

    return math.sqrt((dLp / Sl) ** 2 + (dCp / Sc) ** 2 + (dHp / Sh) ** 2
                     + Rt * (dCp / Sc) * (dHp / Sh))


# ------------------------------------------------------------------ scoring
def zone_means(srgb):
    """Mean Lab of each luminance zone. Content-independent grade signature."""
    lab = to_lab(srgb).reshape(-1, 3)
    edges = np.linspace(0, 100, ZONES + 1)
    idx = np.clip(np.digitize(lab[:, 0], edges[1:-1]), 0, ZONES - 1)
    out = []
    for z in range(ZONES):
        sel = lab[idx == z]
        out.append(tuple(sel.mean(axis=0)) if len(sel) else None)
    return out


def rotate_chroma(lab_zones, degrees):
    """Apply a stated Fidelity deviation, so intent is scored, not fidelity."""
    if not degrees:
        return lab_zones
    r = math.radians(degrees)
    cos_r, sin_r = math.cos(r), math.sin(r)
    out = []
    for z in lab_zones:
        if z is None:
            out.append(None)
        else:
            L, a, b = z
            out.append((L, a * cos_r - b * sin_r, a * sin_r + b * cos_r))
    return out


def score_against_reference(rendered, ref_zones):
    got = zone_means(rendered)
    ds = [delta_e_2000(g, r) for g, r in zip(got, ref_zones) if g and r]
    if not ds:
        return float("inf"), float("inf")
    return float(np.mean(ds)), float(max(ds))


def score_against_targets(rendered):
    """No reference: measurable correctness.

    Near-neutral content should be neutral, the endpoints should not clip.
    Reported on the same dE scale so one gate covers both objectives.
    """
    lab = to_lab(rendered).reshape(-1, 3)
    chroma = np.hypot(lab[:, 1], lab[:, 2])
    near = lab[chroma < 12]
    if len(near) < 32:
        near = lab[np.argsort(chroma)[:max(32, len(lab) // 50)]]
    cast = [delta_e_2000(tuple(p), (p[0], 0.0, 0.0))
            for p in near[:: max(1, len(near) // 512)]]
    cast_mean = float(np.mean(cast)) if cast else 0.0

    flat = rendered.reshape(-1, 3)
    clipped_hi = float((flat.max(axis=1) >= 0.999).mean())
    clipped_lo = float((flat.max(axis=1) <= 0.001).mean())
    penalty = 40.0 * max(0.0, clipped_hi - 0.001) + 40.0 * max(0.0, clipped_lo - 0.001)
    worst = float(np.max(cast)) if cast else 0.0
    return cast_mean + penalty, worst + penalty


# ------------------------------------------------------------------ tuning
def apply_params(base_settings, p):
    """Map the search vector back onto renderer settings."""
    s = dict(base_settings)
    for k in ("IncrementalTemperature", "IncrementalTint", "Exposure2012",
              "Blacks2012", "Whites2012"):
        s[k] = p[k]
    pts = base_settings.get("ToneCurvePV2012")
    if pts and "CurveStrength" in p:
        k = p["CurveStrength"]
        s["ToneCurvePV2012"] = [(x, x + (y - x) * k) for x, y in pts]
    return s


def evaluate(lin, base, p, objective):
    return objective(crs.render(lin, apply_params(base, p)))


def tune(lin, base, objective):
    """Bounded coordinate descent. Deterministic, and it never leaves bounds."""
    p = {k: float(base.get(k, 0.0)) for k in PARAMS if k != "CurveStrength"}
    if base.get("ToneCurvePV2012"):
        p["CurveStrength"] = 1.0
    for k, (lo, hi, _) in PARAMS.items():
        if k in p:
            p[k] = min(hi, max(lo, p[k]))

    best_mean, best_worst = evaluate(lin, base, p, objective)
    best_p, history = dict(p), [best_mean]
    stalls = 0

    for it in range(MAX_ITERS):
        improved = False
        for k in list(p):
            lo, hi, step = PARAMS[k]
            for delta in (step, -step):
                cand = dict(best_p)
                cand[k] = min(hi, max(lo, cand[k] + delta))
                if cand[k] == best_p[k]:
                    continue
                m, w = evaluate(lin, base, cand, objective)
                if m < best_mean - 1e-9:
                    best_mean, best_worst, best_p = m, w, cand
                    improved = True
        history.append(best_mean)
        stalls = stalls + 1 if (not improved or
                                history[-2] - history[-1] < PLATEAU_EPS) else 0
        if stalls >= PLATEAU_ROUNDS:
            return best_p, best_mean, best_worst, it + 1, "plateaued"
        if best_mean <= GATE_MEAN and best_worst <= GATE_WORST:
            return best_p, best_mean, best_worst, it + 1, "reached the gate"
    return best_p, best_mean, best_worst, MAX_ITERS, "hit the iteration cap"


def as_percent(mean_de):
    return 100.0 * max(0.0, 1.0 - mean_de / 10.0)


# per-photo, never portable: these belong in the typed recipe, not the preset.
PER_PHOTO = ("Exposure2012", "Temperature", "Tint")

# tuned by the loop AND safe to ship inside a portable preset.
PORTABLE = ("IncrementalTemperature", "IncrementalTint", "Blacks2012", "Whites2012")


def write_tuned(preset_path, out_path, base, p):
    """Write the tuned portable settings, and strip what must never ship.

    The loop tunes Exposure alongside the rest, but Exposure, Temperature and
    Tint are per-photo: a preset carrying them applies one photo's correction to
    every photo. They belong in the recipe the user types, not in the .xmp.
    """
    import re
    text = Path(preset_path).read_text()
    s = apply_params(base, p)
    for k in PORTABLE:
        val = f"{s[k]:+.0f}"
        if re.search(rf'crs:{k}="[^"]*"', text):
            text = re.sub(rf'crs:{k}="[^"]*"', f'crs:{k}="{val}"', text)
    for k in PER_PHOTO:
        text = re.sub(rf'\s*crs:{k}="[^"]*"', "", text)
    Path(out_path).write_text(text)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source")
    ap.add_argument("preset")
    ap.add_argument("--reference")
    ap.add_argument("--warmer", type=float, default=0.0)
    ap.add_argument("--cooler", type=float, default=0.0)
    ap.add_argument("--out")
    a = ap.parse_args()

    lin, depth = crs.load_image(a.source)
    base, all_attrs = crs.parse_settings(a.preset)

    if a.reference:
        ref_srgb, _ = crs.load_image(a.reference)
        ref_zones = rotate_chroma(zone_means(crs.linear_to_srgb(ref_srgb)),
                                  a.warmer - a.cooler)
        objective = lambda img: score_against_reference(img, ref_zones)
        target = f"reference {Path(a.reference).name}"
        if a.warmer or a.cooler:
            target += f" (stated deviation: {a.warmer - a.cooler:+g})"
    else:
        objective = score_against_targets
        target = "correctness targets (neutral balance, endpoints, no clipping)"

    p, mean_de, worst, iters, why = tune(lin, base, objective)

    # Coverage is read off the TUNED recipe, not the seed: a slider the tuner
    # moved off zero is verified, and a seed of zeros would otherwise report
    # nothing verified however much work the loop did.
    tuned_attrs = dict(all_attrs)
    for k, v in p.items():
        if k != "CurveStrength":
            tuned_attrs[k] = f"{v:g}"
    moved, modelled = crs.moved_sliders(tuned_attrs)

    print(f"source: {a.source} ({depth})")
    print(f"target: {target}")
    print(f"result: mean dE00 {mean_de:.2f} · worst zone {worst:.2f} · "
          f"{as_percent(mean_de):.1f}% (100*(1-dE/10))")
    print(f"        {iters} iteration(s), {why}")
    unmodelled = [m for m in moved if m not in modelled]
    print(f"coverage: verified across {len(modelled)} of {len(moved)} moved "
          f"slider(s)" + (f"; unmodelled: {', '.join(unmodelled)}" if unmodelled else ""))
    print("note: measured against this repo's renderer, which approximates "
          "Camera Raw and does not reproduce it. Not a Lightroom match.")

    changed = [(k, base.get(k, 0.0), v) for k, v in p.items()
               if abs(v - float(base.get(k, 1.0 if k == "CurveStrength" else 0.0))) > 1e-9]
    for k, was, now in changed:
        print(f"  tuned {k}: {was:+g} -> {now:+g}")

    if a.out:
        write_tuned(a.preset, a.out, base, p)
        print(f"wrote {a.out}")

    passed = mean_de <= GATE_MEAN and worst <= GATE_WORST
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
