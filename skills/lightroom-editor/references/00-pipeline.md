# Pipeline and order

## Why order matters

Lightroom is non-destructive and the order you drag sliders in does not change the final result. Adobe does not publish the internal processing order, and you do not need it.

What matters is that **each stage changes what you are looking at when you judge the next one.** Set contrast before white balance and you are judging contrast through a color cast. Judge sharpening before noise reduction and you are judging the wrong image. The working order below is about making every judgement against a correct picture — it is workflow, not a claim about Adobe's code path.

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

Two-finger tap on the image **cycles** the overlay: info → histogram → off. It may take more than one tap to reach the histogram. Recent versions also expose it as a persistent setting under **⋯ → View Options**.

On mobile, clipping is a **held preview, not a latched overlay**: open a tone slider (Exposure, Highlights, Whites, Blacks) and two-finger tap-and-hold on it. The overlay appears only while held.

- **Blue** = shadow clipping. **Red** = highlight clipping.
- **Yellow, cyan, magenta** mean only some channels are clipped — useful, and easy to misread as an error.
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
