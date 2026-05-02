#!/usr/bin/env python3
"""Export icosphere face indices as faces.npy for Godot GDScript .npy parser."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
from pipeline.mesh_gen import make_icosphere
from pipeline.config import MESHES_DIR

mesh = make_icosphere()
faces = mesh.faces.astype(np.int32)   # (1280, 3)
out = MESHES_DIR / "faces.npy"
np.save(out, faces)
print(f"Saved {out}  shape={faces.shape}")
