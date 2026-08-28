# Masking

Masking is where a competent edit becomes a good one. **Reach for a mask the moment a global slider helps one region and hurts another** — a recovered sky that greys the subject, a lifted subject that fogs the background.

Masking requires a paid Lightroom subscription. Confirm the user has it before building a recipe that depends on it.

Subscription is not the only variable: the AI masks (Select Subject, Sky, Background, Objects, People) are additionally gated by device capability on Android, and are reported missing on lower-RAM devices. If a subscribed user cannot find Select Subject, ask what device they are on before assuming a billing problem.

## Mask types

| Type | What it selects | Use for |
|---|---|---|
| **Select Subject** | Main subject, automatically | Separating subject from background |
| **Select Sky** | Sky, automatically | The single most useful mask in landscape |
| **Select Background** | Everything but the subject | Darkening or desaturating surroundings |
| **Select Objects** | An object you brush or box roughly | Anything the automatic masks miss |
| **Select People** | Detected people, with sub-masks | Portrait retouching |
| **Brush** | Freehand, with size/feather/flow | Everything else |
| **Linear Gradient** | A directional ramp | Skies, foregrounds, one-directional light |
| **Radial Gradient** | An ellipse, invertible | Drawing attention to a face or subject |
| **Color Range** | Pixels near a sampled color | One color anywhere in the frame |
| **Luminance Range** | Pixels within a brightness band | Highlights or shadows only |
| **Depth Range** | Distance, on files carrying a depth map | Depth comes from the *capture mode* (iPhone Portrait mode, dual-camera HEIC), not from the RAW format — a ProRAW file is not inherently depth-carrying |

**Select People sub-masks:** Entire Person, Facial Skin (labelled Face Skin in some builds), Body Skin, Eyebrows, Eye Sclera, Iris and Pupil, Lips, Teeth, Hair, Clothes. Facial Skin is the important one — it excludes eyes, lips and hair automatically, which no brush does reliably.

## Combining masks

Every mask can be refined by another. This is the real power, and most people never use it.

- **Add** — union. Sky plus a gradient.
- **Subtract** — removes a region. **The most important operator.**
- **Intersect** — only where both apply. The most precise.

**Subtract Subject from Sky.** Automatic sky selection routinely catches sky through hair, between branches, and around a rim-lit head. Subtracting Subject fixes it in one step and removes the halo that otherwise appears around the subject.

**Intersect Luminance Range with Select Subject** — adjust only the highlights on the subject, leaving their shadows alone. This is how you recover a blown forehead without flattening a face.

**Intersect Color Range with Select Sky** — grade only the blue part of a sky, leaving the sunset gradient untouched.

## Standard recipes

Values assume the global baseline is already correct.

**Sky recovery** — the everyday landscape mask:
```
Select Sky, subtract Select Subject
  Exposure −0.35   Highlights −30   Clarity +8
  Saturation +10   Temp −4 (cooler)
```

**Subject lift** — separating a person from the background:
```
Select Subject
  Exposure +0.25   Shadows +12   Texture +8
```

**Facial skin** — even out and clean, without plastic:
```
Select People → Facial Skin
  Texture −18   Clarity −6   Saturation −5   Exposure +0.10
```
Negative Texture smooths skin while eyes and lips stay crisp. Do not use negative Clarity below −15 here; the face loses structure and reads as blurred.

**Eyes** — the highest impact-per-effort move in portraiture:
```
Select People → Iris and Pupil
  Exposure +0.30   Clarity +15   Saturation +10
```
Stop there. Whitening sclera past a few points looks synthetic immediately.

**Backlit rim-lit subject** — the classic golden-hour problem:
```
Select Subject
  Exposure +0.40   Shadows +20   Temp +6 (warmer)
Select Sky, subtract Select Subject
  Highlights −40   Exposure −0.30
```

**Burnt corner or window** — a bright area drawing the eye:
```
Radial Gradient over the bright area, inverted off
  Exposure −0.50   Highlights −25   Feather 70
```

**Graduated sky without a sky mask** — when the sky selection fails on a complex horizon:
```
Linear Gradient from top
  Exposure −0.40   Highlights −25   Temp −5
```

**Deep skin tones** — protect luminance, do not chase an average:
```
Select People → Facial Skin
  Texture −12   Exposure +0.08   Saturation −3
```
Deep skin loses dimension fast under lifting. Small Exposure moves, and let Red and Orange keep their saturation — desaturating deep skin reads as ashy.

## Restraint on masks

- **Feather everything.** A hard-edged mask on anything organic is visible instantly.
- **Small numbers.** A mask concentrates its effect on a small area, so a mask move at +0.4 EV reads as strongly as a global move at +1.0.
- **Three or four masks is a lot.** Past that, the edit fights itself and each mask's edge compounds.
- **Check the boundary at 100%.** Halos live at mask edges, especially around hair and against bright sky.

## Common mistakes

| Mistake | Fix |
|---|---|
| Global Highlights −70 to save a sky | Mask the sky. Global recovery flattens the whole image. |
| Sky mask with a halo around the subject | Subtract Select Subject from it. |
| Brushing skin freehand | Select People → Facial Skin. It excludes eyes and lips automatically. |
| Sclera whitened to pure white | Iris and Pupil only. Whitened sclera reads as fake at a glance. |
| Six overlapping masks | Fix the global baseline first; most of them will become unnecessary. |
| Hard-edged mask on a face | Feather it. |
