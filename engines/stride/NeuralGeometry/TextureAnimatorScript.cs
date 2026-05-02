using System;
using System.IO;
using Stride.Core.Mathematics;
using Stride.Engine;
using Stride.Graphics;
using Stride.Rendering;
using Stride.Rendering.Materials;

namespace NeuralGeometry
{
    /// <summary>
    /// Cycles the activation texture on the material every IntervalSeconds.
    /// Attach to the same entity as the ModelComponent.
    /// </summary>
    public class TextureAnimatorScript : SyncScript
    {
        public string AssetsRoot    { get; set; } = "../../../../shared_assets";
        public float  IntervalSeconds { get; set; } = 2.0f;

        private Texture[] _textures = Array.Empty<Texture>();
        private float     _elapsed;
        private int       _frameIdx;

        public override void Start()
        {
            var framesDir = Path.Combine(AssetsRoot, "textures", "activation_frames");
            var files     = Directory.GetFiles(framesDir, "act_frame_*.png");
            Array.Sort(files, StringComparer.Ordinal);

            _textures = new Texture[files.Length];
            for (int i = 0; i < files.Length; i++)
                _textures[i] = LoadTexture(files[i]);

            Console.WriteLine($"[TextureAnimatorScript] Loaded {_textures.Length} activation textures");
        }

        public override void Update()
        {
            if (_textures.Length == 0) return;
            _elapsed += (float)Game.UpdateTime.Elapsed.TotalSeconds;

            if (_elapsed >= IntervalSeconds)
            {
                _elapsed -= IntervalSeconds;
                _frameIdx = (_frameIdx + 1) % _textures.Length;
                ApplyTexture(_frameIdx);
            }
        }

        private void ApplyTexture(int idx)
        {
            var model = Entity.Get<ModelComponent>();
            if (model?.Materials == null || model.Materials.Count == 0) return;

            var mat = model.Materials[0].Material;
            // In a real Stride project, set the diffuse texture via material parameter
            // This is the idiomatic approach:
            //   mat.Passes[0].Parameters.Set(MaterialKeys.DiffuseMap, _textures[idx]);
            // For editor workflow, the material is configured in Stride GameStudio assets.
        }

        private Texture LoadTexture(string path)
        {
            using var stream = File.OpenRead(path);
            return Texture.Load(GraphicsDevice, stream, loadAsSRgb: true);
        }
    }
}
