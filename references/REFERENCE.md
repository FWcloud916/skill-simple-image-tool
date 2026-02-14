# Image Processing API Reference

## convert_image.py

### Usage
```
uv run scripts/convert_image.py <input_path> <target_format>
```

### Arguments
| Argument | Description |
|----------|-------------|
| `input_path` | Path to input image file |
| `target_format` | Target format: jpg, jpeg, png, webp, svg, bmp, tiff, gif |

### Format Map (Raster)
| Format key | PIL format | Extension |
|------------|-----------|-----------|
| jpg | JPEG | .jpg |
| jpeg | JPEG | .jpeg |
| png | PNG | .png |
| webp | WEBP | .webp |

### Conversion Behaviors

**Raster to raster** (jpg/png/webp):
- RGBA/LA/PA to JPEG: composites onto white background
- P mode to JPEG: converts to RGB
- Other modes to PNG: converts to RGBA
- Output path: same stem with new extension (e.g., `logo.png` → `logo.webp`)
- If output would match input path, adds `_converted` suffix

**Raster to SVG**:
- Wraps the image as a base64-encoded PNG inside an SVG container
- Preserves original dimensions in the SVG viewBox

**SVG to raster**:
- Requires `cairosvg` package (`uv pip install cairosvg`)
- Converts via PNG intermediate
- Applies same JPEG handling for alpha channels

### Success Output
```json
{"success": true, "output": "/absolute/path/to/result.webp"}
```

### Error Output
```json
{"error": "Unsupported format: xyz"}
```

---

## resize_image.py

### Usage
```
uv run scripts/resize_image.py <input_path> <width> <height>
```

### Arguments
| Argument | Description |
|----------|-------------|
| `input_path` | Path to input image file |
| `width` | Target width in pixels. Use `0` for auto-calculate from height |
| `height` | Target height in pixels. Use `0` for auto-calculate from width |

Both width and height cannot be `0` simultaneously.

### Behaviors
- Auto-dimension: if one dimension is `0`, calculates it from the other while preserving aspect ratio
- Resampling: uses `Image.LANCZOS` for high-quality downscaling
- Output naming: `{stem}_{width}x{height}{ext}` (e.g., `photo_512x384.jpg`)
- JPEG handling: composites RGBA onto white background, saves at quality 95

### Success Output
```json
{
  "success": true,
  "output": "/absolute/path/to/photo_512x384.jpg",
  "width": 512,
  "height": 384
}
```

### Error Output
```json
{"error": "Width and height cannot both be 0."}
```

---

## image_matting.py

### Usage
```
uv run scripts/image_matting.py <input> <colors> <tolerance> <feather> [output_path]
```

### Arguments
| Argument | Required | Description |
|----------|----------|-------------|
| `input` | Yes | Path to input image |
| `colors` | Yes | Comma-separated hex colors (e.g., `#FFFFFF` or `#FF0000,#00FF00`) |
| `tolerance` | Yes | Color distance threshold (float, 0-200). Euclidean distance in RGB space |
| `feather` | Yes | Edge feathering width (float, 0-20). Smooth transition range |
| `output_path` | No | If set, saves PNG to this path. Otherwise returns base64 |

### Algorithm
1. Converts input to RGBA
2. For each specified color, computes Euclidean distance in RGB space for every pixel
3. If `feather > 0`: alpha = clip((distance - tolerance) / feather, 0, 1) — smooth transition
4. If `feather == 0`: alpha = 0 if distance <= tolerance, else 1 — hard edge
5. For multiple colors: uses minimum alpha (union of removed colors)
6. Multiplies with existing alpha channel to preserve original transparency
7. Outputs as PNG (always, since transparency requires it)

### Success Output (with output_path)
```json
{"success": true, "output": "/absolute/path/to/result_matted.png"}
```

### Success Output (without output_path)
```json
{"success": true, "base64": "iVBORw0KGgoAAAANSUhEUg..."}
```

### Error Output
```json
{"error": "No colors specified"}
```

### Tips
- Start with tolerance 30 and feather 5 for clean backgrounds
- Increase tolerance (50-100) for photos with lighting variation
- Use feather 0 for pixel-art or hard-edged graphics
- Multiple colors can be specified to remove multi-colored backgrounds
