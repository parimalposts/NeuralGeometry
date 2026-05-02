import struct
import numpy as np
import trimesh
import pygltflib
from ..config import MESHES_DIR


def export_gltf(mesh: trimesh.Trimesh) -> None:
    """Export base mesh as binary .glb for Godot 4 and Stride."""
    MESHES_DIR.mkdir(parents=True, exist_ok=True)

    verts = mesh.vertices.astype(np.float32)
    faces = mesh.faces.astype(np.uint32)
    normals = mesh.vertex_normals.astype(np.float32)
    uvs = _sphere_uvs(verts)

    # Pack binary buffer: positions | normals | uvs | indices
    pos_bytes    = verts.tobytes()
    norm_bytes   = normals.tobytes()
    uv_bytes     = uvs.tobytes()
    index_bytes  = faces.tobytes()

    blob = pos_bytes + norm_bytes + uv_bytes + index_bytes

    pos_offset   = 0
    norm_offset  = len(pos_bytes)
    uv_offset    = norm_offset + len(norm_bytes)
    idx_offset   = uv_offset + len(uv_bytes)

    gltf = pygltflib.GLTF2(
        scene=0,
        scenes=[pygltflib.Scene(nodes=[0])],
        nodes=[pygltflib.Node(mesh=0)],
        meshes=[pygltflib.Mesh(
            primitives=[pygltflib.Primitive(
                attributes=pygltflib.Attributes(
                    POSITION=0,
                    NORMAL=1,
                    TEXCOORD_0=2,
                ),
                indices=3,
                material=0,
            )]
        )],
        materials=[pygltflib.Material(
            name="neural_mat",
            pbrMetallicRoughness=pygltflib.PbrMetallicRoughness(
                baseColorFactor=[0.3, 0.5, 0.9, 1.0],
                metallicFactor=0.2,
                roughnessFactor=0.6,
            ),
            doubleSided=False,
        )],
        accessors=[
            pygltflib.Accessor(bufferView=0, componentType=pygltflib.FLOAT,
                               count=len(verts), type=pygltflib.VEC3,
                               min=verts.min(axis=0).tolist(), max=verts.max(axis=0).tolist()),
            pygltflib.Accessor(bufferView=1, componentType=pygltflib.FLOAT,
                               count=len(normals), type=pygltflib.VEC3),
            pygltflib.Accessor(bufferView=2, componentType=pygltflib.FLOAT,
                               count=len(uvs), type=pygltflib.VEC2),
            pygltflib.Accessor(bufferView=3, componentType=pygltflib.UNSIGNED_INT,
                               count=len(faces) * 3, type=pygltflib.SCALAR),
        ],
        bufferViews=[
            pygltflib.BufferView(buffer=0, byteOffset=pos_offset,  byteLength=len(pos_bytes),  target=pygltflib.ARRAY_BUFFER),
            pygltflib.BufferView(buffer=0, byteOffset=norm_offset, byteLength=len(norm_bytes), target=pygltflib.ARRAY_BUFFER),
            pygltflib.BufferView(buffer=0, byteOffset=uv_offset,   byteLength=len(uv_bytes),   target=pygltflib.ARRAY_BUFFER),
            pygltflib.BufferView(buffer=0, byteOffset=idx_offset,  byteLength=len(index_bytes), target=pygltflib.ELEMENT_ARRAY_BUFFER),
        ],
        buffers=[pygltflib.Buffer(byteLength=len(blob))],
    )
    gltf.set_binary_blob(blob)

    out = MESHES_DIR / "neural_sphere_base.glb"
    gltf.save_binary(str(out))


def _sphere_uvs(verts: np.ndarray) -> np.ndarray:
    x, y, z = verts[:, 0], verts[:, 1], verts[:, 2]
    u = 0.5 + np.arctan2(z, x) / (2 * np.pi)
    v = 0.5 - np.arcsin(np.clip(y, -1, 1)) / np.pi
    return np.stack([u, v], axis=1).astype(np.float32)
