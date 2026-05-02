import numpy as np
from pathlib import Path
from panda3d.core import (
    GeomVertexFormat, GeomVertexData, GeomVertexWriter,
    Geom, GeomTriangles, GeomNode, NodePath,
)

ASSETS = Path(__file__).parent.parent.parent / "shared_assets"


class MeshAnimator:
    def __init__(self, loader):
        anim_dir = ASSETS / "animations"
        self.displacements = np.load(anim_dir / "displacements.npy")   # (60,642,3)
        self.vertex_colors  = np.load(anim_dir / "vertex_colors.npy")  # (60,642,4)

        # Load base mesh topology from .bam or rebuild from .npy frame 0
        base_frame = np.load(ASSETS / "meshes" / "keyframes" / "frame_000.npy")  # (642,3)
        self.num_verts = len(base_frame)
        self.num_frames = self.displacements.shape[0]

        # Load faces from bam for triangle topology
        bam_path = ASSETS / "meshes" / "neural_sphere_base.bam"
        bam_node = loader.loadModel(str(bam_path))
        geom_node = bam_node.find("**/+GeomNode").node()
        geom = geom_node.getGeom(0)
        prim = geom.getPrimitive(0)
        prim2 = prim.decompose()
        self.faces = []
        for i in range(prim2.getNumPrimitives()):
            s = prim2.getPrimitiveStart(i)
            self.faces.append((
                prim2.getVertex(s),
                prim2.getVertex(s + 1),
                prim2.getVertex(s + 2),
            ))
        bam_node.removeNode()

        # Build mutable GeomVertexData
        fmt = GeomVertexFormat.getV3n3cpt2()
        self.vdata = GeomVertexData("neural_sphere", fmt, Geom.UHDynamic)
        self.vdata.setNumRows(self.num_verts)

        prim_out = GeomTriangles(Geom.UHStatic)
        for f in self.faces:
            prim_out.addVertices(*f)
        prim_out.closePrimitive()

        geom_out = Geom(self.vdata)
        geom_out.addPrimitive(prim_out)
        node_out = GeomNode("animated_sphere")
        node_out.addGeom(geom_out)
        self.nodepath = NodePath(node_out)

        # Precompute base vertex positions for displacement addition
        base_verts_raw = geom.getVertexData()
        base_reader = base_verts_raw.getArrayHandle(0)
        self._base_verts = base_frame   # (642,3) — frame 0 absolute positions

        self.frame_idx = 0
        self._write_frame(0)

    def _write_frame(self, fi: int) -> None:
        verts  = self._base_verts + self.displacements[fi]   # (642,3)
        colors = self.vertex_colors[fi]                       # (642,4)

        # Recompute smooth normals
        faces_arr = np.array(self.faces, dtype=np.int32)
        v0 = verts[faces_arr[:, 0]]
        v1 = verts[faces_arr[:, 1]]
        v2 = verts[faces_arr[:, 2]]
        fn = np.cross(v1 - v0, v2 - v0)
        normals = np.zeros_like(verts)
        for i in range(3):
            np.add.at(normals, faces_arr[:, i], fn)
        norms = np.linalg.norm(normals, axis=1, keepdims=True)
        normals /= np.where(norms == 0, 1.0, norms)

        # Spherical UVs
        x, y, z = verts[:, 0], verts[:, 1], verts[:, 2]
        u = 0.5 + np.arctan2(z, x) / (2 * np.pi)
        v_coord = 0.5 - np.arcsin(np.clip(y / np.maximum(np.linalg.norm(verts, axis=1), 1e-6), -1, 1)) / np.pi

        vw = GeomVertexWriter(self.vdata, "vertex")
        nw = GeomVertexWriter(self.vdata, "normal")
        cw = GeomVertexWriter(self.vdata, "color")
        tw = GeomVertexWriter(self.vdata, "texcoord")
        for i in range(self.num_verts):
            vw.setData3f(float(verts[i, 0]),   float(verts[i, 1]),   float(verts[i, 2]))
            nw.setData3f(float(normals[i, 0]), float(normals[i, 1]), float(normals[i, 2]))
            cw.setData4f(float(colors[i, 0]),  float(colors[i, 1]),  float(colors[i, 2]), float(colors[i, 3]))
            tw.setData2f(float(u[i]), float(v_coord[i]))

    def update(self, fi: int) -> None:
        if fi != self.frame_idx:
            self.frame_idx = fi
            self._write_frame(fi)
