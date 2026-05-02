from direct.gui.OnscreenText import OnscreenText
from panda3d.core import TextNode, LineSegs, NodePath
import numpy as np


class HUD:
    def __init__(self, render2d, aspect2d):
        self._r2d = render2d
        style = dict(fg=(1, 1, 1, 0.9), shadow=(0, 0, 0, 0.6),
                     shadowOffset=(0.003, 0.003), align=TextNode.ALeft, mayChange=True)

        self.title_text = OnscreenText(
            text="NEURAL GEOMETRY", pos=(-1.33, 0.92), scale=0.055,
            fg=(0.4, 0.8, 1.0, 1.0), shadow=(0, 0, 0, 0.7),
            shadowOffset=(0.003, 0.003), align=TextNode.ALeft,
        )
        self.frame_text = OnscreenText(
            text="Frame: 0 / 60", pos=(-1.33, 0.83), scale=0.042, **style,
        )
        self.latent_text = OnscreenText(
            text="z = [0.00, 0.00, 0.00, 0.00]", pos=(-1.33, 0.76), scale=0.038, **style,
        )
        self.infer_text = OnscreenText(
            text="Inference: 0.0 ms", pos=(-1.33, 0.70), scale=0.038, **style,
        )
        self.fps_text = OnscreenText(
            text="FPS: --", pos=(-1.33, 0.64), scale=0.038, **style,
        )

        # Bar chart node for latent vector visualization
        self._bar_root = aspect2d.attachNewNode("latent_bars")
        self._bar_root.setPos(-1.33, 0, 0.52)
        self._bars: list[NodePath] = []
        self._build_bar_chart()

        self._fps_acc = 0.0
        self._fps_count = 0

    def _build_bar_chart(self) -> None:
        colors = [(0.3, 0.6, 1.0, 1), (0.2, 0.9, 0.5, 1),
                  (1.0, 0.6, 0.2, 1), (0.9, 0.3, 0.8, 1)]
        self._bar_segs_list = []
        for i in range(4):
            segs = LineSegs(f"bar_{i}")
            segs.setThickness(4.0)
            segs.setColor(*colors[i])
            segs.moveTo(i * 0.07, 0, 0)
            segs.drawTo(i * 0.07, 0, 0.05)
            node = self._bar_root.attachNewNode(segs.create())
            self._bars.append((node, segs, i * 0.07, colors[i]))
        self._bar_segs_list = self._bars

    def update(self, frame_idx: int, latent: np.ndarray, infer_ms: float, dt: float) -> None:
        self._fps_acc += dt
        self._fps_count += 1
        if self._fps_acc >= 0.5:
            fps = self._fps_count / self._fps_acc
            self.fps_text.setText(f"FPS: {fps:.0f}")
            self._fps_acc = 0.0
            self._fps_count = 0

        self.frame_text.setText(f"Frame: {frame_idx:02d} / 60")
        z = latent
        self.latent_text.setText(
            f"z = [{z[0]:.2f}, {z[1]:.2f}, {z[2]:.2f}, {z[3]:.2f}]"
        )
        self.infer_text.setText(f"Inference: {infer_ms:.2f} ms")

        # Redraw bar chart
        for node, segs, x_offset, color in self._bars:
            node.removeNode()
        self._bars = []

        colors = [(0.3, 0.6, 1.0, 1), (0.2, 0.9, 0.5, 1),
                  (1.0, 0.6, 0.2, 1), (0.9, 0.3, 0.8, 1)]
        for i, (val, col) in enumerate(zip(latent, colors)):
            segs = LineSegs(f"bar_{i}")
            segs.setThickness(5.0)
            segs.setColor(*col)
            h = float(val) * 0.08   # map [-1,1] to [-0.08, 0.08]
            x = i * 0.07
            segs.moveTo(x, 0, 0)
            segs.drawTo(x, 0, h)
            node = self._bar_root.attachNewNode(segs.create())
            self._bars.append((node, segs, x, col))
