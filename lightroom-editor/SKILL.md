---
name: lightroom-editor
description: Use when editing a photo in Adobe Lightroom mobile — building an edit from RAW or JPEG, replicating a look from a reference image, creating or exporting a preset, critiquing an edit that looks wrong, or working around a camera system's known bias (Sony green cast, Canon magenta, Apple ProRAW baked-in tone mapping).
license: MIT
---

# Lightroom Mobile Editor

Photo editing in Adobe Lightroom mobile, driven by two ideas in fixed order:

**Baseline before look.** Every file arrives with its *source* character already baked in — a cast, a tone-mapping decision, a sharpening pass someone else chose. Neutralise that first and you are grading a clean image. Skip it and every creative move fights an error you never named.

**Restraint.** Numbers here are deliberately conservative house limits, not Adobe figures — they are chosen so an edit survives scrutiny at full size. When a stronger move is available, name it and let the user ask for it.

## Scope

Adobe Lightroom mobile (iOS/Android), **Adobe Color** profile as the default starting point. Everything is expressed as slider values the user types by hand, and optionally as an `.xmp` preset.

You cannot see a RAW file. `.ARW`, `.CR3`, `.NEF`, `.RAF`, `.DNG` do not render in this conversation. If the user attaches one, say so plainly and ask for a JPEG export or a screenshot of the photo — then continue; a described photo is still workable.

## Step 1 — Intake

Interview before prescribing. Ask these, and do not guess an answer you could have asked for:

| Ask | Why it changes the recipe |
|---|---|
| **Source** — camera or phone, and file type | Sets the whole baseline. See `references/07-sources.md` |
| **What you have** — photo, reference image, Edit-panel screenshot, or words only | Decides how much you can diagnose vs. must infer |
| **Intent** — the look you want, or "clean and accurate" | Decides whether Step 4 runs at all |
| **Subject** — portrait, landscape, street, food, product, night | Sets what is protected and what is expendable |
| **Destination** — print, web, phone screen, client delivery | Sets sharpening, noise, and how far color can go |
| **Reuse** — one photo, or a whole set | Decides whether to produce an `.xmp` |

Ask them one at a time when the user is conversational; ask them as one block when they clearly want speed. Missing answers are fine if the user declines — state the assumption you are making in its place.

## Step 2 — Verdict

Before any slider, deliver a short verdict the user can disagree with:

- **Source character** — what this file's origin does to it, from `references/07-sources.md`.
- **Headroom** — how much recovery latitude exists. A true Bayer raw has a lot. Apple ProRAW and Pixel DNG have far less, because the tone mapping already spent it. An 8-bit JPEG has almost none and bands when pushed.
- **What is actually wrong** — read from the image if you have it, from the description if not.

## Step 3 — Baseline

Build the corrective edit in **pipeline order**. The order is not cosmetic: each stage changes what the next one sees. `references/00-pipeline.md` explains why, and is the file to read when unsure what to fix first.

1. **Profile** → Adobe Color, unless `references/07-sources.md` names a better one for this source.
2. **Optics** → `references/05-optics.md`. Lens profile and CA first, because they change edge color and geometry everything else is judged against.
3. **White balance** → `references/02-color.md`. Neutralise the source cast here, not later with HSL.
4. **Light** → `references/01-light.md`. Exposure, then the black and white points, then the recovery sliders.
5. **Tone curve** → `references/01-light.md`. Contrast shape and per-channel color balance.
6. **Color** → `references/02-color.md`. Color Mix and Color Grading.
7. **Effects** → `references/03-effects.md`. Texture, Clarity, Dehaze, Vignette, Grain.
8. **Detail** → `references/04-detail.md`. Sharpening and noise, judged at 100%.
9. **Masks** → `references/06-masking.md`. Everything a global slider would damage.

Reach for a mask the moment a global move helps one region and hurts another — a recovered sky that greys the subject, a lifted subject that fogs the background. `references/06-masking.md` carries the standard recipes.

## Step 4 — Look

Runs only when the user wants one. `references/08-looks.md` covers all four routes: decomposing a reference image into slider moves, film emulation, modern digital looks, and genre baselines.

## Step 5 — Deliver

Every answer ends with these four parts, in this order:

1. **Verdict** — source, headroom, diagnosis. Two or three sentences.
2. **Recipe** — panel by panel in pipeline order. Every line is `Slider → value`, with a short why. Give exact numbers, never "increase slightly". Omit any slider you are not moving.
3. **Check yourself** — the specific things to look at on this image before calling it done, from `references/10-diagnostics.md`. Tailored to what this recipe risks, not a generic list.
4. **Preset** — offer it when the user has a set to edit. `references/09-presets-xmp.md` has the XMP template, the attribute map, and the mobile import path.

Done means all four parts are present and every number in the recipe is a number.

## Routing

Read the file when its branch fires. Do not read all of them.

| Branch | File |
|---|---|
| What to fix first, why order matters, reading the histogram | `references/00-pipeline.md` |
| Exposure, contrast, highlights, shadows, whites, blacks, tone curve, RGB channel curves | `references/01-light.md` |
| White balance, vibrance, saturation, Color Mix (HSL), Color Grading, profiles | `references/02-color.md` |
| Texture, clarity, dehaze, vignette, grain | `references/03-effects.md` |
| Sharpening, luminance noise, color noise | `references/04-detail.md` |
| Lens corrections, chromatic aberration, defringe, geometry | `references/05-optics.md` |
| Any edit that should apply to part of the frame only | `references/06-masking.md` |
| Identifying the source and its bias; unknown or unlisted cameras | `references/07-sources.md` |
| Replicating a reference image, film emulation, named looks, genre starting points | `references/08-looks.md` |
| Writing an `.xmp`, attribute names, importing a preset on mobile | `references/09-presets-xmp.md` |
| Critiquing an existing edit; something looks wrong and the user cannot name it | `references/10-diagnostics.md` |

## Red flags

Each of these means stop and correct course:

- About to give a range instead of a number → pick the number.
- About to prescribe without knowing the source → ask; the source decides the baseline.
- Fixing a color cast with Color Mix or Color Grading → white balance owns casts. Correct it upstream.
- Pushing Shadows past +30 on Apple ProRAW or Pixel DNG → the phone already lifted them, and re-lifting is the usual cause of the flat HDR look. +30 is this skill's house limit; the real ceiling is wherever shadow noise appears at 100%.
- Recommending Clarity above +15 or Dehaze above +10 → these are house limits, not hard rules. If the image truly needs more, say why.
- Judging sharpening or noise at fit-to-screen → both are 100%-zoom decisions.
- Offering a preset that carries Exposure, Temp, or Tint → those are per-photo. A portable preset omits them.
