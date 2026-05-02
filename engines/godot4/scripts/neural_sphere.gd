extends Node3D

# Reads .npy keyframe files and drives an ArrayMesh each frame.
# Also loads latent_vectors.npy for HUD display.

const ASSETS_PATH = "res://assets/"
const NUM_FRAMES  = 60
const FPS         = 30.0

var _mesh_instance: MeshInstance3D
var _material: ShaderMaterial
var _frames: Array          # Array of PackedVector3Array — one per keyframe
var _colors: Array          # Array of PackedColorArray  — one per frame
var _latent: Array          # Array of Array[float]      — one per frame
var _faces: PackedInt32Array

var _anim_time: float = 0.0
var _frame_idx: int   = 0

signal frame_changed(frame_idx: int, latent: Array)


func _ready() -> void:
	_mesh_instance = $MeshInstance3D
	_material = preload("res://resources/neural_material.tres")
	_mesh_instance.material_override = _material
	_load_all_frames()
	_build_mesh(0)


func _load_all_frames() -> void:
	var anim_dir = ProjectSettings.globalize_path("res://") + "../../shared_assets/animations/"
	var mesh_dir = ProjectSettings.globalize_path("res://") + "../../shared_assets/meshes/keyframes/"

	# Load latent vectors (60, 4)
	var lv_bytes := _load_npy_bytes(anim_dir + "latent_vectors.npy")
	_latent = _parse_npy_2d(lv_bytes, 60, 4)

	# Load vertex colors (60, 642, 4)
	var vc_bytes := _load_npy_bytes(anim_dir + "vertex_colors.npy")
	var vc_flat  := _parse_npy_flat_f32(vc_bytes)  # 60*642*4 floats

	# Load each keyframe (642, 3)
	_frames = []
	_colors = []
	for fi in range(NUM_FRAMES):
		var path = mesh_dir + "frame_%03d.npy" % fi
		var raw  := _load_npy_bytes(path)
		var flat := _parse_npy_flat_f32(raw)   # 642*3 floats

		var verts := PackedVector3Array()
		verts.resize(642)
		for vi in range(642):
			verts[vi] = Vector3(flat[vi*3], flat[vi*3+1], flat[vi*3+2])
		_frames.append(verts)

		var cols := PackedColorArray()
		cols.resize(642)
		var base = fi * 642 * 4
		for vi in range(642):
			cols[vi] = Color(vc_flat[base + vi*4],
							 vc_flat[base + vi*4 + 1],
							 vc_flat[base + vi*4 + 2],
							 vc_flat[base + vi*4 + 3])
		_colors.append(cols)


func _process(delta: float) -> void:
	_anim_time += delta
	var new_idx := int(_anim_time * FPS) % NUM_FRAMES
	if new_idx != _frame_idx:
		_frame_idx = new_idx
		_build_mesh(_frame_idx)
		frame_changed.emit(_frame_idx, _latent[_frame_idx])


func _build_mesh(fi: int) -> void:
	var verts  : PackedVector3Array = _frames[fi]
	var colors : PackedColorArray   = _colors[fi]

	# Compute normals via SurfaceTool (recalculate_normals does this for us)
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)

	# Build UVs (spherical)
	for vi in range(642):
		var v  := verts[vi]
		var r  := v.length()
		var u  := 0.5 + atan2(v.z, v.x) / (2.0 * PI)
		var vv := 0.5 - asin(clamp(v.y / max(r, 0.0001), -1.0, 1.0)) / PI
		st.set_uv(Vector2(u, vv))
		st.set_color(colors[vi])
		st.add_vertex(v)

	# Faces are constant — same topology as frame 0 (icosphere doesn't change connectivity)
	# We use the indices from a pre-built sphere with 1280 triangles, 642 verts
	# For simplicity, rebuild from trimesh's icosphere winding order stored in faces array
	# The indices are loaded once and cached.
	if _faces.size() == 0:
		_faces = _load_faces()

	for i in range(0, _faces.size(), 3):
		st.add_index(_faces[i])
		st.add_index(_faces[i+1])
		st.add_index(_faces[i+2])

	st.generate_normals()
	_mesh_instance.mesh = st.commit()


func _load_faces() -> PackedInt32Array:
	# Load face indices from a JSON file written by the pipeline
	var meta_path = ProjectSettings.globalize_path("res://") + "../../shared_assets/metadata/mesh_topology.json"
	var f := FileAccess.open(meta_path, FileAccess.READ)
	# topology JSON only has counts; rebuild icosphere faces via algorithm
	# Use trimesh-compatible icosphere subdivision level 3 winding
	# For robustness, we re-derive the faces from the base .npy frame 0
	# using a simple approach: pre-baked face list stored as faces.npy
	f.close()
	return _load_faces_from_npy()


func _load_faces_from_npy() -> PackedInt32Array:
	var path = ProjectSettings.globalize_path("res://") + "../../shared_assets/meshes/faces.npy"
	var fa := FileAccess.open(path, FileAccess.READ)
	if fa == null:
		push_error("faces.npy not found — run tools/export_faces_npy.py")
		return PackedInt32Array()
	var raw := fa.get_buffer(fa.get_length())
	fa.close()
	# Parse npy header
	var header_end := _find_npy_data_start(raw)
	var result := PackedInt32Array()
	var i := header_end
	while i + 4 <= raw.size():
		var b0 := raw[i]; var b1 := raw[i+1]; var b2 := raw[i+2]; var b3 := raw[i+3]
		result.append(b0 | (b1 << 8) | (b2 << 16) | (b3 << 24))
		i += 4
	return result


# ------------------------------------------------------------------ .npy utils

func _load_npy_bytes(path: String) -> PackedByteArray:
	var fa := FileAccess.open(path, FileAccess.READ)
	if fa == null:
		push_error("Cannot open: " + path)
		return PackedByteArray()
	var data := fa.get_buffer(fa.get_length())
	fa.close()
	return data


func _find_npy_data_start(raw: PackedByteArray) -> int:
	# .npy format: 6 magic bytes + 1 major + 1 minor + 2 header_len (little-endian) + header
	var header_len := raw[8] | (raw[9] << 8)
	return 10 + header_len


func _parse_npy_flat_f32(raw: PackedByteArray) -> PackedFloat32Array:
	var start := _find_npy_data_start(raw)
	var result := PackedFloat32Array()
	var i := start
	while i + 4 <= raw.size():
		var b0 := raw[i]; var b1 := raw[i+1]; var b2 := raw[i+2]; var b3 := raw[i+3]
		var bits := b0 | (b1 << 8) | (b2 << 16) | (b3 << 24)
		result.append(bits_to_float(bits))
		i += 4
	return result


func _parse_npy_2d(raw: PackedByteArray, rows: int, cols: int) -> Array:
	var flat := _parse_npy_flat_f32(raw)
	var result := []
	for r in range(rows):
		var row := []
		for c in range(cols):
			row.append(flat[r * cols + c])
		result.append(row)
	return result


func reset_animation() -> void:
	_anim_time = 0.0
	_frame_idx = 0
