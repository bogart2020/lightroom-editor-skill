# Effects

Texture, Clarity, Dehaze, Vignette, Grain. All available on RAW, JPEG and HEIC.

## Quick reference

| Control | Range | Default |
|---|---|---|
| Texture | −100 … +100 | 0 |
| Clarity | −100 … +100 | 0 |
| Dehaze | −100 … +100 | 0 |
| Vignette — Amount | −100 … +100 | 0 |
| Vignette — Midpoint | 0 … 100 | 50 |
| Vignette — Roundness | −100 … +100 | 0 |
| Vignette — Feather | 0 … 100 | 50 |
| Vignette — Highlights | 0 … 100 | 0 |
| Grain — Amount | 0 … 100 | 0 |
| Grain — Size | 0 … 100 | 25 |
| Grain — Roughness | 0 … 100 | 50 |

## Texture vs Clarity vs Dehaze

Three sliders that all look like "more detail" and target completely different frequencies. Choosing the wrong one is the most common Effects mistake.

| | Frequency | Affects color? | Best for |
|---|---|---|---|
| **Texture** | Fine — pores, hair, fabric weave, bark | No | Detail without contrast change |
| **Clarity** | Mid — the whole midtone contrast band | Slightly | Punch, presence, depth |
| **Dehaze** | Broad — atmospheric contrast | Strongly | Haze, fog, flat distance |

### Texture

Fine detail only, no midtone contrast shift, no color shift. The safest of the three by a wide margin.

- **Positive: +8 to +20.** Landscapes, fabric, architecture, hair.
- **Negative: −15 to −30** smooths skin while keeping edges sharp — better than any blur, because eyes and lips stay crisp. The correct global skin-softening tool.
- Texture does not create halos. It is the right answer whenever you are unsure between the three.

### Clarity

Midtone local contrast. Adds presence, and adds it everywhere.

- **+5 to +15 is the working range.** Above +20 it starts producing halos at high-contrast edges — a horizon, a backlit head against sky — and grey, dirty skin.
- **Never above +10 on a face.** Clarity finds every pore and shadow and deepens all of them.
- **Negative Clarity (−10 to −25)** is the dreamy, glowing, soft-focus look. Excellent on backlit portraits.
- Clarity slightly desaturates. If an image goes flat after Clarity, that is why.

### Dehaze

Built for atmospheric haze. It applies broad contrast *and* saturation, and it amplifies noise more than anything else in the panel.

- **+5 to +15** recovers a hazy distance or a flat sky.
- **Above +20 the sky goes cyan-black, shadows crush, and noise appears.** Check the shadows and the noise floor after every Dehaze move.
- **Negative Dehaze (−10 to −30)** adds atmosphere and glow. It is the fastest way to a soft, hazy, misty look, and it pairs naturally with lifted blacks.
- Dehaze runs before Detail in the pipeline, so tune sharpening and noise *after* it.

**Stacking:** Texture +12 with Clarity +8 gives more apparent detail than Clarity +20, with none of the halos.

## Vignette

Post-crop: it follows the crop, not the original frame. Applied after Optics, so it is independent of lens-profile vignette correction.

| Sub-slider | Effect |
|---|---|
| **Amount** | Negative darkens corners, positive brightens. |
| **Midpoint** | How far in the effect reaches. **Low = reaches toward the centre**, high = corners only. |
| **Roundness** | Negative = rectangular, follows the frame. Positive = circular. |
| **Feather** | Edge softness. Low = a hard visible ring. High = an invisible gradient. |
| **Highlights** | Protects bright areas from being darkened. **Only does anything when Amount is negative.** |

**The invisible vignette** — the one that shapes attention without announcing itself:

```
Amount −12   Midpoint 40   Roundness 0   Feather 70   Highlights 0
```

**Portrait vignette** — tighter, holds the face:

```
Amount −18   Midpoint 30   Roundness +15   Feather 60   Highlights 0
```

**When the scene has bright corners** — a window, sky, a lamp — raise **Highlights to 30–50** so the vignette darkens the surroundings without turning the bright area grey.

Amount past −35 is visible as a ring and reads as an effect rather than as light.

## Grain

Adds monochromatic grain. Genuinely useful beyond nostalgia: grain masks banding in gradients (skies, studio backdrops) and hides the plastic smoothness left by heavy noise reduction.

| Sub-slider | Effect |
|---|---|
| **Amount** | Strength. |
| **Size** | Grain particle size. Above 25 Adobe adds slight blue to the grain so noise reduction interacts with it more gracefully. |
| **Roughness** | Irregularity. Low = uniform and digital. High = irregular and organic. |

**Subtle film texture:**

```
Amount 12   Size 22   Roughness 50
```

**Visible 35mm film:**

```
Amount 25   Size 32   Roughness 60
```

**Heavy, pushed film:**

```
Amount 40   Size 45   Roughness 70
```

**Size is resolution-relative.** Grain at Size 25 on a 12 MP phone file is visually coarser than the same setting on a 60 MP file. On high-resolution files raise Size to keep the same apparent texture.

**Grain last, and check it at 100%.** At fit-to-screen, grain is invisible at any setting — you cannot judge it zoomed out.

## Common mistakes

| Mistake | Fix |
|---|---|
| Clarity +30 for punch | Texture +15 with Clarity +8. No halos. |
| Clarity on a face | Never above +10. Prefer Texture, or negative Texture to soften. |
| Dehaze +30 to fix a flat sky | Above +20 the sky goes cyan and the noise arrives. Use +12 and a Blue Lum move. |
| Vignette Amount −40 | Reads as an effect. −12 to −18 with Feather 70. |
| Vignette Highlights raised with a positive Amount | It does nothing there. Highlights only works on negative Amount. |
| Judging grain at fit-to-screen | Grain is a 100% decision. |
