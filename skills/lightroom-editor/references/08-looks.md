# Looks

The creative layer. Runs only after the baseline is correct — a look built on an uncorrected file bakes the source's cast into the style.

Four routes: decompose a reference image, emulate film, apply a named modern look, or start from a genre baseline.

---

## Route 1 — Reverse-engineering a reference image

The method for "make my photo look like this one." Read the reference in this order; each answer maps to a specific control.

**On reference images you do not own.** References for this kind of work are usually press photos, album art or someone else's portfolio. Measuring them — hue range, black point, per-band content, zone statistics — is fine whatever their copyright status; you are reading numbers off a picture to calibrate a recipe, and the numbers are not the picture. What the skill never does is reproduce, redistribute, embed or output the reference image itself, or present the resulting look as the original photographer's work. Measure freely; hand back slider values, never the file.

### 0. Pin the reference set, and pin the target

Two questions come before any reading, and getting either wrong invalidates
everything downstream.

**Which images are the reference?** One look, not one artist. A reference set is
frames that share a single grade — the same shoot, the same treatment. An album
cover plus press photos plus search-results thumbnails is not a set; averaging
them yields a range that describes none of them, and the recipe you derive will
match nothing. Prefer **one primary reference**: the image the user actually
pointed at. Add more only when they demonstrably carry the same grade.

`scripts/look-match.py` measures the saturation-weighted 10th–90th percentile of
hue and **refuses a set whose frames' means differ by more than 12°**. If it
refuses, the set is the problem, not the preset.

**How close should the result land?** The reference is not automatically the
target. A user who says "warm, leaning golden" while holding up a cover that
measures 31–40° wants something 5–10° warmer than the thing they showed you.
Get the deviation as a number, and check the preset against
*reference + deviation*, not against the reference:

```
scripts/look-match.py --warmer 8 REFERENCE.jpg PRESET.xmp
```

Write the deviation into the preset's description or the build notes. Nothing in
the `.xmp` records it, so an unrecorded deviation is lost the moment the
conversation ends, and the next revision drifts back toward fidelity.

### 1. Read the black point

Look at the darkest area. Is it true black, or lifted grey-blue?

- **True black** → Blacks 0 to −20.
- **Lifted** → Blacks **+10 to +25**, plus the Blue channel curve's bottom point raised to `0,10`–`0,15`. Lifted blacks are the defining feature of most film and matte looks, and the single most reliable thing to read off a reference.

### 2. Read the white point and rolloff

Look at the brightest area. Does it reach pure white, or stop short?

- **Reaches white** → Whites +15 or higher, clean digital.
- **Stops short, greyish** → composite curve top pulled down to `255,240`–`255,250`. This is the film rolloff.

### 3. Read the cast per tonal zone

The most informative step. Check three places separately:

| Where | What to read | Maps to |
|---|---|---|
| Darkest non-black area | Shadow cast — usually blue, teal, or green | Color Grading Shadows, or Blue curve bottom |
| Mid-grey / skin | Midtone cast — usually warm or neutral | Color Grading Midtones, or Temp |
| Brightest non-white area | Highlight cast — usually warm, amber, or cream | Color Grading Highlights, or Red/Blue curve top |

**Shadows and highlights casting opposite ways is the signature of nearly every graded look.** Cool shadows with warm highlights is the most common pair by a wide margin.

### 4. Read saturation per hue band

**Establish which bands the reference actually contains before you touch any of
them.** This is the step most often skipped, and skipping it is how a preset
ends up spending its strongest moves on colours the reference does not have.
A golden-hour reference is typically 90%+ Orange with a little Yellow and no
Green or Blue at all; draining Green −40 there does nothing to the reference
and strips green out of the *user's* photo instead, which reads as an orange or
red cast. `scripts/look-match.py` measures this from the reference file.

Two rules follow:

- **Do not push a band the reference does not contain.** If Green is under 5%
  of the reference's colour, Green is not part of the look.
- **Do not leave the dominant band untouched.** If Orange is 90% of the
  reference, the look lives in Orange. A preset that never adjusts Orange has
  not replicated anything.

Then, per band, compare against how the colors would look untouched:

