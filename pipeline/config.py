from pathlib import Path

ROOT = Path(__file__).parent.parent
ASSET_ROOT = ROOT / "shared_assets"

# Mesh
MESH_SUBDIVISIONS = 3       # icosphere subdivisions → 642 vertices, 1280 faces
DISPLACEMENT_SCALE = 0.35   # max vertex displacement magnitude

# Animation
NUM_FRAMES = 60
LATENT_DIM = 4
FPS = 30

# Colors (COLD → HOT heatmap)
COLOR_COLD = (0.1, 0.3, 0.9, 1.0)   # blue
COLOR_HOT  = (1.0, 0.4, 0.1, 1.0)   # orange

# Textures
TEXTURE_SIZE = 512
TEXTURE_FRAMES = 64  # frames in spritesheet (must be perfect square count for grid)
TEXTURE_GRID = (8, 8)

# Output paths
MESHES_DIR     = ASSET_ROOT / "meshes"
KEYFRAMES_DIR  = ASSET_ROOT / "meshes" / "keyframes"
TEXTURES_DIR   = ASSET_ROOT / "textures"
ACT_FRAMES_DIR = ASSET_ROOT / "textures" / "activation_frames"
ANIM_DIR       = ASSET_ROOT / "animations"
META_DIR       = ASSET_ROOT / "metadata"
