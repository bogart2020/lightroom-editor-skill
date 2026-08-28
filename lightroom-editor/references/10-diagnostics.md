# Diagnostics

For critiquing an edit, and for the check-yourself list that ends every recipe.

Every number below is a starting point to judge against the actual image, not a constant. Give the user the number — vague direction is worse than a number they can adjust — but expect to move it once you see the result.

## Failure signatures

Each entry: what the user sees, what actually caused it, what fixes it. Work from the symptom.

### Flat, grey, lifeless — "the HDR look"

**Cause:** Shadows lifted and Highlights recovered at the same time, so nothing is dark and nothing is bright. On computational RAW, the phone did half of it before the user started.

**Fix:** Shadows back to +15 to +25. Highlights back to −25. Set the endpoints — Whites +15, Blacks −10 — then add contrast in the curve. If one region genuinely needs the recovery, mask it.

### Orange or sunburnt skin

**Cause:** Temp pushed warm to fix a green cast that lives on Tint, plus Vibrance or Saturation on top. Or the skin was warmed toward a remembered "correct" tone rather than corrected against a neutral.

**Fix:** Reset Temp. Correct the cast on **Tint**. Then `Orange Hue +5`, `Orange Sat −8`. Check against a neutral object in the frame, not against an idea of what skin should look like.

### Grey, ashy, lifeless skin

**Cause:** Orange saturation pulled too far down, or Clarity applied to a face, or a green cast never corrected. On deep skin, over-desaturation reads as ashy much faster than on light skin.

**Fix:** Orange Sat back to −5 or 0. Clarity off the face — use Texture instead. Check Tint for a residual green cast.

### Halos on high-contrast edges

**Cause:** Clarity above +20, Dehaze above +20, or heavy sharpening at high Radius. On Apple ProRAW, often baked in by the phone before the user touched it.

**Fix:** Clarity to +8, Texture to +15 to replace the lost apparent detail. Reduce Sharpening Radius toward 1.0. If they are baked in, say so — they cannot be removed.

### Crunchy, gritty, over-sharpened

**Cause:** Sharpening Amount too high, Detail too high, Masking at 0. On phone files, sharpening added on top of the phone's own.

**Fix:** Amount 35, Detail 20, Masking 60. On phone files, Amount 15.

### Plastic, waxy, watercolour texture

**Cause:** Luminance noise reduction too high, or an X-Trans file over-sharpened, or the phone's own noise reduction showing through.

**Fix:** Noise Reduction to 30, Detail to 60, and add Grain 15 to restore texture. On Fuji, lower Sharpening Detail to 20.

### Cyan, unnatural sky

**Cause:** Dehaze above +20, or Blue saturation pushed, or Aqua left unaddressed.

**Fix:** Dehaze to +10. Deepen the sky with `Blue Lum −15` rather than saturation. `Aqua Hue +10` moves cyan toward true blue.

### Muddy, dirty greens

**Cause:** Global saturation raised, which pushes the yellow-green digital cameras already over-produce.

**Fix:** `Green Hue +15` to move grass toward believable green, `Green Sat −12`. Vibrance instead of Saturation globally.

### Banding in skies or gradients

**Cause:** Usually an 8-bit JPEG pushed hard, most often by a tone slider or heavy Dehaze — quantisation made visible by a steep tone move. Higher bit depths band far less, but will still band under extreme moves.

**Fix:** Reduce the move that caused it. Add **Grain 12–15**, which hides banding effectively. If the file is JPEG, say that the ceiling is the file, not the edit.

### Colour speckle in the shadows

**Cause:** High ISO with color noise reduction left at default.

**Fix:** Color Noise Reduction to 40–60. Cheap, and it costs almost no detail. Raise Smoothness if large blotches persist.

### The edit looks good on the phone, wrong on a big screen

**Cause:** Judged at fit-to-screen. Clarity, sharpening, noise and grain are all invisible at that size.

**Fix:** Re-check at 100%: sharpening, noise, grain, and every mask edge.

### A visible ring around the frame

**Cause:** Vignette Amount too strong, or Feather too low.

**Fix:** Amount −15, Feather 70, Midpoint 40.

### Halo or bright line around the subject

**Cause:** A sky or background mask that includes the subject's edge.

**Fix:** Subtract Select Subject from the mask, and check the boundary at 100%.

### Nothing is wrong, but it looks like a filter

**Cause:** Color Grading saturation above 25, or a grade applied to an image with no contrast for it to sit on.

**Fix:** Halve the grade. Fix the tone curve first — a grade reads as light when it sits on real contrast, and as a filter when it does not.

---

## Critiquing an edit

When the user shows a finished edit, work this order and report the first two or three findings only. A list of twelve problems is not usable.

1. **White balance** — find a neutral. Is it neutral?
2. **Endpoints** — is there true black and true white? Should there be?
3. **Skin** — correct hue, correct luminance, texture intact?
4. **Regional damage** — did a global move wreck one area?
5. **At 100%** — halos, crunch, plastic texture, mask edges.
6. **Overall** — does it read as a photograph or as a preset?

Lead with what is working. Then the findings, most damaging first, each with the specific slider that fixes it.

---

## Building the check-yourself list

Every recipe ends with checks **specific to what that recipe risks**. A generic list is ignored. Derive it from the moves you actually prescribed:

| If the recipe includes | Then check |
|---|---|
| Shadows above +25 | Shadow noise, and whether the image went flat |
| Dehaze above +10 | Sky for cyan, shadows for crushing and noise |
| Clarity above +10 | High-contrast edges for halos; the face |
| Sharpening changes | 100% zoom on the subject, and on the sky for amplified noise |
| Noise reduction above 30 | Foliage and skin for watercolour |
| Any mask | The mask boundary at 100% |
| Grain | 100% zoom — invisible at any other size |
| Color Grading | Whether skin still reads as skin |
| Orange band moves | Skin against a neutral object in the frame |
| Work on an 8-bit JPEG | Skies and gradients for banding |
