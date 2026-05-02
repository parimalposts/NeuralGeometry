"""
Export animation data for Defold (Lua engine).
Produces JSON metadata instead of .npy binary — avoids binary parsing in Lua.
"""
import json
import numpy as np
import trimesh
from ..config import META_DIR, NUM_FRAMES, FPS


def export_defold(
    mesh: trimesh.Trimesh,
    latent_vectors: np.ndarray,
    displacements: np.ndarray,
    vertex_colors: np.ndarray,
) -> None:
    META_DIR.mkdir(parents=True, exist_ok=True)

    verts = mesh.vertices
    # Orthographic projection: top-down (looking along -Z), project XY
    proj_x = verts[:, 0]
    proj_y = verts[:, 1]

    # Normalize to [0,1] range for display coordinates
    px_min, px_max = proj_x.min(), proj_x.max()
    py_min, py_max = proj_y.min(), proj_y.max()

    # Pick top 60 vertices by mean displacement for the radial display
    mean_disp = np.linalg.norm(displacements, axis=(0, 2))  # (V,)
    top_idx = np.argsort(mean_disp)[-60:][::-1].tolist()

    frames = []
    for fi in range(NUM_FRAMES):
        disp_mag = np.linalg.norm(displacements[fi], axis=1)  # (V,)
        z = latent_vectors[fi].tolist()
        vdata = []
        for vi in top_idx:
            nx = float((proj_x[vi] - px_min) / max(px_max - px_min, 1e-6))
            ny = float((proj_y[vi] - py_min) / max(py_max - py_min, 1e-6))
            mag = float(disp_mag[vi])
            color = [float(c) for c in vertex_colors[fi, vi]]
            vdata.append({"x": nx, "y": ny, "mag": mag, "color": color})
        frames.append({
            "frame": fi,
            "latent": z,
            "vertices": vdata,
            "spritesheet_col": fi % 8,
            "spritesheet_row": fi // 8,
        })

    manifest = {
        "num_frames": NUM_FRAMES,
        "fps": FPS,
        "num_display_vertices": len(top_idx),
        "frames": frames,
    }

    out = META_DIR / "animation_manifest_defold.json"
    with open(out, "w") as f:
        json.dump(manifest, f, separators=(",", ":"))
    print(f"  [defold] wrote {out} ({out.stat().st_size // 1024} KB)")
