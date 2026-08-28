# Sources

Every file arrives with its origin's character already baked in. Name it before you edit, or you spend the whole edit fighting an error you never identified.

Two things to establish: **what the file actually is**, and **how much headroom it has left**.

## Headroom

How much latitude remains for recovery. It decides how hard you are allowed to push.

| File | Headroom | Practical limit |
|---|---|---|
| True Bayer RAW (Sony, Canon, Nikon, Fuji, Panasonic, Leica) | High | Commonly 1–2 stops of highlight recovery depending on body, ISO and how cleanly the channels clipped; shadows tolerate large lifts before noise dominates |
| Computational RAW (Apple ProRAW, Pixel DNG) | Mixed | *Shadow* latitude is largely spent — that is the constraint. Highlight headroom is retained and reachable; see the ProRAW section |
| HEIC (10-bit) | Low | Small moves; some banding resistance |
| JPEG (8-bit) | Very low | Clipped is gone; banding appears quickly on smooth gradients — check skies after every tonal move |

**The headroom rule:** a computational RAW is a real raw container — true Kelvin white balance, 12-bit linear encoding, full profile support — but most of its *tonal* latitude has already been spent. Push color and highlights like a raw; push shadows like a JPEG.

---

## Apple ProRAW (iPhone, `.DNG`)

**What it is:** not a virgin Bayer file. ProRAW is a *linear* DNG that has already been demosaiced, multi-frame merged (Deep Fusion, Smart HDR, Night mode), locally tone-mapped, sharpened, and noise-reduced. Apple's entire computational pipeline ran before the file was written. You are editing Apple's rendering, in a container that gives you raw-like white balance and 12-bit depth.

**Character:**
- **Shadows are already lifted.** The local tone mapping spent that latitude for you, so a second lift buys nothing.
- **Highlights are tone-mapped, not clipped.** Apple deliberately underexposes in high-contrast scenes to protect highlights, and the above-SDR values are still in the file. Lightroom exposes an **Apple ProRAW Amount** slider controlling how much of that range gets compressed into SDR. Highlight headroom is the one thing ProRAW keeps.
- **Halos around high-contrast edges** — a rim-lit head against sky, a horizon, a backlit branch. Baked in by the local tone mapping and Apple's sharpening. Hard to remove: backing off Sharpening and masking the affected edge helps, global sliders do not, and Clarity/Dehaze make them worse.
- **Watercolour texture** in foliage, fabric and fine detail, from aggressive noise reduction plus sharpening.
- **Highlights commonly read yellow** on the Apple ProRAW profile.
- **Semantic per-region processing** — Apple segments people, skin and sky during capture, processes them differently, and stores those masks in the DNG. The uneven starting point is real. Lightroom does not consume the masks, so you cannot undo the segmentation, only compensate locally.

**Editing implications:**
- **Lifting Shadows again is the mistake** — the usual cause of the flat, grey, "phone HDR" look. The phone already lifted them, so a second lift removes the last dimension and exposes the noise floor. There is no fixed ceiling: check shadow noise at 100% and stop when it appears, which is well below where you would stop on a Bayer file. This skill's house limit is +30.
- Add contrast in the **tone curve**, not in Shadows/Highlights. Deepening blacks with Blacks −10 to −20 restores far more dimension than any recovery slider.
- **Sharpening Amount around 15.** Full sharpening on an already-sharpened file produces crunch.
- Lens correction is already applied in-camera; the Optics toggle usually does nothing.
- **Lightroom opens a ProRAW file on Apple's own "Apple ProRAW" profile.** Switching to Adobe Color or Adaptive Color frequently drops the image noticeably darker, because Apple underexposed the capture to protect highlights and its own profile compensates. Expect to add roughly +0.3 to +0.7 Exposure when you leave the Apple profile, and judge the profile choice after that, not before.
- ProRAW Max (48 MP) is the same pipeline at higher resolution — same character, more detail, larger files.

**Plain HEIC from an iPhone** is the same rendering with the white balance baked and 10 bits: everything above applies, with much less latitude.

---

## Sony (`.ARW`)

**What it is:** a true Bayer RAW. Full headroom.

