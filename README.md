# Lightroom Editor Skill

An [Agent Skill](https://agentskills.io) that turns Claude into a competent Adobe Lightroom **mobile** editing partner — one that knows your camera's quirks before you mention them.

Built for **Claude Desktop**. Works in Claude Code too.

---

## What it does

You describe a photo — or upload one — and it gives you exact slider values, in the order Lightroom actually wants them, calibrated to the file you shot.

- **Corrects the source first.** Sony's green cast, Canon's magenta shift, Apple ProRAW's baked-in tone mapping, Fuji's X-Trans demosaic artefacts. It names the bias, then neutralises it, before touching anything creative.
- **Replicates a look** from a reference image by decomposing it — black point, highlight rolloff, per-zone cast, per-band saturation — into slider moves you can argue with.
- **Writes real `.xmp` presets** you can import on your phone.
- **Critiques an edit** you already made, and tells you which slider caused what.
- **Teaches**, if you want it to. Every number comes with why.

It gives **numbers, never ranges**, and defaults to print-grade restraint over social-media punch.

## Coverage

| Panel | Controls |
|---|---|
| **Light** | Exposure · Contrast · Highlights · Shadows · Whites · Blacks · Tone Curve (RGB, Red, Green, Blue) |
| **Color** | Temp · Tint · Vibrance · Saturation · Color Mix (HSL, 8 bands) · Color Grading (4 wheels + Blending + Balance) · Profiles |
| **Effects** | Texture · Clarity · Dehaze · Vignette (Midpoint, Roundness, Feather, Highlights) · Grain (Amount, Size, Roughness) |
| **Detail** | Sharpening (Amount, Radius, Detail, Masking) · Luminance Noise · Color Noise |
| **Optics** | Lens Corrections · Chromatic Aberration · Defringe · Geometry |
| **Masking** | Subject · Sky · Background · Objects · People sub-masks · Brush · Gradients · Color/Luminance/Depth Range |

Adobe Color profile throughout.

## Sources it knows

Deep profiles for **Apple ProRAW**, **Sony ARW**, **Canon CR2/CR3**, **Nikon NEF**, **Fujifilm RAF**, **Google Pixel DNG**, and **smartphone HEIC/JPEG** — plus a diagnosis method that handles anything not on the list, including cameras that don't exist yet.

## What it measures

Colour is measured, not estimated. `scripts/look-analyze.py` reads a reference
image — or your own file with `--source` — and reports the band shares, the hue
range, the per-zone cast, the black point, and on portraits the skin tone as a
published ITA angle. `scripts/look-match.py` holds a preset against the same
measurements. Both go through one module, so the report and the gate can never
disagree about what colour something is.

Everything perceptual is CIE L\*a\*b\*. Anything compared against a `crs:` hue
value stays in RGB-wheel degrees, because that is the wheel those attributes
use. Every measurement is colour science, in numpy, and every threshold is
either derived from a stated definition or labelled in the source as a
judgement call.

**One optional model, for one question colour cannot answer.** Nothing in
numpy can tell a face from a sand dune, and terracotta, sand and bare wood all
sit exactly where skin sits. So `scripts/segment.py` can run MediaPipe's
16 MB Selfie Multiclass segmenter to decide *which pixels are a face* — and
then the skin tone is measured off those pixels by the same L\*a\*b\* code as
everything else. The model locates; it never grades. It is not installed by
default, not required, and not bundled: without it the skin reading withholds
exactly as it did before.

**It refuses rather than guesses.** A frame with no near-neutral content has no
readable cast, so it prints `WITHHELD` and the reason and falls back to the
camera profile, labelled unmeasured. A forest is not a green cast. A face
against a wooden wall is two warm populations, not one skin tone. A withheld
figure is counted in the verdict line so it can never be read as a measured
one.

## Install

### As a plugin (recommended — Claude Code and Claude Desktop)

```
/plugin marketplace add bogart2020/lightroom-editor-skill
/plugin install lightroom-editor@lightroom-editor-skill
```

The skill then loads automatically whenever you talk about editing a photo.

### As a standalone skill (Claude Desktop upload)

1. Download `lightroom-editor.zip` from the [latest release](https://github.com/bogart2020/lightroom-editor-skill/releases).
2. Claude Desktop → **Settings → Capabilities → Skills → Upload skill**.
3. Select the zip.

### Manually (Claude Code)

```bash
git clone https://github.com/bogart2020/lightroom-editor-skill.git
cp -r lightroom-editor-skill/skills/lightroom-editor ~/.claude/skills/
```

## Using it

Just describe what you're working on. The skill fires on its own.

> "I shot this on my a7 IV, backlit portrait, skin looks green and the whole thing's flat."

> "Make my photo look like this one." *(attach a reference)*

> "Build me a preset for a set of 40 iPhone ProRAW shots from a trip."

> "Here's my edit — what's wrong with it?"

**One limitation worth knowing:** Claude can't see RAW files. `.ARW`, `.CR3`, `.NEF`, `.DNG` won't render. Upload a JPEG export or a screenshot and it reads the actual image; describe it in words and it still works from source knowledge.

## Structure

```
.claude-plugin/
├─ marketplace.json        makes this repo installable via /plugin marketplace add
└─ plugin.json             plugin manifest
skills/lightroom-editor/
├─ SKILL.md                orchestrator — intake, pipeline order, routing
└─ references/
   ├─ 00-pipeline.md       working order, histogram, what to fix first
   ├─ 01-light.md          tone sliders, tone curve, RGB channel curves
   ├─ 02-color.md          white balance, HSL, color grading, profiles
   ├─ 03-effects.md        texture, clarity, dehaze, vignette, grain
   ├─ 04-detail.md         sharpening, luminance noise, color noise
   ├─ 05-optics.md         lens corrections, CA, defringe, geometry
   ├─ 06-masking.md        mask types, combination, standard recipes
   ├─ 07-sources.md        per-camera profiles + universal diagnosis method
   ├─ 08-looks.md          reverse-engineering, film looks, modern looks, genres
   ├─ 09-presets-xmp.md    XMP template, attribute map, mobile import
   ├─ 10-diagnostics.md    failure signatures, critique method, check-yourself lists
   └─ 11-intake.md         look-word decompositions, Intent-vs-source conflicts
  scripts/
   ├─ preset-check.py      validates a generated .xmp before it reaches Lightroom
   ├─ lookstats.py         the measurement core — one implementation of colour
   ├─ look-analyze.py      measures a reference or your own file, and reports
   ├─ look-match.py        does the preset grade the colour the reference has?
   ├─ crs-render.py        renders the modellable sliders onto a photo
   ├─ crs-vocabulary.txt   the crs: attribute names Lightroom actually accepts
   └─ tune.py              scores a render in dE2000 and tunes toward the target
scripts/leak-check.sh      CI-able check that no private material is tracked
```

The scripts live *inside* the skill because SKILL.md requires them at handover; a
skill that references a script it does not ship declares a gate no install can
satisfy.

The SKILL.md is an orchestrator: it routes to a reference file only when that file's branch fires, so a simple question doesn't load all twelve.

## Notes

Slider ranges, defaults, and per-camera claims were fact-checked line by line by four independent review agents against Adobe's documentation. That pass corrected several errors, including an inverted Color Grading **Balance** direction, an invented internal processing order, and a backwards claim about Apple ProRAW highlight headroom. XMP attribute names were verified against real preset files — including the trap that Color Grading stores Shadows and Highlights under legacy `SplitToning*` names while Midtones and Global use `ColorGrade*`.

Numbers that are this skill's own conservative defaults rather than Adobe figures are marked as **house limits**, so you can tell which is which.

Film and simulation recipes are original approximations, not derived from any commercial preset pack. Stock names are used descriptively; all marks belong to their owners.

Not affiliated with or endorsed by Adobe. Lightroom is a trademark of Adobe Inc.

## License

MIT — see [LICENSE](LICENSE).
