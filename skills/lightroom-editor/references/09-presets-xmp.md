# Presets and XMP

How to write a Lightroom preset as a real `.xmp` file, and how to get it onto a phone.

## The portability rule

**A preset omits Exposure, Temp and Tint.** Those three are per-photo: they depend on the metering and the light of one frame. A preset carrying them wrecks every image it touches except the one it was built on.

Omit an attribute entirely and Lightroom leaves that setting alone. Include it with a value and Lightroom overwrites. Only write the attributes the look actually needs.

## File structure

A preset is XMP-RDF. Attributes live in the `crs:` namespace on a single `rdf:Description`, with curves and the profile as child elements.

Positive values are written with an explicit `+`. Value `0` is written bare.

## Working template

A **skeleton**, not a look. Every slider below is either structural or a
Lightroom default. Add only the attributes your look actually moves, and
delete the rest — an attribute you leave in overwrites the user's setting
with this file's value, which is how a preset ends up applying a grade
nobody asked for.

**The template must never ship with example slider values.** If you want to
see a filled-in look, read the worked example after the attribute map.

```xml
<x:xmpmeta xmlns:x="adobe:ns:meta/" x:xmptk="Adobe XMP Core 7.0-c000 1.000000, 0000/00/00-00:00:00        ">
 <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
  <rdf:Description rdf:about=""
    xmlns:crs="http://ns.adobe.com/camera-raw-settings/1.0/"
   crs:PresetType="Normal"
   crs:Cluster=""
   crs:UUID="REPLACE_WITH_32_HEX_UPPERCASE"
   crs:SupportsAmount2="True"
   crs:SupportsAmount="True"
   crs:SupportsColor="True"
   crs:SupportsMonochrome="True"
   crs:SupportsHighDynamicRange="True"
   crs:SupportsNormalDynamicRange="True"
   crs:SupportsSceneReferred="True"
   crs:SupportsOutputReferred="True"
   crs:RequiresRGBTables="False"
   crs:CameraModelRestriction=""
   crs:Copyright=""
   crs:ContactInfo=""
   crs:Version="15.3"
   crs:ProcessVersion="11.0"
   crs:ToneCurveName2012="Custom"
   crs:HasSettings="True">
   <crs:Name>
    <rdf:Alt>
     <rdf:li xml:lang="x-default">PRESET NAME</rdf:li>
    </rdf:Alt>
   </crs:Name>
   <crs:ShortName>
    <rdf:Alt>
     <rdf:li xml:lang="x-default"/>
    </rdf:Alt>
   </crs:ShortName>
   <crs:SortName>
    <rdf:Alt>
     <rdf:li xml:lang="x-default"/>
    </rdf:Alt>
   </crs:SortName>
   <crs:Group>
    <rdf:Alt>
     <rdf:li xml:lang="x-default">GROUP NAME</rdf:li>
    </rdf:Alt>
   </crs:Group>
   <crs:Description>
    <rdf:Alt>
     <rdf:li xml:lang="x-default"/>
    </rdf:Alt>
   </crs:Description>
   <crs:Look>
    <rdf:Description
     crs:Name="Adobe Color"
     crs:Amount="1"
     crs:UUID="B952C231111CD8E0ECCF14B86BAA7077"
     crs:SupportsAmount="false"
     crs:SupportsMonochrome="false"
     crs:SupportsOutputReferred="false"
     crs:Copyright="© 2018 Adobe Systems, Inc."
     crs:Stubbed="true">
    <crs:Group>
     <rdf:Alt>
      <rdf:li xml:lang="x-default">Profiles</rdf:li>
     </rdf:Alt>
    </crs:Group>
    </rdf:Description>
   </crs:Look>
  </rdf:Description>
 </rdf:RDF>
</x:xmpmeta>
```

The gap between `crs:ProcessVersion` and `crs:ToneCurveName2012` is where the
look goes. Nothing else belongs there. Drop `crs:ToneCurveName2012` too if the
preset carries no tone curve.

