import sys
import numpy as np
from pathlib import Path
from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    DirectionalLight, AmbientLight, PointLight,
    Vec4, Vec3, LColor, NodePath,
    Shader, ShaderAttrib,
)

ASSETS = Path(__file__).parent.parent.parent / "shared_assets"
ENGINE_DIR = Path(__file__).parent

from .mesh_animator    import MeshAnimator
from .texture_animator import TextureAnimator
from .neural_inference import NeuralInference
from .hud              import HUD


class NeuralGeometryApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        self.setWindowTitle("Neural Geometry — AI Research Visualization")
        self.setBackgroundColor(0.05, 0.05, 0.08, 1.0)
        self.disableMouse()

        self._setup_camera()
        self._setup_lights()
        self._setup_scene()
        self._setup_hud()
        self._setup_input()

        # Animation state
        self.latent_vecs = np.load(ASSETS / "animations" / "latent_vectors.npy")
        self.num_frames = len(self.latent_vecs)
        self.anim_time = 0.0
        self.frame_idx = 0
        self.fps_target = 30.0
        self.shader_on = False

        self.taskMgr.add(self._update, "update_task")

    # ------------------------------------------------------------------ setup

    def _setup_camera(self) -> None:
        self.camera.setPos(0, -8, 3)
        self.camera.lookAt(0, 0, 0)

    def _setup_lights(self) -> None:
        dl = DirectionalLight("sun")
        dl.setColor(Vec4(0.9, 0.85, 0.8, 1))
        dln = self.render.attachNewNode(dl)
        dln.setHpr(45, -45, 0)
        self.render.setLight(dln)

        al = AmbientLight("ambient")
        al.setColor(Vec4(0.15, 0.15, 0.25, 1))
        aln = self.render.attachNewNode(al)
        self.render.setLight(aln)

        pl = PointLight("fill")
        pl.setColor(Vec4(0.3, 0.4, 0.8, 1))
        pln = self.render.attachNewNode(pl)
        pln.setPos(-5, 3, 4)
        self.render.setLight(pln)

    def _setup_scene(self) -> None:
        self.mesh_anim = MeshAnimator(self.loader)
        self.mesh_np = self.mesh_anim.nodepath
        self.mesh_np.reparentTo(self.render)
        self.mesh_np.setScale(1.0)

        self.tex_anim = TextureAnimator(self.loader, self.mesh_np, interval_s=2.0)
        self.inference = NeuralInference(seed=42)

    def _setup_hud(self) -> None:
        self.hud = HUD(self.render2d, self.aspect2d)

    def _setup_input(self) -> None:
        self.accept("f1",     self._toggle_shader)
        self.accept("escape", sys.exit)
        self.accept("r",      self._reset_animation)

    # ------------------------------------------------------------------ loop

    def _update(self, task):
        dt = globalClock.getDt()
        self.anim_time += dt
        self.frame_idx = int(self.anim_time * self.fps_target) % self.num_frames

        # Update geometry
        self.mesh_anim.update(self.frame_idx)

        # Update texture
        self.tex_anim.update(dt)

        # Live inference (for HUD display)
        z = self.latent_vecs[self.frame_idx]
        self.inference.infer(z)

        # HUD
        self.hud.update(self.frame_idx, z, self.inference.last_inference_ms, dt)

        return task.cont

    # ------------------------------------------------------------------ actions

    def _toggle_shader(self) -> None:
        vert = ENGINE_DIR / "shaders" / "neural_vert.glsl"
        frag = ENGINE_DIR / "shaders" / "neural_frag.glsl"
        if not self.shader_on and vert.exists() and frag.exists():
            shader = Shader.load(Shader.SL_GLSL,
                                 vertex=str(vert), fragment=str(frag))
            self.mesh_np.setShader(shader)
            self.shader_on = True
        else:
            self.mesh_np.setShaderOff()
            self.shader_on = False

    def _reset_animation(self) -> None:
        self.anim_time = 0.0
        self.frame_idx = 0