- **Skin** (Orange) — richer or drained?
- **Foliage** (Green/Yellow) — vivid, or muted and yellow-shifted?
- **Sky** (Blue/Aqua) — deep, or pale and cyan?

Most "cinematic" looks are **greens drained and hue-shifted, skin preserved, blues deepened.** Most "film" looks are everything slightly drained with one band left alone.

### 5. Read the contrast shape

Squint at the reference. Where is the tonal separation?

- Separation in the midtones, compressed ends → S-curve.
- Flat midtones, separation only at the ends → inverted S; the matte look.
- Even throughout → linear, minimal curve.

### 6. Read texture

At 100%: grain present? Sharp or soft? Halos, meaning heavy Clarity?

### Then build it

Work the readings back through the pipeline in order: endpoints → curve shape → channel curves for zonal cast → Color Mix for per-band saturation → Color Grading → grain. Show the user which reading produced which slider so they can argue with the reading, not just the number.

**Say what cannot be matched.** A reference shot on medium-format film at f/2 has a depth-of-field and highlight rolloff no slider reproduces. Lens character, dynamic range, and subject lighting are not adjustments. Name those honestly instead of pushing sliders further to chase them.

---

## Route 2 — Film and simulation looks

**Approximations, not emulations.** These are hand-built slider stacks that evoke the *impression* of a look. They are not derived from scans, measurements, spectral data, or any commercial preset pack. No slider recipe reproduces an emulsion's grain structure, spectral response, or halation. Treat them as starting points, adjust to the image, and tell the user that is what they are.

Names are used descriptively to identify the look being approximated. All marks belong to their owners; these recipes are unaffiliated with and not endorsed by Kodak, Kodak Alaris, Fujifilm, CineStill or Harman/Ilford.

### Actual film stocks

**Kodak Portra — warm, soft, forgiving skin:**
```
Contrast −8   Highlights −20   Shadows +18   Whites +12   Blacks +12
Curve: 0,10  64,62  128,130  192,196  255,248
Blue curve: 0,10   Red curve: 192,200
Vibrance +12   Saturation −5
Orange Sat −6   Orange Lum +8   Green Hue +15   Green Sat −12
Color Grading: Shadows Hue 30 Sat 6, Highlights Hue 45 Sat 10
Grain: Amount 14  Size 24  Roughness 50
```

**Kodak Gold — nostalgic, warm, yellow-forward:**
```
Contrast −5   Highlights −15   Shadows +15   Blacks +15
Temp +250K from neutral
Curve: 0,12  128,132  255,246
Blue curve: 0,14  255,244
Vibrance +15   Yellow Sat +10   Orange Lum +6
Color Grading: Highlights Hue 50 Sat 14, Shadows Hue 40 Sat 6
Grain: Amount 18  Size 26  Roughness 55
```

Warmth here is carried by Orange saturation and luminance, the Blue curve
and Color Grading — never by dragging `Yellow Hue` negative. Negative
`HueAdjustmentYellow` rotates the image's own yellows into orange, and into
red once a positive `IncrementalTint` lands on top. Sign table and the full
explanation: `references/09-presets-xmp.md`.

**Tungsten cinema look — 3200K-balanced, cool shadows:**
```
Temp −400K from neutral   Tint +4
Contrast +8   Blacks +14
Blue curve: 0,18  255,250
Color Grading: Shadows Hue 195 Sat 18, Highlights Hue 20 Sat 10
Aqua Sat +12   Orange Sat −8
Grain: Amount 22  Size 30  Roughness 60
```

The red halation around point lights is the signature of this stock and **cannot be produced with global sliders** — it is a localized bloom around highlights, not a highlight tint. Say so rather than pushing Color Grading Highlights further.

**Ilford HP5 — black and white, classic:**
```
Profile: Adobe Monochrome
Contrast +18   Whites +20   Blacks −12
Curve: 0,4  64,54  128,128  192,202  255,252
B&W Mix: Red +20  Orange +25  Yellow +15  Blue −25  Aqua −15
Grain: Amount 28  Size 34  Roughness 60
```

### Fujifilm digital simulation modes

