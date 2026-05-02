"""
Export animation data for Solar2D (Lua engine).
Produces JSON with 2D projected positions for top vertices per frame.
"""
import json
import numpy as np
import trimesh
from ..config import META_DIR, NUM_FRAMES, FPS


def export_solar2d(
    mesh: trimesh.Trimesh,
    latent_vectors: np.ndarray,
    displacements: np.ndarray,
    vertex_colors: np.ndarray,
    top_n: int = 20,
) -> None:
    META_DIR.mkdir(parents=True, exist_ok=True)

    verts = mesh.vertices
    # Radial projection: treat XY as screen plane, distance from origin = display radius
    proj_x = verts[:, 0]
    proj_y = verts[:, 1]

    frames = []
    for fi in range(NUM_FRAMES):
        disp_mag = np.linalg.norm(displacements[fi], axis=1)  # (V,)
        top_idx = np.argsort(disp_mag)[-top_n:][::-1]

        z = latent_vectors[fi].tolist()
        vdata = []
        for vi in top_idx.tolist():
            mag = float(disp_mag[vi])
            # normalize position to [-0.5, 0.5] content coordinates
            nx = float(proj_x[vi])
            ny = float(proj_y[vi])
            r = float(vertex_colors[fi, vi, 0])
            g = float(vertex_colors[fi, vi, 1])
            b = float(vertex_colors[fi, vi, 2])
            vdata.append({"x": nx, "y": ny, "mag": mag, "r": r, "g": g, "b": b})

        # Edges: connect each vertex to its nearest neighbor in the top set (by 3D distance)
        top_verts3d = mesh.vertices[top_idx]
        edges = []
        for i, vi in enumerate(top_idx.tolist()):
            dists = np.linalg.norm(top_verts3d - top_verts3d[i], axis=1)
            dists[i] = 1e9
            j = int(np.argmin(dists))
            if i < j:  # avoid duplicates
                edges.append([i, j])

        frames.append({
            "frame": fi,
            "latent": z,
            "vertices": vdata,
            "edges": edges,
            "spritesheet_frame": fi % 64,
        })

    manifest = {
        "num_frames": NUM_FRAMES,
        "fps": FPS,
        "top_n": top_n,
        "frames": frames,
    }

    out = META_DIR / "solar2d_metadata.json"
    with open(out, "w") as f:
        json.dump(manifest, f, separators=(",", ":"))
    print(f"  [solar2d] wrote {out} ({out.stat().st_size // 1024} KB)")
