import numpy as np
import trimesh
from .config import MESH_SUBDIVISIONS, DISPLACEMENT_SCALE, COLOR_COLD, COLOR_HOT, KEYFRAMES_DIR


def make_icosphere(subdivisions: int = MESH_SUBDIVISIONS) -> trimesh.Trimesh:
    return trimesh.creation.icosphere(subdivisions=subdivisions)


def apply_displacement(mesh: trimesh.Trimesh, magnitudes: np.ndarray) -> np.ndarray:
    """magnitudes: (V,) in [0,1] → displaced vertex positions: (V, 3)"""
    normals = mesh.vertex_normals
    displacements = normals * (magnitudes[:, None] * DISPLACEMENT_SCALE)
    return (mesh.vertices + displacements).astype(np.float32)


def compute_vertex_colors(magnitudes: np.ndarray) -> np.ndarray:
    """magnitudes: (V,) → RGBA vertex colors: (V, 4) float32"""
    cold = np.array(COLOR_COLD, dtype=np.float32)
    hot  = np.array(COLOR_HOT,  dtype=np.float32)
    t = magnitudes[:, None]
    return (cold * (1.0 - t) + hot * t).astype(np.float32)


def recompute_normals(vertices: np.ndarray, faces: np.ndarray) -> np.ndarray:
    """Compute smooth per-vertex normals from updated vertex positions."""
    v0 = vertices[faces[:, 0]]
    v1 = vertices[faces[:, 1]]
    v2 = vertices[faces[:, 2]]
    face_normals = np.cross(v1 - v0, v2 - v0)
    vertex_normals = np.zeros_like(vertices)
    for i in range(3):
        np.add.at(vertex_normals, faces[:, i], face_normals)
    norms = np.linalg.norm(vertex_normals, axis=1, keepdims=True)
    norms = np.where(norms == 0, 1.0, norms)
    return (vertex_normals / norms).astype(np.float32)


def generate_keyframe_meshes(mesh: trimesh.Trimesh, displacement_batches: np.ndarray) -> None:
    """displacement_batches: (F, V, 3) — save each frame as frame_NNN.npy"""
    KEYFRAMES_DIR.mkdir(parents=True, exist_ok=True)
    for i, verts in enumerate(displacement_batches):
        path = KEYFRAMES_DIR / f"frame_{i:03d}.npy"
        np.save(path, verts)
