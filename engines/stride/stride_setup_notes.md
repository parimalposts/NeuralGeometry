# Stride Setup Notes

## Platform Requirements
- **Windows or Linux** (Stride does not support macOS natively)
- .NET 6 SDK
- Visual Studio 2022 (Windows) or JetBrains Rider (cross-platform)
- Stride 4.2 — install via the **Stride Launcher**: https://stride3d.net/download/

## Quick Start
1. Install Stride Launcher and launch Stride GameStudio 4.2
2. Open `NeuralGeometry.sln` in Visual Studio 2022
3. Restore NuGet packages (right-click solution → Restore NuGet Packages)
4. Build the solution (F6)
5. Open `Assets/MainScene.sdscene` in Stride GameStudio
6. Press F5 to run

## NuGet Packages Required
See `NeuralGeometry.csproj`:
- `Stride.Engine 4.2.0.2188`
- `Stride.Games 4.2.0.2188`
- `Stride.Graphics 4.2.0.2188`
- `Stride.Rendering 4.2.0.2188`
- `Stride.Input 4.2.0.2188`

## Asset Path
The scripts expect `shared_assets/` at `../../../../shared_assets` relative to the
executable. If running from a different location, adjust the `AssetsRoot` property
on `NeuralSphereScript` and `TextureAnimatorScript` in the Stride GameStudio inspector.

## Key Scripts
| Script | Purpose |
|--------|---------|
| `NpyLoader.cs` | Parses `.npy` binary format in pure C# — no Python needed at runtime |
| `NeuralSphereScript.cs` | Loads all 60 keyframe arrays at startup, updates mesh vertex buffer each frame |
| `TextureAnimatorScript.cs` | Cycles activation textures from `shared_assets/textures/activation_frames/` |
| `HudScript.cs` | Updates UI TextBlock labels with frame index and latent vector |

## Demo Controls
| Key | Action |
|-----|--------|
| Escape | Quit |
| R | Reset animation to frame 0 |
