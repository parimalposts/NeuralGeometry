#!/usr/bin/env python3
"""Quick trimesh viewer for any keyframe. Usage: python tools/preview_mesh.py [frame_idx]"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import trimesh
from pipeline.mesh_gen import make_icosphere

frame = int(sys.argv[1]) if len(sys.argv) > 1 else 0
path  = Path("shared_assets/meshes/keyframes") / f"frame_{frame:03d}.npy"

verts = np.load(path)
mesh  = make_icosphere()
mesh.vertices = verts

colors = np.load("shared_assets/animations/vertex_colors.npy")[frame]
mesh.visual.vertex_colors = (colors * 255).astype(np.uint8)

print(f"Frame {frame}: vertices={len(verts)}, displacement_rms={np.linalg.norm(verts - make_icosphere().vertices):.4f}")
mesh.show()
