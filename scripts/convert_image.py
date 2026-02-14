#!/usr/bin/env python3
"""Image format conversion tool."""
import sys
import json
import base64
from pathlib import Path
from io import BytesIO

try:
    from PIL import Image
except ImportError as e:
    print(json.dumps({"error": f"Missing Python package: {e}. Install with: pip3 install Pillow"}))
    sys.exit(1)


FORMAT_MAP = {
    'jpg': ('JPEG', '.jpg'),
    'jpeg': ('JPEG', '.jpeg'),
    'png': ('PNG', '.png'),
    'webp': ('WEBP', '.webp'),
}


def convert_raster(input_path, target_format):
    """Convert between raster formats: jpg, png, webp."""
    pil_format, ext = FORMAT_MAP[target_format]
    output_path = input_path.with_suffix(ext)

    if output_path == input_path:
        output_path = input_path.parent / (input_path.stem + '_converted' + ext)

    img = Image.open(input_path)

    if pil_format == 'JPEG':
        if img.mode in ('RGBA', 'LA', 'PA'):
            bg = Image.new('RGB', img.size, (255, 255, 255))
            bg.paste(img, mask=img.split()[-1])
            img = bg
        elif img.mode == 'P':
            img = img.convert('RGB')
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        img.save(str(output_path), pil_format, quality=95)
    else:
        if pil_format == 'PNG' and img.mode not in ('RGBA', 'RGB', 'L', 'LA', 'P'):
            img = img.convert('RGBA')
        img.save(str(output_path), pil_format)

    return json.dumps({"success": True, "output": str(output_path)})


def convert_to_svg(input_path):
    """Wrap raster image in an SVG container with embedded base64 PNG."""
    img = Image.open(input_path)
    w, h = img.size

    buf = BytesIO()
    img_rgba = img.convert('RGBA')
    img_rgba.save(buf, format='PNG')
    b64 = base64.b64encode(buf.getvalue()).decode('ascii')

    svg_content = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<svg xmlns="http://www.w3.org/2000/svg" '
        'xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'width="{w}" height="{h}" viewBox="0 0 {w} {h}">\n'
        f'  <image width="{w}" height="{h}" '
        f'href="data:image/png;base64,{b64}"/>\n'
        '</svg>'
    )

    output_path = input_path.with_suffix('.svg')
    output_path.write_text(svg_content, encoding='utf-8')

    return json.dumps({"success": True, "output": str(output_path)})


def convert_from_svg(input_path, target_format):
    """Convert SVG to raster format using cairosvg."""
    try:
        import cairosvg
    except ImportError:
        return json.dumps({
            "error": "SVG-to-raster conversion requires cairosvg. "
                     "Install with: pip3 install cairosvg"
        })

    pil_format, ext = FORMAT_MAP[target_format]
    output_path = input_path.with_suffix(ext)

    png_data = cairosvg.svg2png(url=str(input_path))
    img = Image.open(BytesIO(png_data))

    if pil_format == 'JPEG':
        if img.mode in ('RGBA', 'LA', 'PA'):
            bg = Image.new('RGB', img.size, (255, 255, 255))
            bg.paste(img, mask=img.split()[-1])
            img = bg
        else:
            img = img.convert('RGB')
        img.save(str(output_path), pil_format, quality=95)
    elif pil_format == 'WEBP':
        img.save(str(output_path), pil_format)
    else:
        img.save(str(output_path), pil_format)

    return json.dumps({"success": True, "output": str(output_path)})


def convert(input_path_str, target_format):
    """Main conversion dispatcher."""
    input_path = Path(input_path_str)
    target_format = target_format.lower()
    input_ext = input_path.suffix.lower()

    if target_format == 'svg':
        return convert_to_svg(input_path)

    if input_ext == '.svg':
        return convert_from_svg(input_path, target_format)

    if target_format not in FORMAT_MAP:
        return json.dumps({"error": f"Unsupported format: {target_format}"})

    return convert_raster(input_path, target_format)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(json.dumps({"error": "Usage: convert_image.py <input_path> <target_format>"}))
        sys.exit(1)

    try:
        result = convert(sys.argv[1], sys.argv[2])
        print(result)
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)
