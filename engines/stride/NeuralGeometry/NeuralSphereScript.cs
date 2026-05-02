using System;
using System.IO;
using Stride.Core.Mathematics;
using Stride.Engine;
using Stride.Graphics;
using Stride.Rendering;

namespace NeuralGeometry
{
    /// <summary>
    /// SyncScript that loads .npy keyframes and updates the mesh vertex buffer each frame.
    /// Attach to a ModelComponent entity in the Stride scene.
    /// </summary>
    public class NeuralSphereScript : SyncScript
    {
        // Path relative to the executable — adjust if needed
        public string AssetsRoot { get; set; } = "../../../../shared_assets";

        private const int NumFrames   = 60;
        private const int NumVertices = 642;
        private const float AnimFps   = 30f;

        private float[,,] _displacements;  // [60, 642, 3]
        private float[,,] _colors;         // [60, 642, 4]
        private float[,]  _latentVecs;     // [60, 4]
        private float[,]  _baseVerts;      // [642, 3]  frame 0

        private float _animTime;
        private int   _frameIdx;
        private Mesh  _mesh;

        // HUD component reference (set in Stride GameStudio or via script)
        public HudScript? HudScript { get; set; }

        public override void Start()
        {
            var animDir  = Path.Combine(AssetsRoot, "animations");
            var meshDir  = Path.Combine(AssetsRoot, "meshes", "keyframes");

            _displacements = NpyLoader.Load3D(Path.Combine(animDir, "displacements.npy"), NumFrames, NumVertices, 3);
            _colors        = NpyLoader.Load3D(Path.Combine(animDir, "vertex_colors.npy"),  NumFrames, NumVertices, 4);
            _latentVecs    = NpyLoader.Load2D(Path.Combine(animDir, "latent_vectors.npy"),  NumFrames, 4);
            _baseVerts     = NpyLoader.Load2D(Path.Combine(meshDir, "frame_000.npy"),        NumVertices, 3);

            Console.WriteLine($"[NeuralSphereScript] Loaded {NumFrames} frames × {NumVertices} vertices");

            _mesh = BuildInitialMesh();
        }

        public override void Update()
        {
            _animTime += (float)Game.UpdateTime.Elapsed.TotalSeconds;
            int newFrame = (int)(_animTime * AnimFps) % NumFrames;

            if (newFrame != _frameIdx)
            {
                _frameIdx = newFrame;
                UpdateMeshGeometry(_frameIdx);

                HudScript?.OnFrameChanged(_frameIdx, _latentVecs);
            }

            HandleInput();
        }

        // ------------------------------------------------------------------ mesh

        private Mesh BuildInitialMesh()
        {
            // Load face topology from faces.npy
            var facesPath = Path.Combine(AssetsRoot, "meshes", "faces.npy");
            var facesFlat = NpyLoader.LoadFlat(facesPath);
            int numFaces  = facesFlat.Length / 3;

            // Build vertex buffer (Position + Normal + TexCoord)
            var vertexDecl = VertexDeclaration.Get<VertexPositionNormalTexture>();
            var vertices   = new VertexPositionNormalTexture[NumVertices];
            FillVertices(vertices, 0);

            var vb = Stride.Graphics.Buffer.Vertex.New(GraphicsDevice,
                        vertices, GraphicsResourceUsage.Dynamic);

            // Build index buffer
            var indices = new int[numFaces * 3];
            for (int i = 0; i < facesFlat.Length; i++)
                indices[i] = (int)facesFlat[i];
            var ib = Stride.Graphics.Buffer.Index.New(GraphicsDevice, indices);

            var meshDraw = new MeshDraw
            {
                PrimitiveType  = PrimitiveType.TriangleList,
                VertexBuffers  = new[] { new VertexBufferBinding(vb, vertexDecl, NumVertices) },
                IndexBuffer    = new IndexBufferBinding(ib, is32Bit: true, count: indices.Length),
                DrawCount      = indices.Length,
            };

            return new Mesh { Draw = meshDraw };
        }

        private void FillVertices(VertexPositionNormalTexture[] vertices, int fi)
        {
            for (int vi = 0; vi < NumVertices; vi++)
            {
                float x = _baseVerts[vi, 0] + _displacements[fi, vi, 0];
                float y = _baseVerts[vi, 1] + _displacements[fi, vi, 1];
                float z = _baseVerts[vi, 2] + _displacements[fi, vi, 2];

                float len = MathF.Sqrt(x*x + y*y + z*z);
                float nx  = len > 0 ? x/len : 0;
                float ny  = len > 0 ? y/len : 1;
                float nz  = len > 0 ? z/len : 0;

                float u = 0.5f + MathF.Atan2(z, x) / (2f * MathF.PI);
                float v = 0.5f - MathF.Asin(Math.Clamp(y / MathF.Max(len, 1e-6f), -1f, 1f)) / MathF.PI;

                vertices[vi] = new VertexPositionNormalTexture(
                    new Vector3(x, y, z),
                    new Vector3(nx, ny, nz),
                    new Vector2(u, v));
            }
        }

        private void UpdateMeshGeometry(int fi)
        {
            if (_mesh?.Draw.VertexBuffers == null) return;

            var vertices = new VertexPositionNormalTexture[NumVertices];
            FillVertices(vertices, fi);

            var vb = _mesh.Draw.VertexBuffers[0].Buffer;
            vb.SetData(Game.GraphicsContext.CommandList, vertices);
        }

        // ------------------------------------------------------------------ input

        private void HandleInput()
        {
            var input = Input;
            if (input.IsKeyPressed(Stride.Input.Keys.Escape))
                Game.Exit();
            if (input.IsKeyPressed(Stride.Input.Keys.R))
            {
                _animTime = 0f;
                _frameIdx = 0;
            }
        }
    }
}
