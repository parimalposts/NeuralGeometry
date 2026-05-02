"""
Export Panda3D native .bam file.
Requires panda3d to be installed. Uses offscreen LoaderOptions to avoid a window.
"""
import trimesh
from ..config import MESHES_DIR


def export_bam(mesh: trimesh.Trimesh) -> bool:
    """
    Load the .obj we already wrote and re-save as .bam.
    Returns True on success, False if panda3d import fails.
    """
    try:
        from panda3d.core import (
            LoaderOptions, Filename, NodePath,
            GeomVertexFormat, GeomVertexData, GeomVertexWriter,
            Geom, GeomTriangles, GeomNode
        )
        import numpy as np
    except ImportError:
        print("[export_bam] panda3d not available — skipping .bam export")
        return False

    obj_path = MESHES_DIR / "neural_sphere_base.obj"
    bam_path = MESHES_DIR / "neural_sphere_base.bam"

    verts   = mesh.vertices.astype("float32")
    normals = mesh.vertex_normals.astype("float32")
    faces   = mesh.faces

    x, y, z_ = verts[:, 0], verts[:, 1], verts[:, 2]
    us = 0.5 + np.arctan2(z_, x) / (2 * 3.14159265)
    vs = 0.5 - np.arcsin(np.clip(y, -1, 1)) / 3.14159265

    fmt = GeomVertexFormat.get_v3n3t2()
    vdata = GeomVertexData("neural_sphere", fmt, Geom.UHStatic)
    vdata.setNumRows(len(verts))

    vw = GeomVertexWriter(vdata, "vertex")
    nw = GeomVertexWriter(vdata, "normal")
    tw = GeomVertexWriter(vdata, "texcoord")
    for i in range(len(verts)):
        vw.addData3f(float(verts[i, 0]), float(verts[i, 1]), float(verts[i, 2]))
        nw.addData3f(float(normals[i, 0]), float(normals[i, 1]), float(normals[i, 2]))
        tw.addData2f(float(us[i]), float(vs[i]))

    prim = GeomTriangles(Geom.UHStatic)
    for f in faces:
        prim.addVertices(int(f[0]), int(f[1]), int(f[2]))
    prim.closePrimitive()

    geom = Geom(vdata)
    geom.addPrimitive(prim)
    node = GeomNode("neural_sphere")
    node.addGeom(geom)

    np_node = NodePath(node)
    np_node.writeBamFile(Filename.fromOsSpecific(str(bam_path)))
    return True
