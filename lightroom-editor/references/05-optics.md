# Optics and Geometry

The stage everyone skips. It runs early because lens correction changes geometry, corner brightness, and edge color — everything you judge afterwards is judged against a different image.

## Optics

Three controls on mobile.

### Enable Lens Corrections

Applies Adobe's profile for the lens recorded in EXIF: corrects barrel/pincushion **distortion** and **corner vignetting**.

- **Turn it on by default.** It is a correction toward what the lens actually saw.
- Lightroom matches the profile automatically from EXIF. Mobile does not let you browse and pick a profile by hand the way desktop does — if no profile exists for the lens, the toggle simply has no effect.
- **Phone files (ProRAW, Pixel, HEIC) already have it applied in-camera.** The toggle usually does nothing. That is expected, not a failure.
- **Adapted, vintage and manual lenses often have no profile.** Nothing happens; correct the distortion by hand in Geometry if it matters.
- Corner vignette correction brightens corners, which **raises corner noise**. On a high-ISO file, check the corners after enabling it.
- If the shot depends on the lens's natural corner falloff, enabling correction removes it. Add it back in `03-effects.md` where you control it.

### Remove Chromatic Aberration

Removes lateral color fringing — the red/cyan or blue/yellow edges at high-contrast boundaries, worst toward the corners and on fast wide lenses.

- **Turn it on by default.** It is cheap and nearly always correct.
- The one risk: on images containing genuine fine red/cyan detail against a bright edge, it can desaturate real color. Rare. Check a high-contrast edge at 100% if the image has strongly saturated fine detail.

### Defringe

Handles **longitudinal** (axial) chromatic aberration — the purple or green halo on out-of-focus edges of a fast lens shot wide open. Different problem from lateral CA, and the Remove Chromatic Aberration toggle does not fix it.

Purple Amount, Purple Hue range, Green Amount, Green Hue range. Availability of the global Defringe sliders varies by mobile platform and version; where they are absent, the **Defringe control on a mask** does the same job on the affected region.

Use it when: shooting wide open, high-contrast backlit edges, purple halos on branches against sky or on rim-lit hair. Amount 5–15 is usually enough. Push it too far and it desaturates genuinely purple objects.

## Geometry

Runs after Optics because it operates on the corrected image.

**Upright** modes:
- **Auto** — balanced correction of horizontal and vertical. The safe default.
- **Level** — horizon only. The right choice most of the time; it fixes the one thing viewers actually notice.
- **Vertical** — verticals only. Architecture.
- **Full** — level plus vertical plus aspect. Aggressive; heavy cropping.
- **Guided** — draw two to four reference lines yourself. The most controlled, and the right answer for architecture where Auto guesses wrong.

Manual sliders: Distortion, Vertical, Horizontal, Rotate, Aspect, Scale, X Offset, Y Offset.

**Geometry costs resolution.** Every correction crops. On a 12 MP phone file that matters; on a 45 MP file it does not.

## Order within this stage

1. **Enable Lens Corrections**
2. **Remove Chromatic Aberration**
3. **Defringe**, only if purple/green fringing is actually visible at 100%
4. **Geometry**, only if the horizon or verticals are visibly wrong

## Common mistakes

| Mistake | Fix |
|---|---|
| Skipping Optics entirely | It changes edge color and corner brightness. Two toggles, do them first. |
| Fixing purple fringing with Remove CA | That is lateral CA. Purple halos on defocused edges are Defringe. |
| Enabling lens correction and then wondering why corners are noisy | Vignette correction brightens corners and lifts their noise. Expected. |
| Upright Full on every image | It crops hard. Level fixes the thing people notice. |
| Expecting the lens toggle to do something on a phone file | The phone already corrected it. |