These four are **Fujifilm's own in-camera simulations, not film stocks** — Classic Chrome is not based on any film at all. If the user shoots Fujifilm, `07-sources.md` applies: Adobe ships matched camera profiles that reach these looks far more accurately than sliders can.

**Classic Chrome — muted, subtly warm, documentary:**
```
Contrast +5   Highlights −18   Shadows −8   Whites +8   Blacks −14
Curve: 0,4  72,64  128,126  186,190  255,246
Vibrance −5   Saturation −10
Red Sat −6   Orange Sat −4   Yellow Sat −14   Green Sat −22   Green Hue +12
Aqua Hue +8   Blue Sat −12   Blue Lum −8
Color Grading: Highlights Hue 42 Sat 6, Shadows Hue 40 Sat 4, Blending 55
```

**Classic Negative — punchy shadows, shifted greens, distinctive:**
```
Contrast +12   Highlights −25   Shadows −10   Blacks +8
Curve: 0,8  64,56  128,128  192,200  255,250
Blue curve: 0,12  128,124
Green Hue +25   Green Sat −20   Aqua Hue −15   Orange Sat −10
Color Grading: Shadows Hue 200 Sat 10, Highlights Hue 40 Sat 8
```

**Eterna — flat, low-saturation cinema rendering:**
```
Contrast −30   Highlights −30   Shadows +30   Whites −10   Blacks +20
Curve: 0,18  128,128  255,238
Saturation −18   Vibrance +8
Color Grading: Shadows Hue 210 Sat 12, Highlights Hue 45 Sat 8, Blending 60
```

**Acros — black and white, smooth, fine grain:**
```
Profile: Adobe Monochrome
Contrast +8   Highlights −20   Shadows +15   Blacks −8
Curve: 0,6  128,130  255,248
B&W Mix: Red +10  Orange +18  Yellow +10  Green +8  Blue −18
Grain: Amount 12  Size 20  Roughness 45
```

---

## Route 3 — Modern digital looks

**Clean commercial — accurate, bright, no visible grade:**
```
Contrast +12   Highlights −20   Shadows +18   Whites +18   Blacks −10
Curve: 0,0  64,60  192,196  255,255
Vibrance +12   Saturation 0
Orange Sat −5   Orange Lum +6   Blue Lum −10
Texture +10   Clarity +5
```

**Moody editorial — dark, desaturated, cool shadows:**
```
Exposure −0.20   Contrast +15   Highlights −35   Shadows −12   Whites −8   Blacks +8
Curve: 0,10  64,52  128,124  192,192  255,242
Blue curve: 0,16
Vibrance +5   Saturation −12
Green Sat −25   Green Hue +18   Orange Sat −8   Blue Lum −18
Color Grading: Shadows Hue 210 Sat 15, Highlights Hue 40 Sat 8, Blending 55
Vignette: Amount −16  Midpoint 40  Feather 70
```

**Warm golden hour — amplify the light that was there:**
```
Temp +300K from neutral
Contrast +8   Highlights −30   Shadows +20   Whites +12   Blacks +6
Curve: 0,6  192,200  255,250
Red curve: 192,204   Blue curve: 0,8  255,246
Vibrance +15
Orange Sat +5   Orange Lum +8   Yellow Sat +6
Color Grading: Highlights Hue 40 Sat 14, Shadows Hue 30 Sat 6
```

Warmth here is carried by Orange saturation and luminance, the Blue curve
and Color Grading — never by dragging `Yellow Hue` negative. Negative
`HueAdjustmentYellow` rotates the image's own yellows into orange, and into
red once a positive `IncrementalTint` lands on top. Sign table and the full
explanation: `references/09-presets-xmp.md`.

**Muted matte — soft, quiet, editorial:**
```
Contrast −15   Highlights −18   Shadows +22   Whites −10   Blacks +20
Curve: 0,20  128,128  255,236
Vibrance +8   Saturation −15
All bands Sat −12 except Orange −4
Color Grading: Shadows Hue 210 Sat 10 Lum +6, Blending 65
Texture −5   Clarity −8
Grain: Amount 12  Size 22
```