## The tone curve rule

**If the file contains any `ToneCurvePV2012*` element, it must also carry
`crs:ToneCurveName2012="Custom"`.**

Without it Lightroom imports the preset with no error, reports success, and
**silently discards every curve** — the composite curve and all three channel
curves. Nothing in the UI indicates this happened.

This matters more than it sounds. The Blue channel curve is where warm
highlights live: pulling its top point down to `255,246` is what makes
highlights read yellow rather than orange. Drop it and a warm look loses its
yellow, leaving the Color Grading split-tone as the only warmth source — which
lands orange, or red once any magenta Tint is present. "I asked for golden and
got orange" is this bug.

Generate `crs:UUID` fresh per preset — 32 uppercase hex characters. Reusing one
makes Lightroom treat two presets as the same preset.

`crs:Version` records which Lightroom version authored the preset. It is
cosmetic, not a compatibility gate — an older value imports fine, so leave it or
omit it rather than chasing the current release. `crs:ProcessVersion="11.0"` is
the meaningful one and is current.

## Attribute map

| Control | Attribute | Notes |
|---|---|---|
| Exposure | `Exposure2012` | **Omit for portability** |
| Temp / Tint (absolute) | `Temperature` / `Tint` | **Omit for portability.** Absolute Kelvin; wrecks every photo but the one it was built on |
| Temp / Tint (relative) | `IncrementalTemperature` / `IncrementalTint` | The portable pair — a *shift*, not a value. Still per-photo in character; use only when the look genuinely needs a nudge, and keep it small |
| HDR edit mode | `HDREditMode` | `0` = SDR, `1` = HDR. Relevant to ProRAW in current Lightroom; omit to leave the user's mode alone |
| Contrast | `Contrast2012` | |
| Highlights | `Highlights2012` | |
| Shadows | `Shadows2012` | |
| Whites | `Whites2012` | |
| Blacks | `Blacks2012` | |
| Texture | `Texture` | |
| Clarity | `Clarity2012` | |
| Dehaze | `Dehaze` | |
| Vibrance / Saturation | `Vibrance` / `Saturation` | |
| Color Mix Hue | `HueAdjustment<Band>` | Red Orange Yellow Green Aqua Blue Purple Magenta |
| Color Mix Sat | `SaturationAdjustment<Band>` | |
| Color Mix Lum | `LuminanceAdjustment<Band>` | |
| Color Grading — Shadows Hue/Sat | `SplitToningShadowHue` / `SplitToningShadowSaturation` | **Legacy names, still current** |
| Color Grading — Highlights Hue/Sat | `SplitToningHighlightHue` / `SplitToningHighlightSaturation` | **Legacy names, still current** |
| Color Grading — Midtones Hue/Sat | `ColorGradeMidtoneHue` / `ColorGradeMidtoneSat` | |
| Color Grading — Global Hue/Sat | `ColorGradeGlobalHue` / `ColorGradeGlobalSat` | |
| Color Grading — all four Luminance | `ColorGrade{Shadow,Midtone,Highlight,Global}Lum` | |
| Blending | `ColorGradeBlending` | Default 50 |
| Balance | `SplitToningBalance` | |
| Tone curve | `ToneCurvePV2012` + `Red`/`Green`/`Blue` | Child elements, `in, out` on 0–255 |
| Curve mode | `ToneCurveName2012="Custom"` | Set when a custom curve is present |
| Sharpening | `Sharpness`, `SharpenRadius`, `SharpenDetail`, `SharpenEdgeMasking` | |
| Luminance NR | `LuminanceSmoothing` + `LuminanceNoiseReductionDetail` / `Contrast` | |
| Color NR | `ColorNoiseReduction` + `Detail` / `Smoothness` | |
| Lens correction | `LensProfileEnable="1"`, `LensProfileSetup="LensDefaults"` | |
| Remove CA | `AutoLateralCA="1"` | |
| Defringe | `Defringe{Purple,Green}Amount` + `HueLo`/`HueHi` | |
| Vignette | `PostCropVignetteAmount`, `Midpoint`, `Roundness`, `Feather`, `HighlightContrast` | `Style="1"` = Highlight Priority |
| Grain | `GrainAmount`, `GrainSize`, `GrainFrequency` | `GrainFrequency` is the **Roughness** slider |
| Profile | `<crs:Look>` child element | Adobe Color as shown above |

