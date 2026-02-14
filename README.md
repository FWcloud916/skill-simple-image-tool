# Image Processing Agent Skill

An [Agent Skill](https://agentskills.io) for image processing. Gives AI agents (Claude Code, Cursor, Gemini CLI, etc.) the ability to convert image formats, resize images, and remove backgrounds.

## Capabilities

| Operation | Description |
|-----------|-------------|
| **Convert** | Convert between JPG, PNG, WebP, SVG, BMP, TIFF, GIF |
| **Resize** | Resize with automatic aspect ratio preservation |
| **Matting** | Remove background colors with adjustable tolerance and feathering |

All scripts output structured JSON, making them easy to chain together for multi-step workflows.

## Installation

Clone into your project's skill directory:

```bash
git clone git@github.com:FWcloud916/skill-simple-image-tool.git image-processing
```

### Dependencies

Python 3 with Pillow and numpy:

```bash
pip install Pillow numpy
```

## Quick Start

```bash
# Convert format
python scripts/convert_image.py logo.png webp
# {"success": true, "output": "logo.webp"}

# Resize (auto height)
python scripts/resize_image.py photo.jpg 512 0
# {"success": true, "output": "photo_512x384.jpg", "width": 512, "height": 384}

# Remove white background
python scripts/image_matting.py logo.png "#FFFFFF" 30 5 logo_matted.png
# {"success": true, "output": "logo_matted.png"}
```

## How It Works

Compatible AI agents automatically discover the `SKILL.md` file and load the instructions when a task involves image processing. The agent then runs the bundled Python scripts to perform the requested operations.

See [SKILL.md](SKILL.md) for the full agent instructions and [references/REFERENCE.md](references/REFERENCE.md) for the detailed API reference.

## Related

This skill is part of the [Simple Image Tool](https://github.com/FWcloud916/vscode-simple-image-tool) VS Code extension, which provides the same capabilities through a graphical interface and a GitHub Copilot chat participant (`@image-tool`).

## License

MIT
