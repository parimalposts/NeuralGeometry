extends Control

# HUD overlay: frame counter + latent vector display.
# Connects to the NeuralSphere's frame_changed signal.

var _title_label:  Label
var _frame_label:  Label
var _latent_label: Label


func _ready() -> void:
	_build_labels()
	# Connect to the neural sphere once it's in the tree
	call_deferred("_connect_sphere")


func _build_labels() -> void:
	_title_label = _make_label("NEURAL GEOMETRY", Vector2(20, 20), 22, Color(0.4, 0.8, 1.0))
	_frame_label  = _make_label("Frame: 0 / 60",  Vector2(20, 52), 16, Color(1, 1, 1))
	_latent_label = _make_label("z = [0.00, 0.00, 0.00, 0.00]", Vector2(20, 76), 15, Color(0.8, 0.9, 1.0))


func _make_label(text: String, pos: Vector2, size: int, color: Color) -> Label:
	var lbl := Label.new()
	lbl.text = text
	lbl.position = pos
	lbl.add_theme_font_size_override("font_size", size)
	lbl.add_theme_color_override("font_color", color)
	lbl.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.7))
	lbl.add_theme_constant_override("shadow_offset_x", 2)
	lbl.add_theme_constant_override("shadow_offset_y", 2)
	add_child(lbl)
	return lbl


func _connect_sphere() -> void:
	var sphere := get_tree().get_first_node_in_group("neural_sphere")
	if sphere and sphere.has_signal("frame_changed"):
		sphere.frame_changed.connect(_on_frame_changed)


func _on_frame_changed(frame_idx: int, latent: Array) -> void:
	_frame_label.text  = "Frame: %02d / 60" % frame_idx
	_latent_label.text = "z = [%.2f, %.2f, %.2f, %.2f]" % [
		latent[0], latent[1], latent[2], latent[3]
	]
