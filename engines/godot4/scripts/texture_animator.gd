extends Node

# Advances the activation texture on the parent MeshInstance3D every interval_s seconds.

@export var interval_s: float = 2.0

var _elapsed: float = 0.0
var _frame_idx: int = 0
var _textures: Array[Texture2D] = []
var _mesh_instance: MeshInstance3D


func _ready() -> void:
	_mesh_instance = get_parent().get_node("MeshInstance3D")
	_load_textures()


func _load_textures() -> void:
	var frames_dir = ProjectSettings.globalize_path("res://") + "../../shared_assets/textures/activation_frames/"
	for i in range(64):
		var path = frames_dir + "act_frame_%03d.png" % i
		var img  := Image.load_from_file(path)
		if img:
			_textures.append(ImageTexture.create_from_image(img))


func _process(delta: float) -> void:
	if _textures.is_empty():
		return
	_elapsed += delta
	if _elapsed >= interval_s:
		_elapsed -= interval_s
		_frame_idx = (_frame_idx + 1) % _textures.size()
		var mat := _mesh_instance.material_override as ShaderMaterial
		if mat:
			mat.set_shader_parameter("activation_texture", _textures[_frame_idx])
