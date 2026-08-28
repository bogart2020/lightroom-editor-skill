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

## Install

### Claude Desktop

1. Download this repo, or `git clone https://github.com/bogart2020/lightroom-editor-skill.git`
2. Zip the **`lightroom-editor/`** folder (the folder containing `SKILL.md`).
3. Claude Desktop → **Settings → Capabilities → Skills → Upload skill**.
4. Select the zip.

A prebuilt `lightroom-editor.zip` is attached to the [latest release](https://github.com/bogart2020/lightroom-editor-skill/releases).

### Claude Code

```bash
git clone https://github.com/bogart2020/lightroom-editor-skill.git
cp -r lightroom-editor-skill/lightroom-editor ~/.claude/skills/
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
lightroom-editor/
├─ SKILL.md              orchestrator — intake, pipeline order, routing
└─ references/
   ├─ 00-pipeline.md     order of operations, histogram, what to fix first
   ├─ 01-light.md        tone sliders, tone curve, RGB channel curves
   ├─ 02-color.md        white balance, HSL, color grading, profiles
   ├─ 03-effects.md      texture, clarity, dehaze, vignette, grain
   ├─ 04-detail.md       sharpening, luminance noise, color noise
   ├─ 05-optics.md       lens corrections, CA, defringe, geometry
   ├─ 06-masking.md      mask types, combination, standard recipes
   ├─ 07-sources.md      per-camera profiles + universal diagnosis method
   ├─ 08-looks.md        reverse-engineering, film emulation, modern looks, genres
   ├─ 09-presets-xmp.md  XMP template, attribute map, mobile import
   └─ 10-diagnostics.md  failure signatures, critique method, check-yourself lists
```

The SKILL.md is an orchestrator: it routes to a reference file only when that file's branch fires, so a simple question doesn't load all eleven.

## Notes

Slider ranges and defaults were checked against Adobe documentation, and the XMP attribute names were verified against real Lightroom preset files rather than taken from memory — including the trap that Color Grading stores Shadows and Highlights under legacy `SplitToning*` names while Midtones and Global use `ColorGrade*`.

Not affiliated with or endorsed by Adobe. Lightroom is a trademark of Adobe Inc.

## License

MIT — see [LICENSE](LICENSE).