**Character:**
- **A green / yellow-green cast in Adobe's rendering**, reported consistently since the a7 III / a7R III era, most visible in skin — sallow on light skin, ashy or grey on deep skin. It is a property of Adobe's calibration, not of the exposure; the same files are widely reported to render more cleanly in other converters. Whether newer bodies are better is *not established* — treat generational claims as unverified.
- A separate, sharper green shift introduced in Lightroom 10.3 was acknowledged by Adobe and fixed in 10.4. Do not confuse the two.
- Excellent dynamic range and highlight retention.
- Some compressed RAW modes carry historical artefacts; lossless compressed is the safe capture setting.

**Editing implications:**
- **Fix the green on Tint, not Temp.** Green lives on the green↔magenta axis. Set the amount by eye against a known neutral; corrections are typically small, but read the image rather than typing a number. Reaching for Temp produces a warm *and* green image, which is worse.
- If green persists only in the shadows after Tint is correct, pull the **Green channel curve's lower third down slightly** (`01-light.md`). That is a zonal cast, and white balance cannot fix a zonal cast.
- **Do not fix it with Color Mix `Green Sat −25`.** That desaturates real greens — foliage, grass — and leaves the skin cast in place.
- **Camera Matching is worth auditioning but is not a fix.** The Sony Camera Standard/Portrait profiles are themselves reported to carry the green. Offer it as an alternative rendering to try, not as a correction.

---

## Canon (`.CR2` / `.CR3`)

**What it is:** a true Bayer RAW. Full headroom.

**Character:**
- **A magenta/pink shift** in Adobe's rendering of CR3, most visible in skin and neutrals. This is community consensus rather than documented Adobe behaviour — verify it on the actual file before prescribing a correction.
- Canon's own color science is widely preferred for skin; Adobe's rendering of it is commonly described as flatter and more washed out than what the camera's own JPEG produces.
- Gentle, pleasing highlight rolloff.
- **Camera Matching profiles now exist for most CR3 bodies** (added from Lightroom Classic 11.0 onward), though coverage still lags new releases. Check the profile list rather than assuming either way.

**Editing implications:**
- **Correct the magenta on Tint**, toward green. Small numbers; Canon's magenta is milder than Sony's green. Judge against a neutral rather than typing a fixed value.
- Adobe Color often reads flat on Canon files. **Vibrance +10 to +15** and a gentle S-curve recover the character people expect from Canon, without pushing Saturation.
- Skin usually needs *less* warming than instinct suggests — the magenta already reads as warmth.

---

## Nikon (`.NEF`)

**What it is:** a true Bayer RAW. Full headroom.

**Character:** the most neutral of the major systems in Adobe's rendering. No widely reported cast. Good shadow recovery. Camera Matching profiles read Nikon's Picture Controls faithfully and are a genuinely good starting point.

**Editing implications:** treat as the reference case. If a Nikon file looks wrong, it is the exposure or the lighting, not the source. Lightroom does offer a **Camera Flexible Color** profile for the Z6III, Zf and Z50II, but it does not reproduce the in-camera recipe accurately. If a user's in-camera look does not carry over, that is why — the profile exists, the match does not.

---

## Fujifilm (`.RAF`)

**What it is:** a true RAW, but with an **X-Trans** sensor (on X-series bodies) rather than a Bayer array. GFX medium format and some entry X models use Bayer and behave normally.

**Character:**
- **Adobe's X-Trans demosaicing produces "wormy" or watercolour artefacts** in fine organic detail — foliage, grass, hair — especially at higher sharpening. This is a demosaic problem, not a color problem.
- Color rendering itself is good. No significant cast.

**Editing implications:**
- **Keep Sharpening Detail low (15–25) and Radius around 1.0.** High Detail values are what surface the worms.
- **Enhance → Raw Details** re-demosaics the file and substantially improves X-Trans rendering, but it is **desktop-only** — Lightroom Classic, Lightroom desktop, Camera Raw. It is **not available in Lightroom on iPhone or Android**, so do not prescribe it in a mobile workflow. (Denoise reached select M-series iPads in 11.5; Raw Details did not.) On mobile, control the worms with Sharpening Detail instead.
- Adobe ships film-simulation-matched profiles (Provia, Velvia, Astia, Classic Chrome, Acros, Eterna, Classic Negative). If the user shoots Fuji and wants the Fuji look, those profiles get there faster than any slider recipe.

