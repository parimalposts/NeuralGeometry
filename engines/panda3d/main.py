#!/usr/bin/env python3
"""
Neural Geometry — Panda3D demo (PRIMARY engine)
Usage: python main.py
Controls: F1 = toggle GLSL shader | R = reset | Escape = quit
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from engines.panda3d.neural_geometry_app import NeuralGeometryApp

app = NeuralGeometryApp()
app.run()
