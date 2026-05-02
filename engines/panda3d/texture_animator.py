from pathlib import Path
from panda3d.core import Texture

ASSETS = Path(__file__).parent.parent.parent / "shared_assets"


class TextureAnimator:
    def __init__(self, loader, mesh_nodepath, interval_s: float = 2.0):
        frames_dir = ASSETS / "textures" / "activation_frames"
        paths = sorted(frames_dir.glob("act_frame_*.png"))
        self.textures = [loader.loadTexture(str(p)) for p in paths]
        self.mesh_np = mesh_nodepath
        self.interval = interval_s
        self.elapsed = 0.0
        self.frame_idx = 0
        self._apply(0)

    def _apply(self, idx: int) -> None:
        self.mesh_np.setTexture(self.textures[idx], 1)

    def update(self, dt: float) -> None:
        self.elapsed += dt
        if self.elapsed >= self.interval:
            self.elapsed -= self.interval
            self.frame_idx = (self.frame_idx + 1) % len(self.textures)
            self._apply(self.frame_idx)
