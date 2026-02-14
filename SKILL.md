---
name: image-processing
description: >-
  Converts image formats (JPG, PNG, WebP, SVG), resizes images with aspect ratio
  preservation, and removes background colors from images. Use when the user wants
  to convert, resize, or remove backgrounds from image files (.jpg, .png, .webp,
  .svg, .bmp, .tiff, .gif). Also use when processing batches of images or chaining
  multiple image operations together.
metadata:
  author: FWcloud916
  version: "1.0"
compatibility: Requires Python 3 and uv. Dependencies are declared inline (PEP 723) and installed automatically by uv run.
---

# Image Processing

Three Python scripts for converting formats, resizing, and removing backgrounds. All scripts output JSON to stdout.

## Setup

Requires [uv](https://docs.astral.sh/uv/). Each script declares its own dependencies via PEP 723 inline metadata, so `uv run` handles installation automatically.

## Convert Format

Converts between JPG, PNG, WebP, and SVG.

```bash
uv run scripts/convert_image.py <input_path> <target_format>
```

**Supported formats**: jpg, jpeg, png, webp, svg, bmp, tiff, gif

**Example**:
```bash
uv run scripts/convert_image.py logo.png webp
# Output: {"success": true, "output": "logo.webp"}
```

**Notes**:
- RGBA images converting to JPEG get a white background automatically
- Converting to SVG wraps the raster image as an embedded base64 PNG
- If output would overwrite input, a `_converted` suffix is added

## Resize Image

Resizes with aspect ratio preservation. Width or height of `0` means auto-calculate.

```bash
uv run scripts/resize_image.py <input_path> <width> <height>
```

**Examples**:
```bash
# Exact dimensions
uv run scripts/resize_image.py photo.jpg 800 600
# Output: {"success": true, "output": "photo_800x600.jpg", "width": 800, "height": 600}

# Width only (auto height)
uv run scripts/resize_image.py photo.jpg 512 0
# Output: {"success": true, "output": "photo_512x384.jpg", "width": 512, "height": 384}

# Height only (auto width)
uv run scripts/resize_image.py photo.jpg 0 256
# Output: {"success": true, "output": "photo_341x256.jpg", "width": 341, "height": 256}
```

Output filename follows the pattern: `{stem}_{width}x{height}{ext}`

## Remove Background (Matting)

Removes specified colors from an image, making them transparent. Uses Euclidean distance in RGB color space.

```bash
uv run scripts/image_matting.py <input> <colors> <tolerance> <feather> [output_path]
```

**Parameters**:
- `colors`: Comma-separated hex colors, e.g. `#FFFFFF` or `#FF0000,#00FF00`
- `tolerance`: Color distance threshold (0-200). Higher = more colors removed
- `feather`: Edge smoothing width (0-20). Higher = softer edges
- `output_path`: If provided, saves to file. Otherwise returns base64

**Examples**:
```bash
# Remove white background, save to file
uv run scripts/image_matting.py logo.png "#FFFFFF" 30 5 logo_matted.png
# Output: {"success": true, "output": "logo_matted.png"}

# Remove green screen
uv run scripts/image_matting.py photo.jpg "#00FF00" 50 10 photo_clean.png
# Output: {"success": true, "output": "photo_clean.png"}

# Get base64 result (no output path)
uv run scripts/image_matting.py logo.png "#FFFFFF" 30 5
# Output: {"success": true, "base64": "iVBORw0KGgo..."}
```

**Common colors**:
| Color | Hex |
|-------|-----|
| White | #FFFFFF |
| Black | #000000 |
| Green | #00FF00 |
| Blue  | #0000FF |
| Red   | #FF0000 |

## Chaining Operations

All scripts output JSON with an `output` field containing the result file path. Use this to chain operations:

```bash
# Step 1: Remove white background
uv run scripts/image_matting.py logo.jpg "#FFFFFF" 30 5 logo_matted.png

# Step 2: Resize the result
uv run scripts/resize_image.py logo_matted.png 512 512

# Step 3: Convert to WebP
uv run scripts/convert_image.py logo_matted_512x512.png webp
```

Parse the JSON output to get the exact file path for the next step:

```bash
output=$(uv run scripts/convert_image.py input.png webp)
next_file=$(echo "$output" | python -c "import sys,json; print(json.load(sys.stdin)['output'])")
uv run scripts/resize_image.py "$next_file" 256 256
```

## Error Handling

All scripts return JSON errors:
```json
{"error": "description of what went wrong"}
```

Check the `success` field or presence of `error` field to determine outcome.

## Detailed Reference

For full API details, supported format mappings, edge cases, and JSON schemas, see [references/REFERENCE.md](references/REFERENCE.md).
