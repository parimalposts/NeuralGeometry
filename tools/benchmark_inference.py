#!/usr/bin/env python3
"""Measures numpy VAE decoder inference speed."""
import sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pipeline.neural_sim import NeuralDecoder, traverse_latent
import numpy as np

decoder = NeuralDecoder(seed=42)
latent  = traverse_latent()

# Warm-up
for z in latent:
    decoder.decode(z)

# Benchmark
N = 1000
t0 = time.perf_counter()
for _ in range(N):
    for z in latent:
        decoder.decode(z)
elapsed = time.perf_counter() - t0

per_call_us = elapsed / (N * len(latent)) * 1e6
per_call_ms = per_call_us / 1000.0

print(f"Benchmark: {N * len(latent)} inference calls in {elapsed:.2f}s")
print(f"  Per call: {per_call_us:.1f} µs ({per_call_ms:.3f} ms)")
print(f"  Max sustainable FPS at 1 inference/frame: {1.0/per_call_ms*1000:.0f}")