Three traps in this table, all verified against real preset files:

- **Color Grading is split across two prefixes.** Shadows and Highlights keep the legacy `SplitToning*` names for Hue and Saturation; only Midtones and Global use `ColorGrade*`. Luminance uses `ColorGrade*Lum` for all four. `ColorGradeShadowHue` and `ColorGradeHighlightHue` do not exist — writing them produces a preset that silently drops the grade.
- **`GrainFrequency` is the Roughness slider.**
- **`SplitToningBalance` is the Color Grading Balance slider.**

## Which way is positive

A sign error here is invisible in the file and obvious in the photo. Never
write one of these from memory.

| Attribute | Negative | Positive |
|---|---|---|
| `IncrementalTemperature` | cooler / blue | warmer / yellow |
| `IncrementalTint` | toward green | **toward magenta** |
| `HueAdjustmentRed` | toward magenta | toward orange |
| `HueAdjustmentOrange` | toward red | toward yellow |
| `HueAdjustmentYellow` | **toward orange** | toward green |
| `HueAdjustmentGreen` | toward yellow | toward aqua |
| `HueAdjustmentAqua` | toward green | toward blue |
| `HueAdjustmentBlue` | toward aqua | toward purple |
| `HueAdjustmentPurple` | toward blue | toward magenta |
| `HueAdjustmentMagenta` | toward purple | toward red |
| `SplitToningBalance` | favours the **shadow** hue | favours the **highlight** hue |
| `PostCropVignetteAmount` | darkens corners | lightens corners |
| `PostCropVignetteRoundness` | more rectangular | more circular |

Colour Grading hue values are absolute degrees on the wheel, not offsets:
`0` red, `30` orange, `45` amber, `60` yellow, `120` green, `240` blue, `300` magenta.

**The yellow row is the one that bites.** A warm look built by dragging
`HueAdjustmentYellow` negative does not get more golden — it rotates the
image's yellows into orange, and then into red once a positive
`IncrementalTint` is added on top. Golden-hour references sit around
**35–48°**; keep the image's own yellows there rather than pulling them down.

## Worked example — a warm golden look

Filled in from the skeleton. Note that every move targets the bands the
reference actually contains, and the Blue curve carries the yellow.

```xml
   crs:Contrast2012="+8"
   crs:Highlights2012="-20"
   crs:Shadows2012="+15"
   crs:Blacks2012="+10"
   crs:HueAdjustmentOrange="+4"
   crs:SaturationAdjustmentOrange="+10"
   crs:LuminanceAdjustmentOrange="+6"
   crs:SaturationAdjustmentYellow="+8"
   crs:SplitToningHighlightHue="45"
   crs:SplitToningHighlightSaturation="10"
   crs:SplitToningShadowHue="220"
   crs:SplitToningShadowSaturation="5"
   crs:ColorGradeBlending="50"
   crs:ToneCurveName2012="Custom"
```
```xml
   <crs:ToneCurvePV2012>
    <rdf:Seq><rdf:li>0, 12</rdf:li><rdf:li>128, 128</rdf:li><rdf:li>255, 248</rdf:li></rdf:Seq>
   </crs:ToneCurvePV2012>
   <crs:ToneCurvePV2012Blue>
    <rdf:Seq><rdf:li>0, 8</rdf:li><rdf:li>255, 244</rdf:li></rdf:Seq>
   </crs:ToneCurvePV2012Blue>
```

The Blue curve's top pulled to `255,244` is what makes the highlights read
yellow. Delete that one line and the same preset lands orange.

## Other profiles

