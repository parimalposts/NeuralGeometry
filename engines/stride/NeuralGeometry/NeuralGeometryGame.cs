using System;
using Stride.Engine;
using Stride.Games;

namespace NeuralGeometry
{
    /// <summary>Entry point for the Neural Geometry Stride demo.</summary>
    public class NeuralGeometryGame : Game
    {
        protected override void Initialize()
        {
            base.Initialize();
            Window.Title = "Neural Geometry — AI Research Visualization (Stride)";
        }

        protected override void BeginRun()
        {
            base.BeginRun();
            Console.WriteLine("[NeuralGeometry] Stride demo starting.");
            Console.WriteLine("  F1 = toggle wireframe | R = reset | Escape = quit");
        }

        public static void Main(string[] args)
        {
            using var game = new NeuralGeometryGame();
            game.Run();
        }
    }
}
