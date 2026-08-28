# Sources

Every file arrives with its origin's character already baked in. Name it before you edit, or you spend the whole edit fighting an error you never identified.

Two things to establish: **what the file actually is**, and **how much headroom it has left**.

## Headroom

How much latitude remains for recovery. It decides how hard you are allowed to push.

| File | Headroom | Practical limit |
|---|---|---|
| True Bayer RAW (Sony, Canon, Nikon, Fuji, Panasonic, Leica) | High | ~1 stop highlight recovery, Shadows to +40 |
| Computational RAW (Apple ProRAW, Pixel DNG) | Low–medium | Shadows to +30 max; highlights largely already spent |
| HEIC (10-bit) | Low | Small moves; some banding resistance |
| JPEG (8-bit) | Very low | Clipped is gone; bands visibly past ±30 on tone sliders |

**The headroom rule:** a computational RAW looks like a RAW and edits like a JPEG that happens to be 12-bit. Treat it accordingly.

---

## Apple ProRAW (iPhone, `.DNG`)

**What it is:** not a virgin Bayer file. ProRAW is a *linear* DNG that has already been demosaiced, multi-frame merged (Deep Fusion, Smart HDR, Night mode), locally tone-mapped, sharpened, and noise-reduced. Apple's entire computational pipeline ran before the file was written. You are editing Apple's rendering, in a container that gives you raw-like white balance and 12-bit depth.

**Character:**
- **Shadows are already lifted and highlights already compressed.** The local tone mapping spent most of the dynamic range for you.
- **Halos around high-contrast edges** — a rim-lit head against sky, a horizon, a backlit branch. Baked in by the local tone mapping; not removable, and Clarity/Dehaze make them worse.
- **Watercolour texture** in foliage, fabric and fine detail, from aggressive noise reduction plus sharpening.
- **Warm, slightly yellow skin rendering**, and skies pushed toward cyan.
- **Semantic per-region processing** — faces and skies are processed differently from the rest of the frame, so a global move can land unevenly.

**Editing implications:**
- **Shadows above +30 is the mistake.** This is the single biggest cause of the flat, grey, "phone HDR" look. The phone already lifted them; lifting again removes the last dimension and exposes the noise floor.
- Add contrast in the **tone curve**, not in Shadows/Highlights. Deepening blacks with Blacks −10 to −20 restores far more dimension than any recovery slider.
- **Sharpening Amount around 15.** Full sharpening on an already-sharpened file produces crunch.
- Lens correction is already applied in-camera; the Optics toggle usually does nothing.
- **Adobe Adaptive** is often a better profile than Adobe Color here, because a fixed profile fights the baked-in tone mapping. Adobe Color remains the safe default.
- ProRAW Max (48 MP) is the same pipeline at higher resolution — same character, more detail, larger files.

**Plain HEIC from an iPhone** is the same rendering with the white balance baked and 10 bits: everything above applies, with much less latitude.

---

## Sony (`.ARW`)

**What it is:** a true Bayer RAW. Full headroom.

**Character:**
- **A green cast in Adobe's rendering**, widely reported, strongest in shadows and midtones and most visible in skin, where it reads as sallow on light skin and ashy or grey on deep skin. It is a property of how Adobe renders Sony's color, not of the exposure. Newer bodies (a7 IV, a1, a7R V era) are noticeably better than older ones, and it persists to some degree.
- Excellent dynamic range and highlight retention.
- Some compressed RAW modes carry historical artefacts; lossless compressed is the safe capture setting.

**Editing implications:**
- **Fix the green on Tint, not Temp.** Green lives on the green↔magenta axis. Typical correction: **Tint +5 to +12** toward magenta. Reaching for Temp produces a warm *and* green image, which is worse.
- If green persists only in the shadows after Tint is correct, pull the **Green channel curve's lower third down slightly** (`01-light.md`). That is a zonal cast, and white balance cannot fix a zonal cast.
- **Do not fix it with Color Mix `Green Sat −25`.** That desaturates real greens — foliage, grass — and leaves the skin cast in place.
- **Camera Matching** profiles help some bodies noticeably. Offer it as an alternative rendering, while noting it replaces Adobe's opinion with Sony's rather than fixing anything.

---

## Canon (`.CR2` / `.CR3`)

**What it is:** a true Bayer RAW. Full headroom.

**Character:**
- **A magenta/pink shift** in Adobe's rendering of CR3, most visible in skin and neutrals.
- Canon's own color science is widely preferred for skin; Adobe's rendering of it is commonly described as flatter and more washed out than what the camera's own JPEG produces.
- Gentle, pleasing highlight rolloff.
- **Camera Matching profiles are sparse for CR3 bodies.** Do not assume they exist for the user's camera.

**Editing implications:**
- **Correct the magenta on Tint: −3 to −8** toward green. Small numbers; Canon's magenta is milder than Sony's green.
- Adobe Color often reads flat on Canon files. **Vibrance +10 to +15** and a gentle S-curve recover the character people expect from Canon, without pushing Saturation.
- Skin usually needs *less* warming than instinct suggests — the magenta already reads as warmth.

---

## Nikon (`.NEF`)

**What it is:** a true Bayer RAW. Full headroom.

**Character:** the most neutral of the major systems in Adobe's rendering. No widely reported cast. Good shadow recovery. Camera Matching profiles read Nikon's Picture Controls faithfully and are a genuinely good starting point.

**Editing implications:** treat as the reference case. If a Nikon file looks wrong, it is the exposure or the lighting, not the source. Note that the newest Z-body "Flexible Color" profiles are not supported in Lightroom — if a user's in-camera look does not carry over, that is why.

---

## Fujifilm (`.RAF`)

**What it is:** a true RAW, but with an **X-Trans** sensor (on X-series bodies) rather than a Bayer array. GFX medium format and some entry X models use Bayer and behave normally.

**Character:**
- **Adobe's X-Trans demosaicing produces "wormy" or watercolour artefacts** in fine organic detail — foliage, grass, hair — especially at higher sharpening. This is a demosaic problem, not a color problem.
- Color rendering itself is good. No significant cast.

**Editing implications:**
- **Keep Sharpening Detail low (15–25) and Radius around 1.0.** High Detail values are what surface the worms.
- **Enhance Details** (where available) re-demosaics the file and substantially improves X-Trans rendering. Worth recommending for landscape and foliage.
- Adobe ships film-simulation-matched profiles (Provia, Velvia, Astia, Classic Chrome, Acros, Eterna, Classic Negative). If the user shoots Fuji and wants the Fuji look, those profiles get there faster than any slider recipe.

---

## Google Pixel and Android computational DNG

**What it is:** the same category as Apple ProRAW — HDR+ multi-frame merging and tone mapping baked into a DNG.

**Character:** pre-lifted shadows, compressed highlights, aggressive noise reduction and sharpening, and Google's characteristic contrastier, cooler rendering. Adobe's profile support is thinner than for Apple; **Adobe Color may not be offered** on some Pixel DNGs, where only Adaptive Color and Monochrome appear.

**Editing implications:** identical to ProRAW. Shadows capped around +30, contrast in the curve, minimal sharpening. If Adobe Color is unavailable, use **Adaptive Color** and say why.

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

That method covers every source, including ones that do not exist yet.
