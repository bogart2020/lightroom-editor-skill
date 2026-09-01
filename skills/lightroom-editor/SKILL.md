---
name: lightroom-editor
description: Use when editing a photo in Adobe Lightroom mobile — building an edit from RAW or JPEG, replicating a look from a reference image, creating or exporting a preset, critiquing an edit that looks wrong, or working around a camera system's known bias (Sony green cast, Canon magenta, Apple ProRAW baked-in tone mapping).
license: MIT
---

# Lightroom Mobile Editor

Photo editing in Adobe Lightroom mobile, driven by two ideas in fixed order:

**Baseline before look.** Every file arrives with its *source* character already baked in — a cast, a tone-mapping decision, a sharpening pass someone else chose. Neutralise that first and you are grading a clean image. Skip it and every creative move fights an error you never named.

**Restraint.** Numbers here are deliberately conservative house limits, not Adobe figures — they are chosen so an edit survives scrutiny at full size. When a stronger move is available, name it and let the user ask for it.

## Scope

Adobe Lightroom mobile (iOS/Android), **Adobe Color** profile as the default starting point. Everything is expressed as slider values the user types by hand, and optionally as an `.xmp` preset.

**Whether you can see a RAW file depends on where you are running.**

- **Chat only** (no shell, no filesystem): `.ARW`, `.CR3`, `.NEF`, `.RAF`, `.DNG` do not render. Say so plainly and ask for a JPEG export or a screenshot — then continue; a described photo is still workable.
- **With a code environment**: decode it. `rawpy`/`libraw` reads the sensor data, `exiftool` reads the metadata, and DNGs carry an embedded JPEG preview you can extract and look at directly. Measure rather than assume — black point, clipping, and neutral balance are all readable, and a measured file beats a described one.

Check which case you are in before declining.

## Step 1 — Intake

**No slider number leaves this step until the gate is open.** Interview before
prescribing, and do not guess an answer you could have asked for.

### The gate

Four answers are load-bearing, plus a fifth whenever a reference image is
attached. Until every one of them is settled, Step 2 does not run and no
number appears in the reply — not one, not "roughly".

| Gate | What it decides | Settled by |
|---|---|---|
| **Source** — camera or phone, and file type | The whole baseline. See `references/07-sources.md` | **Measurement**, where the file or its EXIF is readable; otherwise the user |
| **Subject** — portrait, landscape, street, food, product, night | What is protected and what is expendable | **Measurement**, where the image is visible; otherwise the user |
| **Intent** — the look you want, or "clean and accurate" | Whether Step 4 runs at all | The user only |
| **Destination** — print, web, phone screen, client delivery | Sharpening, noise, and how far color can go | The user only |
| **Fidelity** — *only when a reference image is attached:* match it, or use it as a starting point, and in which direction | Whether the recipe is faithful to the reference or deliberately off it. See `references/08-looks.md` | The user only, and the answer must carry a number |

A fact is yours to find, never the user's to supply: read the EXIF, decode the
file, look at the image. A decision is the user's, and no amount of context
makes it inferable.

Not gated: **Reuse** — one photo or a set; assume one, say so, and offer the
preset in Step 6 — and **What you have**, which is visible from the
conversation.

Ask every outstanding gate as one numbered block, each with your recommended
answer, so the whole gate is visible and can be settled in one reply. The
challenges that follow — a vague word, a conflict — come one at a time.

### The only way past the gate

The gate holds against silence, against a vague answer, and against impatience.
It opens on one thing: the user saying **`skip intake`**, or an unmistakable
equivalent of those words. Then, and only then, prescribe on assumptions — and
the Verdict leads with every assumption the skip forced, one line each.

"Just give me something", "you decide", and no reply at all are not the phrase.
They are the case the gate exists for.

### Where the gate applies

Every path that ends in slider values: building an edit, replicating a look,
critiquing an edit. The one exemption is mechanical conversion — the user hands
over final values and wants them written as an `.xmp` — because nothing is being
decided.

### Two things to push back on rather than record

**A vague look word is not an Intent.** "Moody", "cinematic", "filmic",
"clean", "warm", "punchy", "soft", "vintage" — each names a family, not a
target, and prescribing from one is guessing with confidence. Propose the
concrete reading — which zones move, which bands, how much rolloff — and get it
**explicitly ratified**. Silence is not ratification.
`references/11-intake.md` carries the decompositions.

