# Presets and XMP

How to write a Lightroom preset as a real `.xmp` file, and how to get it onto a phone.

## The portability rule

**A preset omits Exposure, Temp and Tint.** Those three are per-photo: they depend on the metering and the light of one frame. A preset carrying them wrecks every image it touches except the one it was built on.

Omit an attribute entirely and Lightroom leaves that setting alone. Include it with a value and Lightroom overwrites. Only write the attributes the look actually needs.

## File structure

A preset is XMP-RDF. Attributes live in the `crs:` namespace on a single `rdf:Description`, with curves and the profile as child elements.

Positive values are written with an explicit `+`. Value `0` is written bare.

## Working template

Adobe Color profile, portable, ready to fill in. This is a complete valid file.

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
   crs:Contrast2012="+12"
   crs:Highlights2012="-25"
   crs:Shadows2012="+18"
   crs:Whites2012="+15"
   crs:Blacks2012="-10"
   crs:Texture="+10"
   crs:Clarity2012="+5"
   crs:Dehaze="0"
   crs:Vibrance="+12"
   crs:Saturation="0"
   crs:HueAdjustmentRed="0"
   crs:HueAdjustmentOrange="0"
   crs:HueAdjustmentYellow="0"
   crs:HueAdjustmentGreen="+15"
   crs:HueAdjustmentAqua="0"
   crs:HueAdjustmentBlue="0"
   crs:HueAdjustmentPurple="0"
   crs:HueAdjustmentMagenta="0"
   crs:SaturationAdjustmentRed="0"
   crs:SaturationAdjustmentOrange="-6"
   crs:SaturationAdjustmentYellow="0"
   crs:SaturationAdjustmentGreen="-12"
   crs:SaturationAdjustmentAqua="0"
   crs:SaturationAdjustmentBlue="0"
   crs:SaturationAdjustmentPurple="0"
   crs:SaturationAdjustmentMagenta="0"
   crs:LuminanceAdjustmentRed="0"
   crs:LuminanceAdjustmentOrange="+8"
   crs:LuminanceAdjustmentYellow="0"
   crs:LuminanceAdjustmentGreen="0"
   crs:LuminanceAdjustmentAqua="0"
   crs:LuminanceAdjustmentBlue="-10"
   crs:LuminanceAdjustmentPurple="0"
   crs:LuminanceAdjustmentMagenta="0"
   crs:SplitToningShadowHue="30"
   crs:SplitToningShadowSaturation="6"
   crs:SplitToningHighlightHue="45"
   crs:SplitToningHighlightSaturation="10"
   crs:SplitToningBalance="0"
   crs:ColorGradeMidtoneHue="0"
   crs:ColorGradeMidtoneSat="0"
   crs:ColorGradeShadowLum="0"
   crs:ColorGradeMidtoneLum="0"
   crs:ColorGradeHighlightLum="0"
   crs:ColorGradeGlobalHue="0"
   crs:ColorGradeGlobalSat="0"
   crs:ColorGradeGlobalLum="0"
   crs:ColorGradeBlending="50"
   crs:Sharpness="40"
   crs:SharpenRadius="+1.0"
   crs:SharpenDetail="25"
   crs:SharpenEdgeMasking="0"
   crs:LuminanceSmoothing="0"
   crs:LuminanceNoiseReductionDetail="50"
   crs:LuminanceNoiseReductionContrast="0"
   crs:ColorNoiseReduction="25"
   crs:ColorNoiseReductionDetail="50"
   crs:ColorNoiseReductionSmoothness="50"
   crs:LensProfileEnable="1"
   crs:LensProfileSetup="LensDefaults"
   crs:AutoLateralCA="1"
   crs:DefringePurpleAmount="0"
   crs:DefringePurpleHueLo="30"
   crs:DefringePurpleHueHi="70"
   crs:DefringeGreenAmount="0"
   crs:DefringeGreenHueLo="40"
   crs:DefringeGreenHueHi="60"
   crs:PostCropVignetteAmount="-12"
   crs:PostCropVignetteMidpoint="40"
   crs:PostCropVignetteRoundness="0"
   crs:PostCropVignetteFeather="70"
   crs:PostCropVignetteHighlightContrast="0"
   crs:PostCropVignetteStyle="1"
   crs:GrainAmount="14"
   crs:GrainSize="24"
   crs:GrainFrequency="50"
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
   <crs:ToneCurvePV2012>
    <rdf:Seq>
     <rdf:li>0, 0</rdf:li>
     <rdf:li>64, 60</rdf:li>
     <rdf:li>128, 128</rdf:li>
     <rdf:li>192, 196</rdf:li>
     <rdf:li>255, 250</rdf:li>
    </rdf:Seq>
   </crs:ToneCurvePV2012>
   <crs:ToneCurvePV2012Red>
    <rdf:Seq>
     <rdf:li>0, 0</rdf:li>
     <rdf:li>255, 255</rdf:li>
    </rdf:Seq>
   </crs:ToneCurvePV2012Red>
   <crs:ToneCurvePV2012Green>
    <rdf:Seq>
     <rdf:li>0, 0</rdf:li>
     <rdf:li>255, 255</rdf:li>
    </rdf:Seq>
   </crs:ToneCurvePV2012Green>
   <crs:ToneCurvePV2012Blue>
    <rdf:Seq>
     <rdf:li>0, 10</rdf:li>
     <rdf:li>255, 246</rdf:li>
    </rdf:Seq>
   </crs:ToneCurvePV2012Blue>
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

Generate `crs:UUID` fresh per preset — 32 uppercase hex characters. Reusing one makes Lightroom treat two presets as the same preset.

`crs:Version` records which Lightroom version authored the preset. It is cosmetic, not a compatibility gate — an older value imports fine, so leave it or omit it rather than chasing the current release. `crs:ProcessVersion="11.0"` is the meaningful one and is current.

## Attribute map

| Control | Attribute | Notes |
|---|---|---|
| Exposure | `Exposure2012` | **Omit for portability** |
| Temp / Tint | `Temperature` / `Tint` | **Omit for portability** |
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
