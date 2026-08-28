# Detail

Sharpening and noise reduction. Both are **100%-zoom decisions** — at fit-to-screen every setting looks identical and you are guessing.

Detail comes last, because Shadows, Dehaze, Clarity and Exposure all change the noise floor these sliders are tuned against.

## Quick reference

| Control | Range | RAW default | JPEG/HEIC default |
|---|---|---|---|
| Sharpening — Amount | 0 … 150 | 40 | 0 |
| Sharpening — Radius | 0.5 … 3.0 | 1.0 | 1.0 |
| Sharpening — Detail | 0 … 100 | 25 | 25 |
| Sharpening — Masking | 0 … 100 | 0 | 0 |
| Noise Reduction | 0 … 100 | 0 | 0 |
| Noise Reduction — Detail | 0 … 100 | 50 | 50 |
| Noise Reduction — Contrast | 0 … 100 | 0 | 0 |
| Color Noise Reduction | 0 … 100 | 25 | 0 |
| Color NR — Detail | 0 … 100 | 50 | 50 |
| Color NR — Smoothness | 0 … 100 | 50 | 50 |

RAW arrives with baseline sharpening (40) and color noise reduction (25) already applied. Those are not zero, and "adding sharpening" means moving away from a value that is already there.

## Sharpening

The four sliders do genuinely different jobs. Moving Amount alone is why over-sharpened images look crunchy.

- **Amount** — strength of the edge contrast.
- **Radius** — how wide an edge is treated. **Small radius for fine detail** (foliage, hair, text). **Larger radius for soft, broad subjects** (portraits, mist).
- **Detail** — how much fine, high-frequency information gets sharpened. **High Detail sharpens noise along with detail.** Lower it on noisy files.
- **Masking** — restricts sharpening to edges only, leaving smooth areas untouched. **The most valuable of the four and the least used.** Masking 0 sharpens sky, skin and out-of-focus background as hard as it sharpens the subject.

Mobile has no Alt/Option key, but it has the same preview: **hold two fingers on the Masking slider while dragging, then tap the screen** to bring up the black-and-white mask. White is sharpened, black is protected. Look at the mask rather than guessing at it.

### Starting points

**Portrait** — protect skin, sharpen eyes and hair:
```
Amount 35   Radius 1.2   Detail 20   Masking 60
```

**Landscape** — fine detail everywhere, protect sky:
```
Amount 50   Radius 0.9   Detail 35   Masking 40
```

**High ISO / noisy** — sharpen edges only, do not touch the noise:
```
Amount 30   Radius 1.0   Detail 15   Masking 70
```

**Already-sharp phone file (ProRAW, Pixel, HEIC)** — the phone sharpened it already:
```
Amount 15   Radius 1.0   Detail 15   Masking 50
```

Amount above 80 is a red flag on any file. If the image needs it, the image is soft and sharpening will not fix soft.

## Noise reduction — luminance

Removes grain-like brightness noise. It removes fine detail at the same time; there is no setting where it does not.

- **Noise Reduction** — strength. **Detail** — how much fine texture is preserved (raise it if the image goes plastic). **Contrast** — preserves local contrast in noisy areas, useful above NR 40.
- **Under-correct deliberately.** Some luminance noise reads as film. A plastic, waxy, smeared image reads as broken. Grain (`03-effects.md`) is a better answer than more noise reduction.

| Situation | Noise Reduction | Detail | Contrast |
|---|---|---|---|
| Base ISO, clean | 0 | 50 | 0 |
| Moderate (ISO 1600–3200) | 15 | 55 | 0 |
| High (ISO 6400+) | 30 | 60 | 20 |
| Extreme (night, ISO 12800+) | 45 | 65 | 30 |

Above 50, expect foliage to go watercolour and skin to go waxy. Prefer NR 35 plus Grain 15.

## Color noise reduction

Removes the colored speckle — red, green and magenta blotches — that appears in shadows and at high ISO. **Far less destructive than luminance NR**, because chroma noise carries almost no real detail.

RAW starts at 25 and that is usually correct. Raise to 40–60 on high-ISO files, and specifically when shadows show magenta or green mottling.

**Smoothness** controls how far color blotches are blended; raise it when large colored patches persist. **Detail** protects color edges; lower it if colors bleed across boundaries.

Color noise reduction is nearly free. When shadows look colour-speckled, raise this before touching luminance NR.

## AI Denoise

Adobe's machine-learning denoiser is a different and far better tool than the sliders — it produces a new DNG rather than adjusting the existing one.

Availability on mobile is narrow: **iPad Pro or iPad Air with an M1 chip or later** and 8 GB+ RAM, RAW/DNG only. The base iPad and iPad mini run A-series chips and are excluded, so "Apple silicon" is too broad a test. Not available on iPhone or Android as of Lightroom mobile 11.5 (August 2026). Do not prescribe it for a phone-only workflow, and recheck availability — Adobe has been expanding it.

## Working order within Detail

1. **Color noise reduction first** — cheap, and it changes what the luminance noise looks like.
2. **Luminance noise reduction second** — set it as low as the image tolerates.
3. **Sharpening last** — because you now know how much noise you are about to amplify.
4. **Grain after all three** (`03-effects.md`) if the result is too smooth.

## Common mistakes

| Mistake | Fix |
|---|---|
| Judging at fit-to-screen | 100% zoom, or you are guessing. |
| Amount 100 for a soft image | Sharpening cannot fix soft focus. Amount past 80 is a red flag. |
| Masking left at 0 | Sky, skin and bokeh all get sharpened. Raise it to 50–70 on portraits. |
| Noise Reduction 70 | Plastic skin, watercolour foliage. NR 35 plus Grain 15. |
| Full sharpening on ProRAW or HEIC | The phone already sharpened. Amount 15. |
| Sharpening before Dehaze/Shadows | Those moves change the noise floor. Detail comes last. |