Swap `crs:Name` inside `<crs:Look>`. Each Adobe profile has its own UUID; if you do not have the correct one, omit `crs:UUID` and `crs:Stubbed` and keep `crs:Name`. Lightroom then resolves the profile by name — this is how community preset generators emit non-default profiles, though Adobe does not document the fallback explicitly.

```xml
<crs:Look>
 <rdf:Description crs:Name="Adobe Monochrome" crs:Amount="1">
  <crs:Group><rdf:Alt><rdf:li xml:lang="x-default">Profiles</rdf:li></rdf:Alt></crs:Group>
 </rdf:Description>
</crs:Look>
```

Omit the `<crs:Look>` block entirely to leave the user's current profile untouched.

## Black and white presets

Set `crs:ConvertToGrayscale="True"`, use the `Adobe Monochrome` profile, and write the B&W mix with `crs:GrayMixer<Band>` attributes (`GrayMixerRed`, `GrayMixerOrange`, and so on), each −100…+100.

## Getting a preset onto mobile

1. Save the file with a `.xmp` extension.
2. Get it onto the phone — AirDrop, email, Google Drive, or Files.
3. **If it arrived as a `.zip`, extract it first.** Older Lightroom mobile versions cannot read a zip; recent versions reportedly can. Extracting always works, so extract rather than testing the version.
4. In Lightroom, open any photo → **Edit** → **Presets** → **Yours** → **⋯** → **Import Presets**.
5. Navigate to the file and select it. It appears under **User Presets**.

If `.xmp` import is unavailable on the user's version, the **DNG carrier** path always works:

1. Apply the settings to a DNG in Lightroom desktop.
2. Export as DNG and move it to the phone.
3. Import it into Lightroom mobile, open it, and **Create Preset** from its settings.

Presets created or imported on one device sync through Creative Cloud to the others.

## Handing a preset to the user

Write the `.xmp` to a file and send it, rather than pasting XML into chat — the user needs a file to import, not text to copy.

Name the file exactly as `crs:Name`. Set `crs:Group` to something meaningful so it lands in its own folder rather than loose among Adobe's.

## Common mistakes

| Mistake | Fix |
|---|---|
| Preset includes Exposure or Temp | Omit them. They are per-photo. |
| Same UUID on several presets | Generate a fresh 32-hex UUID each time. |
| Writing `GrainRoughness` | The attribute is `GrainFrequency`. |
| Writing `ColorGradeBalance` | The attribute is `SplitToningBalance`. |
| Writing `ColorGradeShadowHue` / `ColorGradeHighlightHue` | They do not exist. Use `SplitToningShadowHue` / `SplitToningHighlightHue`. The grade silently vanishes otherwise. |
| Custom curve ignored | Set `ToneCurveName2012="Custom"`. |
| Every attribute written with a 0 default | Only write what the look uses; zeros overwrite the user's settings. |
| Pasting XML into chat | Write a file and send it. |
| Custom curve with no `ToneCurveName2012` | Set it to `"Custom"`. Otherwise every curve is silently discarded. |
| Draining a band the reference does not contain | Read the reference's actual hue content first. `Green Sat −40` on a reference with no green only strips green from the *user's* photo. |
| Warm look built with `HueAdjustmentYellow` negative | That rotates yellow toward orange. Build warmth on Orange sat/lum and the Blue curve. |
| Shipping without running the checks | Run `scripts/preset-check.py` and `scripts/look-match.py` before handing the file over. |

## Before you ship it

Two checks live in the repo. Run both; neither needs Lightroom.

```
scripts/preset-check.py PRESET.xmp              # structure, vocabulary, ranges, curve mode
scripts/look-match.py REFERENCE.jpg PRESET.xmp  # does it grade the bands the reference has?
```

`preset-check.py` catches the silent-failure class — unknown attribute names,
out-of-range values, non-monotonic curves, reused UUIDs, and a custom curve
with no `ToneCurveName2012`. `look-match.py` catches the look-is-wrong class:
hard moves on bands the reference does not contain, and a dominant reference
band the preset never touches.
