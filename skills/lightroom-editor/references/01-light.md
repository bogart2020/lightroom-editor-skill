# Light

All six tone sliders and the tone curve. Ranges verified against Adobe documentation, August 2026. Temp and Tint differ between raw and non-raw files — see `02-color.md`.

## Quick reference

| Control | Range | Default | Owns |
|---|---|---|---|
| Exposure | −5.00 … +5.00 EV | 0 | Overall brightness, whole range |
| Contrast | −100 … +100 | 0 | Midtone separation; the pivot is Adobe's, not yours |
| Highlights | −100 … +100 | 0 | Bright zone recovery, below the white point |
| Shadows | −100 … +100 | 0 | Dark zone recovery, above the black point |
| Whites | −100 … +100 | 0 | The white endpoint |
| Blacks | −100 … +100 | 0 | The black endpoint |

**Auto** runs Adobe Sensei and writes Exposure, Contrast, Highlights, Shadows, Whites, Blacks, and often Vibrance/Saturation. Legitimate as a starting point on a difficult file, but it optimises for a safe histogram rather than a look, and it habitually over-lifts shadows. Treat its output as a first draft to correct.

## Exposure

Overall brightness in stops. Move this before anything else tonal.

- Judge exposure on **the subject**, not the histogram. A correctly exposed backlit portrait has a bright, clipped background — that is the scene, not an error.
- RAW usually holds highlight detail above what the preview shows — commonly one to two stops, varying by body, ISO, and how cleanly the channels clipped. On JPEG/HEIC there is none: clipped is gone.
- Typical corrective range: **−0.50 to +0.80**. Past ±1.5 stops, ask whether the file is salvageable rather than pushing further.

## Whites and Blacks — the endpoints

Set these before Highlights and Shadows. They define where the image begins and ends; recovery works inside them.

**White point:** raise Whites until the brightest area that should hold detail is just short of clipping. **Black point:** lower Blacks until the darkest area that should read as black is just short of clipping.

An image with no true black and no true white looks flat — and the fix is here, not in Contrast and not in Clarity. This is the most common cause of "flat straight out of camera."

- Typical: **Whites +10 to +25**, **Blacks −5 to −20**.
- **Lifted blacks** (Blacks **+10 to +25**) are the matte/film look. Deliberate, but it costs contrast you then buy back in the curve.

## Highlights and Shadows — recovery

These compress detail back into range without moving the endpoints.

- **Highlights negative** recovers sky, skin speculars, bright cloud. **−20 to −45** is normal on a bright file.
- **Shadows positive** opens dark areas. **+15 to +35** is normal on a true Bayer raw.
- **House limit: Shadows +50 on any file, +30 on computational RAW** (Apple ProRAW, Pixel DNG). These are this skill's conservative ceilings, not Adobe figures — the real ceiling is wherever shadow noise appears at 100%. Those phones already lifted the shadows. Lifting again is exactly what produces the grey, dimensionless "HDR" look, and it exposes the noise floor the phone's noise reduction was hiding.
- Heavy Highlights *and* heavy Shadows together flattens the image. If both are past ±40, the image wants a mask, not more global recovery.

## Contrast

A single symmetric S weighted on the midtones. Blunt but honest — you do not choose where it bites, and Adobe documents the weighting as adaptive rather than fixed.

- **+10 to +25** for a flat file. **Negative Contrast** is the fastest route to a soft portrait or a matte look.
- Contrast slightly raises apparent saturation. Set it before judging Vibrance.
- When you want control over *where* the contrast lands, use the tone curve. Contrast pivots where Adobe decided; a curve pivots where you decide.

## Tone Curve

Two modes on mobile: **Parametric** (drag the curve regions — Highlights, Lights, Darks, Shadows — plus range split sliders) and **Point** (draggable points). The Point curve carries four channels, labelled in the mobile UI as **White Channel** (all three at once), **Red Channel**, **Green Channel**, **Blue Channel**. A user hunting for "RGB" will be looking for a label that is not there.

Points are dragged; **mobile shows no numbers on the curve at all** and has no numeric entry. The `input,output` pairs below are the 0–255 scale Lightroom stores in XMP and displays in Classic — on mobile, use them as positions to eyeball, then judge the result on the image.

### White Channel curve — contrast shape

The classic gentle S. Stronger than Contrast +20, far more controllable:

```
0,0   64,58   128,128   192,198   255,255
```

Lower the shadow point, raise the highlight point. The steeper the middle, the more midtone separation.

**Highlight rolloff** — pulling the top point down to `255,248` stops highlights reaching pure white. The single most film-like move available, and it costs almost nothing.

### RGB channel curves — where color grading actually happens

The most powerful and most underused control in Lightroom. Each channel pushes toward its own color when raised, toward its complement when lowered:

| Channel | Raise → | Lower → |
|---|---|---|
| Red | red | cyan |
| Green | green | magenta |
| Blue | blue | yellow |

**Faded film shadows** — lift the bottom-left point of the **Blue** curve from `0,0` to `0,12`. Shadows go cool, blacks lift, the image reads as film. One move, and it does more than any other single channel-curve edit.

**Warm highlights, cool shadows** — the standard cinematic split:
- Blue: `0,10` and `255,245` — blue into shadows, yellow into highlights
- Red: add a point at `192,200` — warmth in the upper midtones

**Correcting a cast in one tonal zone only** — a source with green shadows but neutral highlights is a Green-curve job, not a white-balance job. Pull the Green curve's lower third down slightly and leave its top anchored. White balance moves the whole image; a channel curve moves one zone.

**Restraint:** ±15 on the 0–255 scale is a strong move. ±30 is a look. Past that you are inventing color that was never in the file.

## Common mistakes

| Mistake | Fix |
|---|---|
| Fixing flatness with Clarity or Contrast | Set the endpoints. Whites and Blacks first. |
| Highlights −80 with Shadows +80 | You have flattened the image. Mask instead. |
| Shadows +50 on iPhone ProRAW | The phone already lifted them. Back to +15 and add contrast in the curve. |
| Whites/Blacks before Exposure | Exposure moves the range; you will redo them. |
| Judging exposure by the histogram alone | Judge by the subject. |
