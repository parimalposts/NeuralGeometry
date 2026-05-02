import numpy as np
from PIL import Image
from .config import TEXTURE_SIZE, TEXTURE_FRAMES, TEXTURE_GRID, ACT_FRAMES_DIR, TEXTURES_DIR


def _gaussian_blob(arr: np.ndarray, cx: float, cy: float, sigma: float, color: np.ndarray) -> None:
    """Add a Gaussian blob in-place on arr (H, W, 3) float32."""
    H, W = arr.shape[:2]
    ys, xs = np.mgrid[0:H, 0:W]
    g = np.exp(-((xs - cx * W) ** 2 + (ys - cy * H) ** 2) / (2 * sigma ** 2))
    arr += g[:, :, None] * color[None, None, :]


def make_activation_frame(latent_vector: np.ndarray, size: int = TEXTURE_SIZE) -> Image.Image:
    """Generate one activation-map PNG from a 4D latent vector."""
    rng = np.random.default_rng(seed=int(abs(latent_vector.sum()) * 1e6) % (2**32))
    canvas = np.zeros((size, size, 3), dtype=np.float32) + 0.03

    num_blobs = rng.integers(6, 14)
    for _ in range(num_blobs):
        cx = float(rng.uniform(0.1, 0.9))
        cy = float(rng.uniform(0.1, 0.9))
        sigma = float(rng.uniform(0.04, 0.15)) * size
        # latent components determine color hue
        r = float(np.clip(0.3 + latent_vector[0] * 0.5, 0, 1))
        g = float(np.clip(0.1 + latent_vector[1] * 0.4, 0, 1))
        b = float(np.clip(0.8 - latent_vector[2] * 0.3, 0.2, 1))
        intensity = float(rng.uniform(0.4, 1.0))
        _gaussian_blob(canvas, cx, cy, sigma, np.array([r, g, b]) * intensity)

    canvas = np.clip(canvas, 0, 1)
    rgb = (canvas * 255).astype(np.uint8)
    return Image.fromarray(rgb, mode="RGB")


def generate_all_frames(latent_seq: np.ndarray) -> list:
    """Generate TEXTURE_FRAMES activation frames, return list of PIL Images."""
    ACT_FRAMES_DIR.mkdir(parents=True, exist_ok=True)
    images = []
    for i in range(TEXTURE_FRAMES):
        z = latent_seq[i % len(latent_seq)]
        img = make_activation_frame(z)
        path = ACT_FRAMES_DIR / f"act_frame_{i:03d}.png"
        img.save(path)
        images.append(img)
    return images


def make_spritesheet(images: list, output_path=None) -> Image.Image:
    """Assemble images into a grid spritesheet."""
    if output_path is None:
        output_path = TEXTURES_DIR / "activation_map_spritesheet.png"
    cols, rows = TEXTURE_GRID
    w, h = images[0].size
    sheet = Image.new("RGB", (cols * w, rows * h), (0, 0, 0))
    for idx, img in enumerate(images[:cols * rows]):
        col = idx % cols
        row = idx // cols
        sheet.paste(img, (col * w, row * h))
    sheet.save(output_path)
    return sheet


def save_base_texture(images: list) -> None:
    TEXTURES_DIR.mkdir(parents=True, exist_ok=True)
    images[0].save(TEXTURES_DIR / "activation_map_base.png")
