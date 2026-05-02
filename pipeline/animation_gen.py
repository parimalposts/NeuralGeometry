import json
import numpy as np
from datetime import datetime, timezone
from .config import ANIM_DIR, NUM_FRAMES, LATENT_DIM, FPS


def save_animation_data(
    latent_vectors: np.ndarray,
    displacements: np.ndarray,
    vertex_colors: np.ndarray,
) -> None:
    """Save all animation arrays and manifest JSON."""
    ANIM_DIR.mkdir(parents=True, exist_ok=True)

    np.save(ANIM_DIR / "latent_vectors.npy",  latent_vectors.astype(np.float32))
    np.save(ANIM_DIR / "displacements.npy",   displacements.astype(np.float32))
    np.save(ANIM_DIR / "vertex_colors.npy",   vertex_colors.astype(np.float32))

    num_vertices = displacements.shape[1]
    manifest = {
        "num_frames":   NUM_FRAMES,
        "num_vertices": num_vertices,
        "latent_dim":   LATENT_DIM,
        "fps":          FPS,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "arrays": {
            "latent_vectors":  {"shape": list(latent_vectors.shape),  "dtype": "float32"},
            "displacements":   {"shape": list(displacements.shape),   "dtype": "float32"},
            "vertex_colors":   {"shape": list(vertex_colors.shape),   "dtype": "float32"},
        },
    }
    with open(ANIM_DIR / "animation_manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)