**An Intent that fights the Source or the Destination is a conflict, not a
brief.** A deep-black print look on an 8-bit JPEG, a heavy shadow lift on
ProRAW, +40 Clarity on a portrait. Name the conflict in one line with the cost
of each side, then stop and let the user pick which side wins.
`references/11-intake.md` carries the archetypes.

**Ask Fidelity with the numbers already attached.** Nobody answers "how close?"
in degrees, so do not ask for degrees — offer the buckets, and let the choice
*be* the number. The verifier and `scripts/look-match.py --warmer/--cooler` both
need a figure, and this is where it comes from:

| Offer this | It means | Deviation |
|---|---|---|
| **Match closely** | Land on the reference; full intensity | `±3°` |
| **Same family, my own take** | The reference's character, not its exact temperature | `±10°` |
| **Loose inspiration** | A starting point to move well away from | `±20°` or more |

Then say which direction — warmer, cooler, more contrast, more muted — and
record the signed number with the preset. If the user answers in words instead
("a bit warmer, not that orange"), map it to the nearest bucket, state the
number you mapped it to, and let them correct it. A qualitative answer is fine;
an unrecorded one is not.

**Fidelity is the one that cannot be inferred.** A reference image tells you what
*it* looks like, never how close the user wants to land. "Warm and golden" is a
different target from an album cover that measures orange, and a recipe faithful
to the reference is then wrong on purpose. Ask, put a number on the answer
("about 8° warmer"), and record it with the preset — it is not recoverable from
the files afterwards.

## Step 2 — Verdict

Open with the **receipt** — one line naming what the gate settled and how, so a
skipped gate is visible in the answer itself and not only in the transcript:

`Sony ARW (measured) · muted-warm (ratified) · portrait · web · single photo`

After a `skip intake`, the receipt is replaced by the assumptions the skip
forced, one line each, each marked `assumed`.

Then, before any slider, a short verdict the user can disagree with:

- **Source character** — what this file's origin does to it. With a code
  environment, `scripts/look-analyze.py --source FILE` measures it off the
  photograph in front of you rather than assuming it: it reports the cast in
  CIELAB, and the Tint that undoes it, probed on this file. Where the frame
  holds too little near-neutral content to read — a forest, a sunset, anything
  without something that ought to be grey — it prints `WITHHELD` with the
  reason and no number, and `references/07-sources.md` fills in as the
  fallback. Say which one you used: a profile figure is **unmeasured**, and
  reporting it as measured is the failure this whole step exists to prevent.
- **Headroom** — how much recovery latitude exists. A true Bayer raw has a lot. Apple ProRAW and Pixel DNG have far less, because the tone mapping already spent it. An 8-bit JPEG has almost none and bands when pushed.
- **What is actually wrong** — read from the image if you have it, from the description if not.

## Step 3 — Baseline

Build the corrective edit in **pipeline order**. The order is not cosmetic: each stage changes what the next one sees. `references/00-pipeline.md` explains why, and is the file to read when unsure what to fix first.

1. **Profile** → Adobe Color, unless `references/07-sources.md` names a better one for this source.
2. **Optics** → `references/05-optics.md`. Lens profile and CA first, because they change edge color and geometry everything else is judged against.
3. **White balance** → `references/02-color.md`. Neutralise the source cast here, not later with HSL.
4. **Light** → `references/01-light.md`. Exposure, then the black and white points, then the recovery sliders.
5. **Tone curve** → `references/01-light.md`. Contrast shape and per-channel color balance.
6. **Color** → `references/02-color.md`. Color Mix and Color Grading.
7. **Effects** → `references/03-effects.md`. Texture, Clarity, Dehaze, Vignette, Grain.
8. **Detail** → `references/04-detail.md`. Sharpening and noise, judged at 100%.
9. **Masks** → `references/06-masking.md`. Everything a global slider would damage.

Reach for a mask the moment a global move helps one region and hurts another — a recovered sky that greys the subject, a lifted subject that fogs the background. `references/06-masking.md` carries the standard recipes.

## Step 4 — Look

Runs only when the user wants one. `references/08-looks.md` covers all four routes: decomposing a reference image into slider moves, film emulation, modern digital looks, and genre baselines.

