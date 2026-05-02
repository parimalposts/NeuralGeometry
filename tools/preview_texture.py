#!/usr/bin/env python3
"""Quick PIL viewer for any activation frame. Usage: python tools/preview_texture.py [frame_idx]"""
import sys
from pathlib import Path

frame = int(sys.argv[1]) if len(sys.argv) > 1 else 0
if sys.argv[1:] and sys.argv[1] == "sheet":
    path = Path("shared_assets/textures/activation_map_spritesheet.png")
else:
    path = Path("shared_assets/textures/activation_frames") / f"act_frame_{frame:03d}.png"

from PIL import Image
img = Image.open(path)
print(f"Image: {path}  size={img.size}  mode={img.mode}")
img.show()
