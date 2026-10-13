#!/usr/bin/env python3
"""Ensure an image is portrait 3:4 at 1080x1440.

Usage:
  python3 scripts/ensure_3x4.py INPUT [-o OUTPUT] [--bg R,G,B] [--force] [--mode pad|crop]

Defaults:
  - OUTPUT is INPUT with "-3x4" before the suffix (e.g. cover.png -> cover-3x4.png)
  - Overwrite INPUT only when --force is set (and -o omitted)
  - --mode pad: letterbox/pillarbox on --bg (default)
  - --mode crop: center-crop to 3:4 then scale
  - Target size: 1080x1440
Exit 0 only if final WxH is exactly 1080x1440.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

TARGET_W = 1080
TARGET_H = 1440
TARGET_RATIO = TARGET_W / TARGET_H  # 0.75


def die(msg: str, code: int = 1) -> None:
    print(msg, file=sys.stderr)
    raise SystemExit(code)


def parse_bg(s: str) -> tuple[int, int, int]:
    parts = [p.strip() for p in s.split(",")]
    if len(parts) != 3:
        die(f"--bg must be R,G,B got: {s!r}")
    try:
        rgb = tuple(int(p) for p in parts)
    except ValueError:
        die(f"--bg values must be integers: {s!r}")
    if any(v < 0 or v > 255 for v in rgb):
        die(f"--bg channels must be 0-255: {s!r}")
    return rgb  # type: ignore[return-value]


def default_output(inp: Path, force: bool) -> Path:
    if force:
        return inp
    return inp.with_name(f"{inp.stem}-3x4{inp.suffix or '.png'}")


def fit_pad(im, bg: tuple[int, int, int]):
    from PIL import Image

    w, h = im.size
    if w <= 0 or h <= 0:
        die(f"invalid size: {w}x{h}")
    ratio = w / h
    if abs(ratio - TARGET_RATIO) < 1e-6:
        canvas = im.convert("RGBA") if im.mode in ("RGBA", "LA", "P") else im.convert("RGB")
    elif ratio > TARGET_RATIO:
        # too wide: fit height, pad left/right
        new_h = h
        new_w = int(round(h * TARGET_RATIO))
        # Actually we scale later; first create 3:4 canvas matching max side intent
        # Simpler: scale so image fits inside TARGET, then paste on bg
        scale = min(TARGET_W / w, TARGET_H / h)
        nw, nh = max(1, int(round(w * scale))), max(1, int(round(h * scale)))
        resized = im.resize((nw, nh), Image.Resampling.LANCZOS)
        canvas = Image.new("RGB", (TARGET_W, TARGET_H), bg)
        if resized.mode == "RGBA":
            canvas.paste(resized, ((TARGET_W - nw) // 2, (TARGET_H - nh) // 2), resized)
        else:
            canvas.paste(resized.convert("RGB"), ((TARGET_W - nw) // 2, (TARGET_H - nh) // 2))
        return canvas
    else:
        # too tall: fit width, pad top/bottom — same fit-inside path
        scale = min(TARGET_W / w, TARGET_H / h)
        nw, nh = max(1, int(round(w * scale))), max(1, int(round(h * scale)))
        resized = im.resize((nw, nh), Image.Resampling.LANCZOS)
        canvas = Image.new("RGB", (TARGET_W, TARGET_H), bg)
        if resized.mode == "RGBA":
            canvas.paste(resized, ((TARGET_W - nw) // 2, (TARGET_H - nh) // 2), resized)
        else:
            canvas.paste(resized.convert("RGB"), ((TARGET_W - nw) // 2, (TARGET_H - nh) // 2))
        return canvas

    # already 3:4 — scale to exact pixels
    if canvas.size != (TARGET_W, TARGET_H):
        canvas = canvas.resize((TARGET_W, TARGET_H), Image.Resampling.LANCZOS)
    if canvas.mode != "RGB":
        # flatten alpha onto bg
        base = Image.new("RGB", canvas.size, bg)
        if canvas.mode == "RGBA":
            base.paste(canvas, mask=canvas.split()[-1])
            canvas = base
        else:
            canvas = canvas.convert("RGB")
    return canvas


def fit_crop(im, bg: tuple[int, int, int]):
    from PIL import Image

    w, h = im.size
    if w <= 0 or h <= 0:
        die(f"invalid size: {w}x{h}")
    ratio = w / h
    if ratio > TARGET_RATIO:
        # too wide: crop width
        new_w = int(round(h * TARGET_RATIO))
        left = max(0, (w - new_w) // 2)
        im = im.crop((left, 0, left + new_w, h))
    elif ratio < TARGET_RATIO:
        # too tall: crop height
        new_h = int(round(w / TARGET_RATIO))
        top = max(0, (h - new_h) // 2)
        im = im.crop((0, top, w, top + new_h))
    out = im.resize((TARGET_W, TARGET_H), Image.Resampling.LANCZOS)
    if out.mode == "RGBA":
        base = Image.new("RGB", out.size, bg)
        base.paste(out, mask=out.split()[-1])
        return base
    return out.convert("RGB")


def main() -> None:
    ap = argparse.ArgumentParser(description="Force image to 1080x1440 (3:4).")
    ap.add_argument("input", type=Path, help="Input image path")
    ap.add_argument("-o", "--output", type=Path, default=None, help="Output path")
    ap.add_argument("--bg", default="255,255,255", help="Pad background R,G,B (default 255,255,255)")
    ap.add_argument("--force", action="store_true", help="Overwrite input when -o omitted")
    ap.add_argument(
        "--mode",
        choices=("pad", "crop"),
        default="pad",
        help="pad=letterbox on bg (default); crop=center-crop then scale",
    )
    args = ap.parse_args()

    try:
        from PIL import Image
    except ImportError:
        die(
            "Pillow is required but not installed. Install with: python3 -m pip install Pillow",
            code=2,
        )

    inp = args.input.expanduser().resolve()
    if not inp.is_file():
        die(f"input not found: {inp}")

    out = args.output.expanduser().resolve() if args.output else default_output(inp, args.force)
    bg = parse_bg(args.bg)

    try:
        im = Image.open(inp)
        im.load()
    except Exception as e:
        die(f"failed to open image: {e}")

    src_w, src_h = im.size
    print(f"input: {src_w}x{src_h} ({inp})")

    if args.mode == "crop":
        result = fit_crop(im, bg)
    else:
        result = fit_pad(im, bg)

    out.parent.mkdir(parents=True, exist_ok=True)
    # Preserve png when possible
    suffix = out.suffix.lower()
    if suffix in (".jpg", ".jpeg"):
        result.save(out, quality=95, optimize=True)
    else:
        if out.suffix == "":
            out = out.with_suffix(".png")
        result.save(out, optimize=True)

    fw, fh = result.size
    print(f"output: {fw}x{fh} ({out})")
    if fw != TARGET_W or fh != TARGET_H:
        die(f"ratio check failed: got {fw}x{fh}, want {TARGET_W}x{TARGET_H}", code=1)
    print("ok: 1080x1440 (3:4)")


if __name__ == "__main__":
    main()