Where a reference image exists and there is a code environment, decompose it by
measurement before reasoning about it: `scripts/look-analyze.py REFERENCE.jpg`
gives the band shares, the hue range in RGB-wheel degrees, the per-zone cast
and the black point. Read the numbers and choose the sliders yourself — the
script deliberately does not. The hue range it prints is the same range Step 5
will hold the preset's Color Grading hues against, so a grade chosen outside it
is a failure you can see coming.

## Step 5 — Verify

A gate on Step 6, not a footnote. A recipe that has not been through it is
delivered marked **unverified**, and says why.

Both the gate and the analysis measure through one module,
`scripts/lookstats.py`, so the report and the gate can never disagree about
what colour the reference is. Its figures are CIE L*a*b* for anything
perceptual and RGB-wheel degrees for anything compared against a `crs:` hue
value, which is the wheel those attributes use.

Run `scripts/look-match.py` first wherever a reference exists — it needs only
the reference and the `.xmp`, costs milliseconds, works with no source photo,
and catches a recipe that grades bands the reference does not contain before
any rendering happens. Then, with a code environment, `scripts/crs-render.py`
renders the recipe onto the source photo and `scripts/tune.py` scores and tunes
it.

- **Target.** With a reference image: perceptual distance to the reference,
  offset by the stated Fidelity deviation. Without one: measurable correctness —
  neutral white balance on content that should be neutral, the black point where
  Step 3 intended it, no clipped highlights, no crushed shadows.
- **Score.** Mean CIEDE2000 between **tonal zones** — both images bucketed by
  luminance, zone mean colours compared — plus the worst zone. Zones rather than
  pixels because a reference is usually a different photograph, and a pixel-wise
  comparison would measure the difference in subject rather than in grade. The
  loop stops at **mean ΔE00 ≤ 1.0 with no zone above 2.0** — the published
  perceptibility thresholds. A percentage is printed beside it for readability,
  derived by the formula stated in `scripts/tune.py`; the ΔE is the gate.
- **What may be tuned.** Only **Temperature, Tint, Exposure, the tone-curve
  points, and the white and black endpoints**. These are the controls whose
  behaviour is derivable from the DNG specification and Adobe's own published
  rendering code. Everything else — Highlights, Shadows, Clarity, Texture,
  Dehaze, Color Grading, per-band HSL — holds exactly what Step 3 and Step 4 set,
  and is reported as unmodelled.
- **Bounds.** The house limits under Red flags are hard constraints. The
  optimiser may not cross one to gain score.
- **Portability.** Exposure, Temperature and Tint are tuned as part of the
  recipe the user types, and stripped from any `.xmp` written — they are
  per-photo, and a preset carrying them applies one photo's correction to a
  whole set. `IncrementalTemperature`/`IncrementalTint` are the portable pair.
- **Stopping.** Twelve iterations, or three rounds without meaningful
  improvement, whichever comes first. Ship the best-scoring recipe with the score
  it actually reached, never the threshold it was aiming at.

**Coverage is part of the result**, always reported beside the score:
`mean ΔE00 0.8 · worst region 1.6 · verified across 6 of 11 moved sliders;
Clarity +12, Dehaze +8 unmodelled`. A good score on a look built mostly from
unmodelled sliders is not a verified preset and must never read as one.

**What the score is not.** It measures agreement with this repo's renderer,
which approximates Camera Raw and does not reproduce it — Adobe's published DNG
SDK implements none of the PV2012 develop pipeline, and the math behind Clarity,
Texture, Dehaze and Color Grading is unpublished. Say "verified against our
renderer". Never say "matches Lightroom".

**With no code environment** — chat only, no shell — none of this runs. Say so
plainly, deliver the preset marked unverified, and offer the two ways to close
it: run the scripts in a code environment, or apply the preset in Lightroom and
send back the export. Never imply a score you did not measure.

**With a code environment but no `scripts/` directory** — check before you rely
on them; some installs carry only `SKILL.md` and `references/`. This is not a
reason to refuse the preset, and not a reason to claim a verification that never
ran. Say which scripts are missing, measure what you can by hand — reference
hue range, black point, clipping, per-band content are all readable with any
image library — deliver the preset marked unverified, and name what the missing
gate would have caught. The Red flags below require the scripts to be *run*
where they exist, not invented where they do not.

Masked adjustments pass through untouched and are counted as unverified; the
renderer models global sliders only.

## Step 6 — Deliver

Every answer ends with these five parts, in this order:

