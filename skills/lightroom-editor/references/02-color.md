# Color

White balance, vibrance/saturation, Color Mix (HSL), Color Grading, and profiles.

## Quick reference

| Control | Range (RAW) | Range (JPEG/HEIC) | Default |
|---|---|---|---|
| Temp | 2000 … 50000 K | −100 … +100 | As Shot |
| Tint | −150 … +150 | −100 … +100 | As Shot |
| Vibrance | −100 … +100 | same | 0 |
| Saturation | −100 … +100 | same | 0 |
| Color Mix — Hue / Sat / Lum, per band | −100 … +100 each | same | 0 |
| Color Grading — Hue | 0 … 359 (wraps) | same | 0 |
| Color Grading — Saturation | 0 … 100 | same | 0 |
| Color Grading — Luminance | −100 … +100 | same | 0 |
| Blending | 0 … 100 | same | 50 |
| Balance | −100 … +100 | same | 0 |

## Profile

**Adobe Color is Adobe's default profile for RAW and the right starting point.** It is their modern general-purpose rendering, and every recipe in this skill assumes it unless stated otherwise.

Available for RAW: Adobe Color, Adobe Standard, Adobe Landscape, Adobe Portrait, Adobe Vivid, Adobe Neutral, Adobe Monochrome, plus **Camera Matching** profiles that emulate the manufacturer's own JPEG rendering (Camera Standard, Camera Neutral, Camera Portrait, and so on — availability varies by body). Newer versions add the **Adaptive** group — **Adaptive Color** and **Adaptive B&W** — AI per-image profiles that require RAW or DNG.

For **JPEG/HEIC the Basic group holds only Color and Monochrome** — the raw rendering is baked in, so Adobe Raw and Camera Matching are unavailable. Creative profiles (Artistic, B&W, Film-Inspired, Modern, Vintage) still apply to any file type and carry an Amount slider, but those are a *look*, not a baseline. Treat Color as the fixed starting point on non-raw files.

**When to leave Adobe Color:**
- **Adobe Standard** — flatter and more neutral. The better base when you are grading heavily and want Adobe's opinion out of the way.
- **Camera Matching** — when the user wants the look they saw on the camera's rear screen. It genuinely helps some Sony and Nikon files. But it is a *different* rendering, not a fix: it trades Adobe's bias for the manufacturer's. Say that when you recommend it.
- **Adaptive Color** — often works better on computational RAW (ProRAW, Pixel), where baked-in tone mapping fights a fixed profile. This is a judgement call, not a documented recommendation.

Profile changes everything downstream. Choose it first, then build.

## White balance

**Temp and Tint own color casts. Nothing else does.** Correcting a cast with Color Mix or Color Grading leaves the error in the file and paints over it — the cast returns the moment you touch anything else.

On RAW, Temp is a true Kelvin value applied before demosaic, so it costs nothing across a normal range. Extreme settings still amplify one channel's noise and can push a channel to clip. On JPEG/HEIC it is a relative ±100 nudge around the baked-in value, and it degrades as you push it.

**Presets:** As Shot, Auto, Daylight, Cloudy, Shade, Tungsten, Fluorescent, Flash, Custom. RAW gets all of them; JPEG/HEIC gets As Shot, Auto, and Custom only.

### The two axes

- **Temp** — blue ↔ yellow. Raise for warmer.
- **Tint** — green ↔ magenta. Raise for magenta.

Most source casts are a **Tint** problem, not a Temp problem. Sony's green and Canon's magenta both live on the Tint axis. Reaching for Temp when the cast is green produces a warm *and* green image.

### Setting it

1. **Eyedropper on a true neutral** — concrete, white paint, grey clothing, the whites of eyes. Not skin, not sky, not foliage.
2. **No neutral available?** Set Temp by feel on the subject, then fix the residual cast on Tint alone.
3. **Golden hour is a trap.** Auto WB will neutralise the warmth that is the entire point of the photograph. Start from Auto's value and push Temp up until the warmth reads as light rather than as a cast, then stop.

### Skin

Skin is the reference every viewer checks unconsciously. Judge white balance on skin last, and know that **skin tone is not one target.** Deep skin holds more red and less yellow; a "correct" warm push tuned for pale skin turns deep skin orange and flat. Light skin shows a green cast as sallow; deep skin shows it as ashy or grey. Correct the *cast* against a neutral object, then check skin — do not warm skin until it matches an imagined average.

## Vibrance and Saturation

Different algorithms, not different strengths.

- **Saturation** is linear: every color moves by the same amount. Colors already near-saturated clip and lose detail first.
- **Vibrance** is non-linear and protective: it lifts muted colors most, already-saturated colors least, and explicitly protects skin-tone hues.

**Vibrance first, almost always.** Typical: **Vibrance +8 to +20**. Saturation stays at 0 or goes slightly negative.

**Negative Saturation with positive Vibrance** (`Saturation −10, Vibrance +15`) is a genuinely useful combination: it pulls the loudest colors back while keeping the quiet ones alive. This is much of the muted-editorial look.

