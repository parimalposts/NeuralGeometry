extends Node3D

# Root scene autoload — loads the neural sphere scene and wires up input.

const NEURAL_SPHERE_SCENE = preload("res://scenes/neural_sphere.tscn")

var _sphere_node: Node3D

func _ready() -> void:
	_sphere_node = NEURAL_SPHERE_SCENE.instantiate()
	add_child(_sphere_node)

func _input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed:
		if event.keycode == KEY_ESCAPE:
			get_tree().quit()
		elif event.keycode == KEY_R:
			# Reset animation by reloading the sphere node
			_sphere_node.reset_animation()
