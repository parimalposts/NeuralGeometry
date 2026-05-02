#!/usr/bin/env python3
"""
Smoke-test for the Neural Geometry asset pipeline.
Usage: python tools/verify_pipeline.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np

ASSETS = Path("shared_assets")
PASS = "  [PASS]"
FAIL = "  [FAIL]"
errors = []

def check(condition: bool, label: str) -> None:
    if condition:
        print(f"{PASS} {label}")
    else:
        print(f"{FAIL} {label}")
        errors.append(label)

def check_file(path: Path, min_bytes: int = 1) -> None:
    ok = path.exists() and path.stat().st_size >= min_bytes
    check(ok, f"File exists: {path.relative_to(Path('.'))}")

def check_npy_shape(path: Path, expected_shape: tuple) -> None:
    try:
        arr = np.load(path)
        check(arr.shape == expected_shape,
              f"Shape {arr.shape} == {expected_shape}: {path.name}")
    except Exception as e:
        check(False, f"Load {path.name}: {e}")

print("\n=== Neural Geometry Pipeline Verification ===\n")

# ── Keyframe meshes
print("Keyframe meshes (60 × frame_NNN.npy):")
for i in range(60):
    p = ASSETS / "meshes" / "keyframes" / f"frame_{i:03d}.npy"
    check_file(p, 7000)
check_npy_shape(ASSETS / "meshes" / "keyframes" / "frame_000.npy", (642, 3))

# ── Faces
print("\nMesh topology:")
check_file(ASSETS / "meshes" / "faces.npy", 100)
check_npy_shape(ASSETS / "meshes" / "faces.npy", (1280, 3))
check_file(ASSETS / "meshes" / "neural_sphere_base.glb", 10000)
check_file(ASSETS / "meshes" / "neural_sphere_base.obj",  1000)
check_file(ASSETS / "meshes" / "neural_sphere_base.bam",  1000)

# ── Animation arrays
print("\nAnimation arrays:")
check_npy_shape(ASSETS / "animations" / "latent_vectors.npy",  (60, 4))
check_npy_shape(ASSETS / "animations" / "displacements.npy",   (60, 642, 3))
check_npy_shape(ASSETS / "animations" / "vertex_colors.npy",   (60, 642, 4))
check_file(ASSETS / "animations" / "animation_manifest.json")

# ── Textures
print("\nTextures:")
for i in range(64):
    p = ASSETS / "textures" / "activation_frames" / f"act_frame_{i:03d}.png"
    check_file(p, 5000)
check_file(ASSETS / "textures" / "activation_map_base.png",        5000)
check_file(ASSETS / "textures" / "activation_map_spritesheet.png", 100000)

# Verify spritesheet dimensions
try:
    from PIL import Image
    sheet = Image.open(ASSETS / "textures" / "activation_map_spritesheet.png")
    check(sheet.size == (4096, 4096), f"Spritesheet size {sheet.size} == (4096, 4096)")
except Exception as e:
    check(False, f"Spritesheet open: {e}")

# ── Metadata
print("\nMetadata:")
check_file(ASSETS / "metadata" / "animation_manifest_defold.json", 10000)
check_file(ASSETS / "metadata" / "solar2d_metadata.json",           5000)
check_file(ASSETS / "metadata" / "mesh_topology.json")
check_file(ASSETS / "metadata" / "pipeline_manifest.json")

# ── Value sanity checks
print("\nValue sanity:")
lv = np.load(ASSETS / "animations" / "latent_vectors.npy")
check(float(lv.min()) >= -1.1 and float(lv.max()) <= 1.1,
      f"Latent vectors in [-1, 1] range (min={lv.min():.3f}, max={lv.max():.3f})")

vc = np.load(ASSETS / "animations" / "vertex_colors.npy")
check(float(vc.min()) >= 0.0 and float(vc.max()) <= 1.01,
      f"Vertex colors in [0, 1] range (min={vc.min():.3f}, max={vc.max():.3f})")

disp = np.load(ASSETS / "animations" / "displacements.npy")
check(float(np.abs(disp).max()) <= 0.6,
      f"Displacements within ±0.6 (max_abs={np.abs(disp).max():.3f})")

# ── GLB magic bytes
print("\nGLB format:")
glb = (ASSETS / "meshes" / "neural_sphere_base.glb").read_bytes()
check(glb[:4] == b"glTF", f"GLB magic bytes == b'glTF'")

# ── Summary
print("\n" + "="*45)
if not errors:
    print("  ALL CHECKS PASSED ✓")
else:
    print(f"  {len(errors)} CHECK(S) FAILED:")
    for e in errors:
        print(f"    - {e}")
    sys.exit(1)