1. **Verdict** — receipt, then source, headroom, diagnosis. Two or three sentences.
2. **Recipe** — panel by panel in pipeline order. Every line is `Slider → value`, with a short why. Give exact numbers, never "increase slightly". Omit any slider you are not moving. Where Step 5 moved a slider, append what the move earned — `Blacks → −14 (seed −8, −0.4 ΔE)` — so the tuning is visible and arguable.
3. **Check yourself** — the specific things to look at on this image before calling it done, from `references/10-diagnostics.md`. Tailored to what this recipe risks, not a generic list.
4. **Score** — what Step 5 measured, with its coverage; or `unverified` and the reason. Never a number you did not measure.
5. **Preset** — offer it when the user has a set to edit. `references/09-presets-xmp.md` has the XMP template, the attribute map, and the mobile import path.

Done means all five parts are present and every number in the recipe is a number.

## Routing

Read the file when its branch fires. Do not read all of them.

| Branch | File |
|---|---|
| What to fix first, why order matters, reading the histogram | `references/00-pipeline.md` |
| Exposure, contrast, highlights, shadows, whites, blacks, tone curve, RGB channel curves | `references/01-light.md` |
| White balance, vibrance, saturation, Color Mix (HSL), Color Grading, profiles | `references/02-color.md` |
| Texture, clarity, dehaze, vignette, grain | `references/03-effects.md` |
| Sharpening, luminance noise, color noise | `references/04-detail.md` |
| Lens corrections, chromatic aberration, defringe, geometry | `references/05-optics.md` |
| Any edit that should apply to part of the frame only | `references/06-masking.md` |
| Identifying the source and its bias; unknown or unlisted cameras | `references/07-sources.md` |
| Replicating a reference image, film emulation, named looks, genre starting points | `references/08-looks.md` |
| One look shipped for several cameras or phones — a preset family | `references/08-looks.md` Route 5, with `references/07-sources.md` |
| Writing an `.xmp`, attribute names, importing a preset on mobile | `references/09-presets-xmp.md` |
| Critiquing an existing edit; something looks wrong and the user cannot name it | `references/10-diagnostics.md` |
| A vague look word to decompose, or an Intent that fights the Source or Destination | `references/11-intake.md` |

## Red flags

Each of these means stop and correct course:

- About to give a range instead of a number → pick the number.
- About to emit a slider number with a gate still unanswered → stop and ask. Silence, vagueness and impatience do not open the gate; only `skip intake` does.
- About to accept a vague look word as an Intent → decompose it and get the reading ratified first. "Moody" is a family, not a target.
- About to prescribe without knowing the source → ask; the source decides the baseline.
- Fixing a color cast with Color Mix or Color Grading → white balance owns casts. Correct it upstream.
- Pushing Shadows past +30 on Apple ProRAW or Pixel DNG → the phone already lifted them, and re-lifting is the usual cause of the flat HDR look. +30 is this skill's house limit; the real ceiling is wherever shadow noise appears at 100%.
- Recommending Clarity above +15 or Dehaze above +10 → these are house limits, not hard rules. If the image truly needs more, say why.
- Judging sharpening or noise at fit-to-screen → both are 100%-zoom decisions.
- Offering a preset that carries Exposure, Temp, or Tint → those are per-photo. A portable preset omits them. `IncrementalTemperature`/`IncrementalTint` are the portable pair, but `IncrementalTint` positive is *toward magenta* — check the sign in `references/09-presets-xmp.md`.
- Writing a tone curve without `ToneCurveName2012="Custom"` → Lightroom discards every curve silently, including the Blue curve that carries warm highlights. This is the most common cause of "I asked for golden and got orange".
- Adjusting a hue band the reference image does not contain → read the reference's band content first (`references/08-looks.md`).
- Handing over a preset without running `scripts/preset-check.py` and `scripts/look-match.py` → both catch failures that are invisible until the user applies the preset. If the scripts are absent from this install, say so and mark the preset unverified; never report a check you did not run.
- Reporting a score without its coverage, or calling a score a Lightroom match → the renderer approximates Camera Raw and does not reproduce it. Report what was verified and what was not modelled.
- Letting the tuner move Clarity, Texture, Dehaze, Highlights, Shadows, Color Grading or a hue band → none of them is modelled. Step 5 tunes white balance, exposure, the curve and the endpoints; the rest holds what Step 3 and Step 4 chose.