Saturation above +20 is a red flag on any image containing a person.

## Color Mix (HSL)

Eight bands: **Red, Orange, Yellow, Green, Aqua, Blue, Purple, Magenta.** Each has Hue, Saturation, Luminance, all −100…+100. Mobile has a targeted-adjustment mode: tap the target icon, then drag on the image to move whichever bands that pixel belongs to.

**What each band actually contains:**

| Band | Real-world content |
|---|---|
| Red | Deep skin shadows, lips, brick, red clothing |
| **Orange** | **Skin — all skin tones.** Sand, wood, autumn leaves |
| Yellow | Highlights on skin, foliage in sun, gold, sand |
| Green | Foliage, grass |
| Aqua | Water, the pale band of sky near the horizon |
| Blue | Sky, deep water, shade, denim |
| Purple | Sunset gradient, flowers, some fringing |
| Magenta | Flowers, sunset edges, some skin cast |

**Orange is skin.** Almost every skin adjustment is Orange, with Red as its partner for deeper skin and shadowed skin. Move Orange with care and small numbers.

### The moves that matter

**Skin, all tones:** `Orange Sat −5 to −12`, `Orange Lum +5 to +10`. Slightly desaturated and slightly lifted reads as clean skin. For deeper skin add `Red Lum +5` rather than pushing Orange further — deep skin lives across Red and Orange, and pushing Orange alone shifts hue instead of brightness.

**Orange skin (the most common failure):** `Orange Hue +4 to +8` moves skin back toward yellow and away from tan. Pair with `Orange Sat −8`.

**Sky:** `Blue Sat +8 to +15`, `Blue Lum −10 to −20`. Darkening blue is what makes a sky look deep — not saturating it. `Aqua Hue +10` pulls a cyan sky toward true blue.

**Foliage:** `Green Hue +10 to +20` moves grass away from the yellow-green digital cameras produce, toward a believable green. `Yellow Hue +8` does the same for sunlit leaves.

**Muted look:** pull Sat down 10–20 on every band *except* Orange — skin keeps its colour while the surroundings drain.

### Color Mix is not a cast fixer

If every band needs the same correction, the problem is white balance. Go back to Temp/Tint.

## Color Grading

Four wheels — **Shadows, Midtones, Highlights, Global** — each with Hue (0–359, wrapping), Saturation (0–100), Luminance (−100…+100). Plus two sliders that control how the wheels interact.

**Blending (0–100, default 50)** — how much the three zones bleed into each other. Low = hard-edged separation between graded zones. High = smooth, subtle, everything blends. Raise it when the grade is showing edges; lower it when the grade looks washed out and undefined.

**Balance (−100…+100, default 0)** — weights the effect between the wheels. **Positive increases the effect of the Highlights wheel; negative increases the effect of the Shadows wheel.** Use it when a grade is landing on the wrong part of the image.

### Useful hue values

| Hue | Color | Common use |
|---|---|---|
| 30 | Orange | Warm highlights, skin, golden hour |
| 45 | Amber | Warm highlights, gentler than 30 |
| 60 | Yellow | Sunlight, vintage highlights |
| 180 | Cyan | Cool shadows, cinematic |
| 210 | Blue | Cool shadows, night, film shadows |
| 240 | Deep blue | Strong cool shadows |
| 300 | Magenta | Counteracting green, sunset |

### The standard grades

**Teal and orange (cinematic):**
- Shadows: Hue **210**, Sat **12**
- Highlights: Hue **40**, Sat **10**
- Blending **50**, Balance **0**

**Warm film:**
- Shadows: Hue **30**, Sat **8**
- Highlights: Hue **50**, Sat **12**
- Balance **+10** — positive, so the warm Highlights wheel carries more of the grade

**Faded matte:**
- Shadows: Hue **210**, Sat **10**, Luminance **+8**
- Global: Sat **5**, Hue **30**

**Restraint:** Saturation **8–15** on a wheel is a real grade. Above **25** it stops reading as light and starts reading as a filter. If a grade needs more than 25 to be visible, the problem is that the tone curve has no contrast for it to sit on.

### Color Grading vs RGB curves

Both tint tonal zones. Color Grading is faster and more intuitive; RGB channel curves (`01-light.md`) are more precise and let you control exactly where the transition falls. Use Color Grading to design the look, and channel curves when it needs to be exact.

## Common mistakes

| Mistake | Fix |
|---|---|
| Fixing a green cast with `Green Sat −25` | The cast is on the Tint axis. Fix it in white balance. |
| Warming skin with Temp when the cast is green | Temp is blue↔yellow. Green lives on Tint. |
| Saturation +30 to make an image "pop" | Vibrance +15 and Blue Lum −15. |
| Warming skin to a remembered average | Neutralise against a neutral object, then check skin. Skin tone is not one target. |
| Color Grading saturation at 40 | The image lacks contrast, not color. Fix the curve. |
| Orange Sat −30 for "clean skin" | Skin goes grey and dead. −8 is a strong move. |
