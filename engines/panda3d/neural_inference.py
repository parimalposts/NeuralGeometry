import time
import numpy as np

_LAYER_SIZES = [4, 64, 256, 642]


class NeuralInference:
    """Live numpy MLP decoder — mirrors pipeline/neural_sim.py for real-time use."""

    def __init__(self, seed: int = 42):
        rng = np.random.default_rng(seed)
        self.weights, self.biases = [], []
        for i in range(len(_LAYER_SIZES) - 1):
            fan_in = _LAYER_SIZES[i]
            w = rng.standard_normal((_LAYER_SIZES[i], _LAYER_SIZES[i + 1])) * np.sqrt(2.0 / fan_in)
            b = np.zeros(_LAYER_SIZES[i + 1])
            self.weights.append(w)
            self.biases.append(b)
        self.last_inference_ms = 0.0

    def infer(self, z: np.ndarray) -> np.ndarray:
        """z: (4,) → displacement magnitudes (642,) in [0, 1]. Times itself."""
        t0 = time.perf_counter()
        x = z.copy().astype(np.float64)
        for w, b in zip(self.weights[:-1], self.biases[:-1]):
            x = np.tanh(x @ w + b)
        x = x @ self.weights[-1] + self.biases[-1]
        result = (np.tanh(x) + 1.0) * 0.5
        self.last_inference_ms = (time.perf_counter() - t0) * 1000.0
        return result.astype(np.float32)
