# Intake

For the two things Step 1 pushes back on rather than records: a vague look word
offered as an Intent, and an Intent that fights the Source or the Destination.

Every number below is a proposal to be ratified, not a constant. The point of
proposing it is that the user can say "no, less" — which is an answer you can
build on, where "moody" was not.

---

## Decomposing a vague look word

A vague word names a family. Prescribing from one is guessing with confidence,
and the guess is invisible to the user until the edit looks wrong.

**The move:** state the concrete reading, put numbers on it, and ask for it to be
ratified. One sentence, then the ladder, then the question. Do not proceed on
silence — a user who has not answered has not agreed, and the whole point of the
gate is that this particular fact cannot be inferred.

Phrase it as a claim they can reject:

> "Moody" I read as: blacks lifted rather than crushed, highlights rolled off
> early, blues pulled down in saturation, shadows cooled. Roughly `Blacks +8`,
> `Highlights −35`, `Blue Sat −15`, shadow grading at 220°. Is that the moody
> you mean, or a darker/warmer one?

### The ladders

Each row is the default reading. Where a word has two common and incompatible
readings, both are given — offer them as a choice rather than picking silently.

| Word | Default reading | Concrete moves |
|---|---|---|
| **Moody** | Lifted blacks, early highlight rolloff, desaturated blues, cool shadows | `Blacks +8`, `Highlights −35`, `Blue Sat −15`, `Blue Lum −10`, shadow grade 220° at 15 |
| | *or* the darker reading: crushed blacks, deep contrast | `Blacks −20`, `Contrast +15`, curve toe pulled down |
| **Cinematic** | Teal shadows, warm skin, wide flat midtones, letterbox contrast | Shadow grade 200° at 20, highlight grade 45° at 10, `Contrast −5`, curve S with a lifted toe |
| | *or* the modern-blockbuster reading: heavy orange-teal separation | `Orange Sat +12`, `Aqua Hue −10`, shadow grade 195° at 30 |
| **Filmic** | Halation-free grain, rolled highlights, slightly lifted black point, muted greens | `Blacks +6`, `Highlights −25`, `Green Sat −18`, `Green Hue +8`, Grain 12/25/50 |
| **Clean** | No grade at all — a correct baseline, nothing creative | Step 3 only; Step 4 does not run |
| **Warm** | Temperature toward amber, not orange skin | `Temp +300K` from the corrected neutral, `Orange Hue +3`, highlight grade 45° at 8 |
| **Punchy** | Contrast and local contrast, not saturation | `Contrast +18`, `Texture +12`, `Whites +12`, `Blacks −12`, `Vibrance +10` before `Saturation` |
| **Soft** | Reduced local contrast and a lifted toe, not blur | `Clarity −8`, `Texture −10`, `Blacks +10`, `Highlights −15` |
| **Vintage** | Faded black point, cross-processed shadows, muted primaries | `Blacks +14`, `Saturation −12`, shadow grade 180° at 18, highlight grade 40° at 12 |
| **Airy** | High key, cool-neutral, protected highlights | `Exposure +0.30`, `Blacks +12`, `Highlights −20`, `Vibrance +8` |
| **Gritty** | Local contrast and grain, cool cast, deep blacks | `Texture +18`, `Clarity +12` (house limit), `Blacks −18`, `Saturation −15`, Grain 20/30/60 |

### When the word is not on the list

Ask what it is standing in for, in terms the user does have: is it brighter or
darker than the photo now, warmer or cooler, more contrast or less, more colour
or less. Four answers give you a reading you can propose. That is still a
decomposition — it is just built from the user's comparatives instead of a
stored ladder.

A reference image, where one exists, ends the argument faster than any of this.
Ask for one before working through the ladder blind.

---

## Conflict archetypes

An Intent that fights the Source or the Destination is a conflict, not a brief.
Delivering the recipe anyway produces a preset that is wrong on purpose and
looks like an error.

**The move:** name the conflict in one line, give the cost of each side, and stop.
The user picks which side wins. Do not resolve it yourself — both sides are
defensible, and which one matters is not a fact about the file.

Phrase it as two costs, not as a warning:

> Deep-black print look on an 8-bit JPEG: honour the look and the sky bands
> visibly at `Blacks −25`; honour the file and blacks stop at −8, which reads
> softer than the reference. Which one do you want?

### The archetypes

| Conflict | Honouring the Intent costs | Honouring the file or destination costs |
|---|---|---|
| **Crushed blacks on an 8-bit JPEG** | Visible banding in skies and gradients; no recovery available | Blacks stop near −8; the look reads softer than the reference |
| **Shadow lift on ProRAW / Pixel DNG** | The flat HDR look — the phone already spent that latitude | Shadows stay at the +30 house limit; deep areas stay genuinely dark |
| **Heavy Clarity on a portrait** | Skin texture becomes pores and blemishes; ageing effect | Clarity stays ≤ +15 and the punch comes from the curve instead |
| **Saturated grade for print** | Out-of-gamut colour that prints dull or shifts hue on paper | Saturation pulled back; the screen version looks tamer than intended |
| **Deep contrast for phone-screen viewing** | Shadows read as pure black on an OLED at low brightness | Contrast held back; the image looks flatter on a desktop monitor |
| **Film grain plus heavy noise reduction** | The two fight; grain looks like plastic over a smoothed base | Pick one — NR for a clean file, grain for a filmic one |
| **Reference look on a different source** | The reference's camera character is imitated on top of this file's own | Correct this file first; the look lands close but not identical |
| **A look built on masks, delivered as a portable preset** | The preset carries nothing that moved the reference's subject | The set gets a global preset and the masks are applied per photo |
| **"Clean and accurate" plus a strong look word** | The two Intents are different edits; one of them is not what they meant | Ask which they actually want — this is the cheapest conflict to resolve |

### When the conflict is with the Fidelity answer

A stated deviation can turn an apparent conflict into a settled one. "Match the
reference" on a file with less latitude is a conflict; "the reference's family,
about 8° warmer and less contrast" is a brief. Where the user has given a
deviation, check the conflict against the deviated target, not against the
reference — and record the number with the preset, because it is not recoverable
from the files afterwards.
