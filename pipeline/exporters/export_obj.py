import numpy as np
import trimesh
from pathlib import Path
from ..config import MESHES_DIR


def export_obj(mesh: trimesh.Trimesh) -> None:
    """Export base mesh as .obj + .mtl for Panda3D fallback."""
    MESHES_DIR.mkdir(parents=True, exist_ok=True)
    obj_path = MESHES_DIR / "neural_sphere_base.obj"

    verts = mesh.vertices
    faces = mesh.faces
    normals = mesh.vertex_normals
    uvs = _sphere_uvs(verts)

    lines = [
        "# Neural Geometry — base icosphere",
        "mtllib neural_sphere_base.mtl",
        "usemtl neural_mat",
        "",
    ]
    for v in verts:
        lines.append(f"v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}")
    for uv in uvs:
        lines.append(f"vt {uv[0]:.6f} {uv[1]:.6f}")
    for n in normals:
        lines.append(f"vn {n[0]:.6f} {n[1]:.6f} {n[2]:.6f}")
    lines.append("")
    for f in faces:
        i, j, k = f + 1  # OBJ is 1-indexed
        lines.append(f"f {i}/{i}/{i} {j}/{j}/{j} {k}/{k}/{k}")

    obj_path.write_text("\n".join(lines))

    mtl = [
        "newmtl neural_mat",
        "Ka 0.1 0.1 0.1",
        "Kd 0.3 0.5 0.9",
        "Ks 0.2 0.2 0.2",
        "Ns 32.0",
        "map_Kd ../textures/activation_map_base.png",
    ]
    (MESHES_DIR / "neural_sphere_base.mtl").write_text("\n".join(mtl))


def _sphere_uvs(verts: np.ndarray) -> np.ndarray:
    """Spherical UV mapping."""
    x, y, z = verts[:, 0], verts[:, 1], verts[:, 2]
    u = 0.5 + np.arctan2(z, x) / (2 * np.pi)
    v = 0.5 - np.arcsin(np.clip(y, -1, 1)) / np.pi
    return np.stack([u, v], axis=1).astype(np.float32)