---

## Google Pixel and Android computational DNG

**What it is:** the same category as Apple ProRAW — HDR+ multi-frame merging and tone mapping baked into a DNG.

**Character:** pre-lifted shadows and compressed highlights, as with ProRAW. Google's HDR+ pipeline is generally reported as *less* prone to the watercolour smearing seen in Apple's files, so treat detail on a Pixel DNG as better preserved than on a ProRAW until you check at 100%. Adobe's profile support is thinner than for Apple; **Adobe Color may not be offered** on some Pixel DNGs, where only Adaptive Color and Monochrome appear.

**Editing implications:** as ProRAW for shadows — do not re-lift them — with contrast built in the curve and minimal sharpening. If Adobe Color is unavailable, use **Adaptive Color** and say why.

---

## Smartphone JPEG and HEIC (non-RAW)

**What it is:** fully rendered. White balance, tone curve, color, sharpening and noise reduction are permanent.

**Character:** 8-bit JPEG bands visibly when pushed; 10-bit HEIC tolerates more. Temp/Tint become relative ±100 nudges rather than true Kelvin. Only Color and Monochrome profiles exist.

**Editing implications:**
- **Halve every number** you would use on a RAW.
- Watch for banding in skies and smooth gradients after any tonal move. **Grain 10–15** hides banding effectively.
- Clipped highlights are unrecoverable. Do not prescribe Highlights −60 on a JPEG; there is nothing there to recover.

---

## Other sources

| Source | Character | Editing note |
|---|---|---|
| **Panasonic / Lumix** | Neutral, no reported cast | Treat as the reference case |
| **OM System / Olympus** | Neutral; smaller sensor, so noise arrives earlier | Detail settings matter more |
| **Leica** | Neutral, gentle rolloff | Reference case |
| **Sigma / Foveon** | Unusual color response, limited Adobe support | Verify what profiles exist before prescribing |
| **DJI drones** | Arrives flat and washed out; thin profile support | Expect to build contrast from scratch; skip AI Denoise |
| **GoPro** | Neutral; heavy wide-angle distortion | Lens correction matters more than usual |
| **Scanned film** | Whatever the scanner did | Treat as a JPEG with a cast; correct on Tint first |

---

## Diagnosing an unknown source

When the camera is unlisted, unrecognised, or the user does not know, work the method.

**1. Is it a true RAW or a computational RAW?**

Computational RAW gives itself away: shadows that are already open with no noise in them, halos at high-contrast edges, and smeared watercolour texture in foliage at 100%. A true RAW at base ISO shows real shadow noise and no halos. Phone-sized files that look impossibly clean in the shadows are computational.

**2. Find the cast on a neutral.**

Locate something that should be neutral — concrete, white paint, grey fabric. Which way is it off?

| Neutral looks | Cast is | Correct with |
|---|---|---|
| Green / sallow / ashy | Green | Tint **+** (toward magenta) |
| Pink / magenta | Magenta | Tint **−** (toward green) |
| Blue / cold | Cool | Temp **+** |
| Orange / yellow | Warm | Temp **−** |

**3. Is the cast global or zonal?**

Check a neutral in the highlights and a neutral in the shadows. Both off the same way is a **global** cast → white balance. Off differently is a **zonal** cast → RGB channel curves (`01-light.md`). White balance cannot fix a zonal cast, and trying is why some images never look right.

**4. Test the headroom before committing.**

Push Highlights to −100 briefly. If detail returns, the file has real headroom. If the area stays flat white, it is clipped and gone — plan the edit around that rather than fighting it. Reset and build the actual recipe.

**5. Check the noise floor and existing sharpening at 100%.**

Already-sharpened files show halos on edges. Already-denoised files show waxy, detail-free texture. Both mean: minimal sharpening, no noise reduction.

The method is source-agnostic: it reads the file rather than looking up the camera.