**Airy and bright — light, open, high-key:**
```
Exposure +0.30   Contrast −10   Highlights −25   Shadows +30   Whites +15   Blacks +14
Curve: 0,16  128,136  255,250
Vibrance +10   Saturation −8
Orange Lum +12   Blue Lum +10   Green Sat −15
Color Grading: Highlights Hue 45 Sat 8, Shadows Hue 210 Sat 6
Clarity −8   Texture −5
```

**High-contrast punch — bold, graphic:**
```
Contrast +25   Highlights −30   Shadows +10   Whites +22   Blacks −22
Curve: 0,0  64,48  128,128  192,206  255,255
Vibrance +18   Saturation +5
Blue Lum −22   Blue Sat +12   Orange Lum +5
Clarity +12   Texture +14
```

---

## Route 4 — Genre baselines

Where to start, and what to protect.

| Genre | Protect | Push | Never |
|---|---|---|---|
| **Portrait** | Skin texture and hue | Eyes, separation from background | Clarity above +10 on a face; Saturation above +15 |
| **Landscape** | Sky gradient, foliage hue | Texture, endpoints, Blue Lum down | Dehaze above +15; over-saturated greens |
| **Street** | Grit, real contrast | Blacks down, Texture, grain | Over-smoothing; noise reduction above 30 |
| **Food** | Warmth, appetite colors | Texture, Orange/Yellow Sat | Cool grades; green casts near any food |
| **Product** | Accurate color, clean white | Whites, sharpening, neutrality | Any grade; Vibrance above +8 |
| **Architecture** | Straight lines, neutral greys | Geometry, Clarity, Texture | Warm grades that misread as time of day |
| **Night / astro** | Star color, shadow detail | Color NR, Contrast, Blacks | Luminance NR above 40; Dehaze |

---

## Route 5 — One look, several sources

For a preset *family*: the same look shipped as variants for different bodies —
iPhone ProRAW and Sony ARW, X100VI and a phone, a two-camera wedding set. The
mistake is grading each source separately and hoping they land together. They
will not: two independently-built looks drift, and the drift shows the moment
the photos sit side by side in one feed.

**Split the recipe in two, and treat the halves completely differently.**

| Layer | Per source? | What lives here |
|---|---|---|
| **Correction** | **Different for every source** | Profile, white balance, the cast fix, lens/optics, noise and sharpening, and the curve points that undo the source's own tone mapping. See `references/07-sources.md` — this is exactly the per-body bias it documents. |
| **Creative** | **Byte-identical across variants** | Color Mix bands, Color Grading wheels, curve *shape* above the correction, Texture, Clarity, Dehaze, vignette. This layer is the look. If it differs between variants, they are two looks. |

The method:

1. **Correct each source to the same neutral.** Not "to something reasonable" — to the *same* place. Grey should measure grey on both, and the black point should land at the same value. This is the whole job; if it is right, the creative layer transplants cleanly.
2. **Build the creative layer once**, on whichever file has the most latitude — a true Bayer raw over a ProRAW or a JPEG. Freedom to push comes from headroom, and it is easier to pull a look back than to invent it on a file that has already spent its range.
3. **Transplant that layer unchanged** onto the other corrected sources, and change nothing in it to "make it look right". If a variant looks wrong, the bug is in step 1's correction, not in the look.
4. **Grain Size is the one exception**, because it is resolution-relative and the bodies differ in megapixels. Scale it per variant with the rule in `references/03-effects.md`; every other creative number stays put.
5. **Verify the variants against each other**, not only against the reference. Run each through the Step 5 score, and expect the *same* look to land at similar zone statistics. A gap between variants means a correction gap.

Headroom caps how far the family can go: the look must be reachable on the **weakest** source in the set, or that variant will be the one that bands. Build to that ceiling, and the stronger files will hold it comfortably.

---

## Restraint

A look is a layer, not a rescue. When a look needs extreme numbers to show up, the baseline underneath it is wrong — usually flat endpoints or an uncorrected cast. Go back to `01-light.md` and `02-color.md` rather than pushing the grade harder.

Ceilings for a look that still reads as photography: Color Grading Saturation **25**, Clarity **+15**, Dehaze **+15**, Saturation **+20**, channel curve moves **±30**.
