# Test fixtures

Four photographs, committed so the face-segmentation checks in
`tests/test_skill.py` Layer 10 run on CI instead of skipping. Each one is here
because it is a *specific documented failure*, not because it is a nice picture.

All four are from [Pexels](https://www.pexels.com) under the
[Pexels License](https://www.pexels.com/license/): free to use, commercial use
permitted, no attribution required. Attribution is given anyway, because the
photographers deserve it and because a fixture whose provenance nobody recorded
is a fixture nobody can re-license later.

Each is downscaled to a 1024 px long edge and re-encoded at quality 88 — 405 KB
for the set. The segmenter's output is stable across that resize: face share
moves by less than half a point, confidence not at all, and ITA by at most 0.7°,
which crosses no class boundary. Verified before committing, at full size and at
1024, 640 and 480 px.

| File | Photographer | Source | What it is a test of |
|---|---|---|---|
| `portrait-face-against-wood.jpg` | Chris F | [pexels.com/photo/7944975](https://www.pexels.com/photo/7944975/) | **The named failure.** `lookstats.skin()`'s docstring and the README both cite "a face against a wooden wall" as two warm populations rather than one skin tone. This is literally that photograph. Colour alone refuses it; the segmenter measures it at ITA −2.8. |
| `portrait-warm-background.jpg` | Dylann Hendricks | [pexels.com/photo/15286995](https://www.pexels.com/photo/15286995/) | A face filling 38% of a warm frame, refused by colour alone as two warm populations. Measures +34.3 off the segmented face. |
| `portrait-neutral-background.jpg` | Spenc Photo | [pexels.com/photo/36646353](https://www.pexels.com/photo/36646353/) | The control, and the dark end of the range. Colour alone and the segmenter agree here (−32.7), so it guards against a regression rather than demonstrating a fix. |
| `no-face-warm-dune.jpg` | Eclipse Chasers | [pexels.com/photo/26447275](https://www.pexels.com/photo/26447275/) | **A sand dune.** Colour alone reported it as "+37 intermediate" — a human skin tone, for a photograph of a desert. Contains no people at all. |

## Why three portraits and not one

The bug being guarded is **directional**. Before the segmenter, readings were
systematically too dark: the docstring records a light-skinned subject with a
published ITA of +41 to +55 being reported between −3 and −64, as fact. Across
49 photographs the segmented readings moved lighter almost without exception.

A single fixture cannot catch a return of that bias. These three span ITA +34,
−3 and −33 — intermediate, brown and dark — and Layer 10 asserts they stay in
distinct classes. A change that collapsed them toward one answer would go red,
which is the whole point.
