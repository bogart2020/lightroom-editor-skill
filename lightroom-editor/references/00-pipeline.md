# Pipeline and order

## Lightroom applies edits in a fixed internal order

The order the user drags sliders is irrelevant. Lightroom always processes in the same sequence:

`Demosaic → Profile → White balance → Exposure & tone → Texture/Clarity/Dehaze → Vibrance/Saturation → Color Mix → Color Grading → Tone curve → Detail → Grain → Optics → Geometry → Masks`

The order matters for a different reason: **each stage changes what you are looking at when you judge the next one.** Set contrast before white balance and you are judging contrast through a color cast. Sharpen before noise reduction and you sharpen the noise.

## The working order

Work in the order below. It is chosen so every judgement is made against a correct picture.

| # | Stage | Why here |
|---|---|---|
| 1 | **Profile** | Changes every pixel. Nothing judged before it survives. |
| 2 | **Optics** | Lens correction shifts geometry and edge color. Do it before composing or judging corners. |
| 3 | **White balance** | Removes the color cast so every later color decision is honest. |
| 4 | **Exposure** | Sets overall brightness. Everything tonal is relative to it. |
| 5 | **Whites / Blacks** | Sets the endpoints of the tonal range. |
| 6 | **Highlights / Shadows** | Recovery, judged against fixed endpoints. |
| 7 | **Contrast / Tone curve** | Shapes what is now a correctly-ranged image. |
| 8 | **Color Mix, Color Grading** | Color styling on a neutral, correctly-toned base. |
| 9 | **Effects** | Texture, Clarity, Dehaze, Vignette, Grain. |
| 10 | **Detail** | Sharpening and noise, judged last because everything above changed the noise floor. |
| 11 | **Masks** | Anything a global slider cannot do without collateral damage. |

**Exposure before Whites/Blacks, not after.** Exposure moves the whole range; setting endpoints first means resetting them.

**Detail last, always.** Dehaze, Shadows, and Clarity all amplify noise. Sharpening and noise reduction tuned before those moves will be wrong after them.

## Reading the histogram on mobile

Two-finger tap on the image toggles the histogram. Tap the histogram itself to cycle its display.

- **Blue overlay** on the image = shadow clipping (pure black, no detail).
- **Red overlay** = highlight clipping (pure white, no detail).
- Mobile does **not** show numeric RGB readouts on touch-hold. Desktop Classic does; do not tell the user to look for a number that is not there.

**Clipping is not automatically wrong.** Specular highlights — sun on water, a light bulb, a chrome reflection — *should* clip. A clipped face or a clipped sky with visible structure is a problem. Judge by what is clipping, not by whether anything is.

## Where the tonal sliders actually live

The six Light sliders overlap. Knowing where each one bites prevents fighting them against each other:

```
black ──── shadow ──── midtone ──── highlight ──── white
 │           │            │             │            │
Blacks    Shadows      Contrast     Highlights    Whites
 └── endpoint          Exposure ──── whole range ──┘
```

- **Whites / Blacks** set the endpoints — where the image stops.
- **Highlights / Shadows** recover detail *inside* those endpoints.
- Recovering highlights and then pulling Whites down is doing the same job twice and produces the grey, flat, "HDR" look.

## What to fix first when everything is wrong

Diagnose in this order and stop at the first true statement:

1. **Is the color cast?** → white balance, `02-color.md`. Never fix a cast with Color Mix.
2. **Is it exposure?** → `01-light.md`.
3. **Is it flat?** → endpoints first (Whites/Blacks), then curve. Not Contrast, not Clarity.
4. **Is it noisy or soft?** → `04-detail.md`, and check whether an earlier move caused it.
5. **Is it only wrong in one region?** → `06-masking.md`.
