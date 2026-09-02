#!/usr/bin/env python3
"""Which pixels are a face? The one question colour alone cannot answer.

`lookstats.skin()` says so itself: it withholds by default because nothing in
that module can tell a face from a sand dune, and it notes the measurement "is
correct once something else has established which pixels are skin, which is a
face detector's job and not this module's". This is that something else.

It runs MediaPipe's Selfie Multiclass segmenter -- a 16 MB tflite file --
directly on `ai-edge-litert`, and hands `skin()` only the pixels the model
calls facial skin.

WHY THIS MODEL, AND WHY NOT VIA MEDIAPIPE. The `mediapipe` package pulls in
opencv-contrib and matplotlib: 273 MB installed, against 56 MB for this
project's whole existing stack. The weights are a plain `.tflite`, so running
them on `ai-edge-litert` (10.8 MB wheel) costs about 47 MB instead. Same model,
same numbers, a fifth of the footprint.

WHAT THE MODEL ACTUALLY EMITS. Logits, not probabilities -- the six channels
sum to about -2.4, not 1. The "per-pixel confidence" this module gates on is
the softmax computed here, in `_probabilities`. Anything that reports a
confidence straight off this model's output without softmaxing it is reporting
a number with no probabilistic meaning at all.

OPTIONAL, ALWAYS. Neither the runtime nor the weights ship with the skill.
Absent either, every entry point returns a refusal that names what is missing
and how to get it, and `skin()` goes on withholding exactly as it does today.
Nothing here is on the path of any measurement that worked before it existed.

Install:
    pip install ai-edge-litert
    curl -sLo skills/lightroom-editor/scripts/models/selfie_multiclass_256x256.tflite \\
      https://storage.googleapis.com/mediapipe-models/image_segmenter/selfie_multiclass_256x256/float32/latest/selfie_multiclass_256x256.tflite

Usage:
  scripts/segment.py PHOTO.jpg
"""
import os
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lookstats as ls

HERE = Path(__file__).resolve().parent
MODEL = Path(os.environ.get(
    "LIGHTROOM_SEGMENT_MODEL", HERE / "models" / "selfie_multiclass_256x256.tflite"))
MODEL_URL = ("https://storage.googleapis.com/mediapipe-models/image_segmenter/"
             "selfie_multiclass_256x256/float32/latest/selfie_multiclass_256x256.tflite")

# The model's six output channels, in index order.
BACKGROUND, HAIR, BODY_SKIN, FACE_SKIN, CLOTHES, OTHER = range(6)
CATEGORIES = ["background", "hair", "body-skin", "face-skin", "clothes", "other"]

SIZE = 256          # the model's fixed input, 1x256x256x3 float32

# MEASURED against 49 Pexels photographs, 29 containing a face and 20 not.
# Mean softmax confidence over the pixels argmaxed to face-skin separated the
# two groups cleanly: every real face scored 0.72 or better, every frame
# without one scored 0.65 or worse. 0.70 sits in that gap.
#
# The gap is 0.07 wide on a sample of 49, which is thin -- treat it the way
# look-match.py treats DOMINANT's 0.9-point margin. A frame that lands between
# 0.65 and 0.72 is genuinely ambiguous and is refused, which is the right
# answer for a number this skill would otherwise print as a fact about a
# person's skin.
MIN_CONFIDENCE = 0.70

# Below this share of the frame there are too few face pixels for their mean
# to be stable. The smallest true face in the measured set was 1.3% of frame;
# the largest false positive was 2.1% but scored only 0.53 confidence, so
# share alone does not separate the groups and is deliberately loose here.
# MIN_CONFIDENCE does the discriminating.
MIN_FACE_SHARE = 0.005


def available():
    """(ready, reason). Never raises: absence is a normal state, not an error."""
    try:
        import ai_edge_litert  # noqa: F401
    except ImportError:
        return False, ("ai-edge-litert is not installed, so no face can be "
                       "located — install it with `pip install ai-edge-litert`")
    if not MODEL.exists():
        return False, (f"the segmentation model is not at {MODEL} — fetch it "
                       f"with `curl -sLo {MODEL} {MODEL_URL}`")
    return True, ""


