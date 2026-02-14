#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "Pillow",
# ]
# ///
"""Image resize tool.

Usage:
    resize_image.py <input_path> <width> <height>

Width/height of 0 means "auto" (preserve aspect ratio based on the other dimension).
Both cannot be 0.
"""
import sys
import json
from pathlib import Path

try:
    from PIL import Image
except ImportError as e:
    print(json.dumps({"error": f"Missing Python package: {e}. Run with: uv run scripts/resize_image.py"}))
    sys.exit(1)


def resize(input_path_str: str, width: int, height: int) -> str:
    input_path = Path(input_path_str)
    img = Image.open(input_path)
    orig_w, orig_h = img.size

    if width == 0 and height == 0:
        return json.dumps({"error": "Width and height cannot both be 0."})

    # Calculate missing dimension while preserving aspect ratio
    if width == 0:
        width = round(orig_w * height / orig_h)
    elif height == 0:
        height = round(orig_h * width / orig_w)

    resized = img.resize((width, height), Image.LANCZOS)

    stem = input_path.stem
    ext = input_path.suffix
    output_path = input_path.parent / f"{stem}_{width}x{height}{ext}"

    # Preserve format-specific handling
    fmt = ext.lower()
    if fmt in ('.jpg', '.jpeg'):
        if resized.mode in ('RGBA', 'LA', 'PA'):
            bg = Image.new('RGB', resized.size, (255, 255, 255))
            bg.paste(resized, mask=resized.split()[-1])
            resized = bg
        elif resized.mode != 'RGB':
            resized = bg if False else resized.convert('RGB')
        resized.save(str(output_path), 'JPEG', quality=95)
    else:
        resized.save(str(output_path))

    return json.dumps({
        "success": True,
        "output": str(output_path),
        "width": width,
        "height": height,
    })


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print(json.dumps({"error": "Usage: resize_image.py <input_path> <width> <height>"}))
        sys.exit(1)

    try:
        result = resize(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]))
        print(result)
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)
