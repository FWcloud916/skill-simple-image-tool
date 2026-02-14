#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "Pillow",
#     "numpy",
# ]
# ///
"""Image matting tool - removes specified colors from an image."""
import sys
import json
import base64
from io import BytesIO

try:
    import numpy as np
    from PIL import Image
except ImportError as e:
    print(json.dumps({
        "error": f"Missing Python package: {e}. Run with: uv run scripts/image_matting.py"
    }))
    sys.exit(1)


def hex_to_rgb(hex_str):
    """Convert hex color string to RGB tuple."""
    h = hex_str.lstrip('#')
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def process(input_path, colors_str, tolerance, feather, output_path=None):
    """
    Remove specified colors from an image, making them transparent.

    Args:
        input_path: Path to input image
        colors_str: Comma-separated hex colors, e.g. "#ff0000,#00ff00"
        tolerance: Color distance threshold (euclidean in RGB space)
        feather: Feather width for smooth edge transition
        output_path: If set, save to file. Otherwise return base64.
    """
    img = Image.open(input_path).convert('RGBA')
    data = np.array(img, dtype=np.float64)

    colors = [hex_to_rgb(c.strip()) for c in colors_str.split(',') if c.strip()]
    if not colors:
        return json.dumps({"error": "No colors specified"})

    h, w = data.shape[:2]

    # Start with fully opaque
    alpha = np.ones((h, w), dtype=np.float64)

    for (r, g, b) in colors:
        # Euclidean distance in RGB space
        diff = np.sqrt(
            (data[:, :, 0] - r) ** 2 +
            (data[:, :, 1] - g) ** 2 +
            (data[:, :, 2] - b) ** 2
        )

        if feather > 0:
            # Smooth transition: transparent within tolerance, fade over feather range
            color_alpha = np.clip((diff - tolerance) / feather, 0.0, 1.0)
        else:
            color_alpha = np.where(diff <= tolerance, 0.0, 1.0)

        # Combine: minimum alpha across all picked colors
        alpha = np.minimum(alpha, color_alpha)

    # Preserve any existing alpha from the original image
    original_alpha = data[:, :, 3] / 255.0
    final_alpha = alpha * original_alpha
    data[:, :, 3] = (final_alpha * 255).astype(np.uint8)

    result = Image.fromarray(data.astype(np.uint8))

    if output_path:
        result.save(output_path, 'PNG')
        return json.dumps({"success": True, "output": output_path})
    else:
        buf = BytesIO()
        result.save(buf, format='PNG', optimize=True)
        b64 = base64.b64encode(buf.getvalue()).decode('ascii')
        return json.dumps({"success": True, "base64": b64})


if __name__ == '__main__':
    if len(sys.argv) < 5:
        print(json.dumps({
            "error": "Usage: image_matting.py <input> <colors> <tolerance> <feather> [output]"
        }))
        sys.exit(1)

    input_path = sys.argv[1]
    colors_str = sys.argv[2]
    tolerance = float(sys.argv[3])
    feather = float(sys.argv[4])
    output_path = sys.argv[5] if len(sys.argv) > 5 else None

    try:
        result = process(input_path, colors_str, tolerance, feather, output_path)
        print(result)
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)
