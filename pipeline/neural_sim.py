"""
Simulated VAE decoder — pure numpy, no torch/jax required.
Swap NeuralDecoder.decode() with real model inference to use actual ML outputs.
"""

import numpy as np
from .config import LATENT_DIM, NUM_FRAMES

_LAYER_SIZES = [LATENT_DIM, 64, 256, 642]


class NeuralDecoder:
    def __init__(self, seed: int = 42):
        rng = np.random.default_rng(seed)
        self.weights = []
        self.biases = []
        sizes = _LAYER_SIZES
        for i in range(len(sizes) - 1):
            fan_in = sizes[i]
            w = rng.standard_normal((fan_in, sizes[i + 1])) * np.sqrt(2.0 / fan_in)
            b = np.zeros(sizes[i + 1])
            self.weights.append(w)
            self.biases.append(b)

    def decode(self, z: np.ndarray) -> np.ndarray:
        """z: (4,) → displacement magnitudes: (642,) in [0, 1]"""
        x = z.copy()
        for w, b in zip(self.weights[:-1], self.biases[:-1]):
            x = np.tanh(x @ w + b)
        x = x @ self.weights[-1] + self.biases[-1]
        return (np.tanh(x) + 1.0) * 0.5   # map to [0, 1]

    def decode_batch(self, latent_seq: np.ndarray) -> np.ndarray:
        """latent_seq: (N, 4) → (N, 642)"""
        return np.stack([self.decode(z) for z in latent_seq])


def traverse_latent(steps: int = NUM_FRAMES) -> np.ndarray:
    """Return (steps, 4) Lissajous curve through latent space."""
    t = np.linspace(0, 2 * np.pi, steps, endpoint=False)
    return np.stack([
        np.sin(t),
        np.sin(2 * t + np.pi / 4),
        np.sin(3 * t),
        np.cos(t),
    ], axis=1).astype(np.float32)
