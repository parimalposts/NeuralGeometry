#!/usr/bin/env python3
"""
Master pipeline script — run once before any engine demo.
Usage: python -m pipeline.run_pipeline   (from project root)
       OR: python pipeline/run_pipeline.py
"""
import sys, time
from pathlib import Path

# Allow running as a script OR as a module
sys.path.insert(0, str(Path(__file__).parent.parent))

from pipeline.config import (
    ASSET_ROOT, MESHES_DIR, KEYFRAMES_DIR, TEXTURES_DIR,
    ACT_FRAMES_DIR, ANIM_DIR, META_DIR, NUM_FRAMES,
)
from pipeline.neural_sim   import NeuralDecoder, traverse_latent
from pipeline.mesh_gen     import (make_icosphere, apply_displacement,
                                   compute_vertex_colors, generate_keyframe_meshes)
from pipeline.texture_gen  import generate_all_frames, make_spritesheet, save_base_texture
from pipeline.animation_gen import save_animation_data
from pipeline.exporters.export_obj    import export_obj
from pipeline.exporters.export_gltf   import export_gltf
from pipeline.exporters.export_bam    import export_bam
from pipeline.exporters.export_defold import export_defold
from pipeline.exporters.export_solar2d import export_solar2d

import numpy as np
import json
from datetime import datetime, timezone


def _header(title: str) -> None:
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def run() -> None:
    t0 = time.time()
    _header("Neural Geometry — Asset Pipeline")

    # 1. Create output dirs
    for d in [MESHES_DIR, KEYFRAMES_DIR, TEXTURES_DIR, ACT_FRAMES_DIR, ANIM_DIR, META_DIR]:
        d.mkdir(parents=True, exist_ok=True)

    # 2. Generate latent sequence
    print("\n[1/7] Generating latent space trajectory...")
    latent_vectors = traverse_latent()          # (60, 4)
    print(f"      Latent sequence: {latent_vectors.shape}")

    # 3. Run neural decoder
    print("[2/7] Running simulated VAE decoder...")
    decoder = NeuralDecoder(seed=42)
    displacement_mags = decoder.decode_batch(latent_vectors)  # (60, 642)
    print(f"      Displacement magnitudes: {displacement_mags.shape}")

    # 4. Generate mesh geometry
    print("[3/7] Generating icosphere and keyframe meshes...")
    mesh = make_icosphere()
    print(f"      Icosphere: {len(mesh.vertices)} vertices, {len(mesh.faces)} faces")

    # Build per-frame displaced vertex arrays
    all_verts  = np.stack([apply_displacement(mesh, displacement_mags[i])
                           for i in range(NUM_FRAMES)])   # (60, 642, 3)
    all_colors = np.stack([compute_vertex_colors(displacement_mags[i])
                           for i in range(NUM_FRAMES)])   # (60, 642, 4)

    generate_keyframe_meshes(mesh, all_verts)
    print(f"      Saved {NUM_FRAMES} keyframe .npy files")

    # 5. Generate textures
    print("[4/7] Generating activation-map textures...")
    tex_images = generate_all_frames(latent_vectors)
    save_base_texture(tex_images)
    make_spritesheet(tex_images)
    print(f"      Saved {len(tex_images)} frames + spritesheet")

    # 6. Save animation arrays + manifest
    print("[5/7] Saving animation data...")
    displacements = all_verts - mesh.vertices[None]   # delta from base (60, 642, 3)
    save_animation_data(latent_vectors, displacements, all_colors)
    print(f"      Saved latent_vectors, displacements, vertex_colors + manifest")

    # 7. Run exporters
    print("[6/7] Exporting engine assets...")
    print("  → OBJ / MTL ...")
    export_obj(mesh)

    print("  → GLB (GLTF2) ...")
    export_gltf(mesh)

    print("  → BAM (Panda3D) ...")
    ok = export_bam(mesh)
    if not ok:
        print("     (skipped — panda3d not available for headless bam export)")

    print("  → Defold JSON ...")
    export_defold(mesh, latent_vectors, displacements, all_colors)

    print("  → Solar2D JSON ...")
    export_solar2d(mesh, latent_vectors, displacements, all_colors)

    # 8. Write mesh topology metadata
    print("[7/7] Writing pipeline manifest...")
    topo = {
        "num_vertices": len(mesh.vertices),
        "num_faces":    len(mesh.faces),
        "subdivisions": 3,
        "mesh_radius":  float(np.linalg.norm(mesh.vertices, axis=1).max()),
    }
    with open(META_DIR / "mesh_topology.json", "w") as f:
        json.dump(topo, f, indent=2)

    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "num_frames":   NUM_FRAMES,
        "num_vertices": len(mesh.vertices),
        "files": _list_files(ASSET_ROOT),
    }
    with open(META_DIR / "pipeline_manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)

    elapsed = time.time() - t0
    _header(f"Pipeline complete in {elapsed:.1f}s")
    _print_summary(ASSET_ROOT)


def _list_files(root: Path) -> list:
    return [
        {"path": str(p.relative_to(root)), "size_bytes": p.stat().st_size}
        for p in sorted(root.rglob("*")) if p.is_file()
    ]


def _print_summary(root: Path) -> None:
    files = list(root.rglob("*"))
    total = sum(f.stat().st_size for f in files if f.is_file())
    print(f"\n  {sum(1 for f in files if f.is_file())} files written")
    print(f"  Total size: {total / 1024:.0f} KB")
    # Print key files
    key_patterns = ["*.glb", "*.bam", "*.npy", "*.json", "spritesheet*"]
    for f in sorted(root.rglob("*")):
        if f.is_file() and any(f.match(p) for p in key_patterns):
            rel = f.relative_to(root)
            sz = f.stat().st_size
            unit = "KB" if sz > 1024 else "B"
            val = sz // 1024 if sz > 1024 else sz
            print(f"  {str(rel):<55} {val:>6} {unit}")


if __name__ == "__main__":
    run()
