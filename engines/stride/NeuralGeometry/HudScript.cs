using System;
using Stride.Core.Mathematics;
using Stride.Engine;
using Stride.UI;
using Stride.UI.Controls;

namespace NeuralGeometry
{
    /// <summary>
    /// UI script that updates the HUD labels when the neural sphere advances a frame.
    /// Attach to a UIComponent entity in the Stride scene.
    /// </summary>
    public class HudScript : SyncScript
    {
        private TextBlock? _titleBlock;
        private TextBlock? _frameBlock;
        private TextBlock? _latentBlock;

        public override void Start()
        {
            var ui = Entity.Get<UIComponent>();
            if (ui?.Page?.RootElement == null) return;

            _titleBlock  = ui.Page.RootElement.FindName("TitleText")  as TextBlock;
            _frameBlock  = ui.Page.RootElement.FindName("FrameText")  as TextBlock;
            _latentBlock = ui.Page.RootElement.FindName("LatentText") as TextBlock;

            if (_titleBlock  != null) _titleBlock.Text  = "NEURAL GEOMETRY";
            if (_frameBlock  != null) _frameBlock.Text  = "Frame: 0 / 60";
            if (_latentBlock != null) _latentBlock.Text = "z = [0.00, 0.00, 0.00, 0.00]";
        }

        public override void Update() { }

        public void OnFrameChanged(int frameIdx, float[,] latentVecs)
        {
            if (_frameBlock != null)
                _frameBlock.Text = $"Frame: {frameIdx:D2} / 60";

            if (_latentBlock != null)
                _latentBlock.Text = string.Format(
                    "z = [{0:F2}, {1:F2}, {2:F2}, {3:F2}]",
                    latentVecs[frameIdx, 0], latentVecs[frameIdx, 1],
                    latentVecs[frameIdx, 2], latentVecs[frameIdx, 3]);
        }
    }
}