def _probabilities(rgb2d):
    """Per-pixel class probabilities at 256x256, softmaxed from the logits.

    The model is fed a bilinear-resized copy. That is safe here and would not
    be safe in lookstats: resampling averages neighbouring pixels and invents
    colours the file never had, which is why load_source subsamples instead of
    resizing. But nothing is MEASURED off this copy -- it only decides which
    pixels are a face. Every colour figure is then taken from the full-size
    original through the upsampled mask.
    """
    from ai_edge_litert.interpreter import Interpreter
    from PIL import Image

    interp = Interpreter(model_path=str(MODEL))
    interp.allocate_tensors()
    inp = interp.get_input_details()[0]
    out = interp.get_output_details()[0]

    small = Image.fromarray((np.clip(rgb2d, 0, 1) * 255).astype(np.uint8))
    small = small.resize((SIZE, SIZE), Image.BILINEAR)
    x = (np.asarray(small, dtype=np.float32) / 255.0)[None]

    interp.set_tensor(inp["index"], x)
    interp.invoke()
    z = interp.get_tensor(out["index"])[0]

    # The model emits logits. Softmax here or the "confidence" below is not a
    # probability and the threshold on it means nothing.
    e = np.exp(z - z.max(-1, keepdims=True))
    return e / e.sum(-1, keepdims=True)


def face_mask(rgb2d):
    """(mask over the full-size image, mean confidence, share of frame).

    The mask is upsampled NEAREST. Interpolating it would produce fractional
    membership at the face's edge, and a pixel is either being measured as
    skin or it is not.
    """
    from PIL import Image

    p = _probabilities(rgb2d)
    small = p.argmax(-1) == FACE_SKIN
    if not small.any():
        return np.zeros(rgb2d.shape[:2], dtype=bool), 0.0, 0.0
    confidence = float(p[..., FACE_SKIN][small].mean())
    h, w = rgb2d.shape[:2]
    big = Image.fromarray((small * 255).astype(np.uint8)).resize((w, h), Image.NEAREST)
    mask = np.asarray(big) > 127
    return mask, confidence, float(mask.mean())


def skin(path):
    """Skin tone measured on the segmented face, or a refusal naming the reason.

    Returns the shape `lookstats.skin()` returns, plus `confidence` and
    `face_share`, so a caller can treat the two interchangeably.

    The refusal cases, each one a real state rather than an error:
      runtime or weights missing   nothing can be located; fall back to
                                   lookstats.skin(), which withholds
      no face found                the frame has none, or too little of one
      confidence below the floor   something face-shaped, not confidently a face

    `allow_unreliable=True` on the inner call is not a shortcut. That flag
    means "the caller has established which pixels are skin" -- which, once
    the mask exists, is exactly true, and is the precondition lookstats names
    for its own measurement being correct.
    """
    ready, why = available()
    if not ready:
        return {"ok": False, "reason": why, "confidence": None, "face_share": None}

    rgb2d, provenance = ls.load_image_2d(path)
    mask, confidence, share = face_mask(rgb2d)

    if share < MIN_FACE_SHARE:
        return {"ok": False, "confidence": confidence, "face_share": share,
                "provenance": provenance,
                "reason": (f"no face found — {share * 100:.1f}% of the frame "
                           f"segments as facial skin, below the {MIN_FACE_SHARE * 100:.1f}% "
                           "floor. A warm frame with no face in it is where a "
                           "skin tone gets invented, so none is reported")}

    if confidence < MIN_CONFIDENCE:
        return {"ok": False, "confidence": confidence, "face_share": share,
                "provenance": provenance,
                "reason": (f"face uncertain — the segmenter averaged {confidence:.2f} "
                           f"over the pixels it called facial skin, below the "
                           f"{MIN_CONFIDENCE:.2f} floor measured to separate real "
                           "faces from warm surfaces. Ambiguous is not a face")}

    out = ls.skin(rgb2d[mask], allow_unreliable=True)
    out["confidence"] = confidence
    out["face_share"] = share
    out["provenance"] = provenance
    return out


def main():
    argv = [a for a in sys.argv[1:] if not a.startswith("-")]
    if len(argv) != 1:
        sys.exit(__doc__)
    if not Path(argv[0]).exists():
        sys.exit(f"no such file: {argv[0]}")

    r = skin(argv[0])
    print(f"file:       {argv[0]}")
    if r.get("provenance"):
        print(f"pixels:     {r['provenance']}")
    if r.get("face_share") is not None:
        print(f"face:       {r['face_share'] * 100:.1f}% of frame"
              f"   confidence {r['confidence']:.2f}")
    if r.get("ok"):
        print(f"skin tone:  ITA {r['ita']:.1f}°  ({r['ita_class']})")
        print( "            measured on the segmented face only, not on the")
        print( "            frame's warm content. Look at the picture before")
        print( "            trusting it: a mask is not a judgement.")
        return 0
    print(f"skin tone:  WITHHELD — {r['reason']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
