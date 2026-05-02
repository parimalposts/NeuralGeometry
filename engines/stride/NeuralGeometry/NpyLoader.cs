using System;
using System.IO;
using System.Text;
using System.Text.RegularExpressions;

namespace NeuralGeometry
{
    /// <summary>
    /// Parses NumPy .npy binary files (version 1.0 and 2.0) containing float32 arrays.
    /// Supports 1-D, 2-D, and 3-D arrays.
    /// </summary>
    public static class NpyLoader
    {
        private static readonly byte[] Magic = { 0x93, (byte)'N', (byte)'U', (byte)'M', (byte)'P', (byte)'Y' };

        /// <summary>Loads a flat float array from a .npy file.</summary>
        public static float[] LoadFlat(string path)
        {
            using var fs = new FileStream(path, FileMode.Open, FileAccess.Read);
            using var reader = new BinaryReader(fs, Encoding.ASCII, leaveOpen: false);

            // Validate magic
            var magic = reader.ReadBytes(6);
            for (int i = 0; i < 6; i++)
                if (magic[i] != Magic[i])
                    throw new InvalidDataException($"Not a .npy file: {path}");

            byte major = reader.ReadByte();
            byte minor = reader.ReadByte();

            int headerLen;
            if (major == 1)
                headerLen = reader.ReadByte() | (reader.ReadByte() << 8);
            else
                headerLen = reader.ReadInt32();  // version 2.0

            byte[] headerBytes = reader.ReadBytes(headerLen);
            string header = Encoding.ASCII.GetString(headerBytes);

            // Verify float32 little-endian
            if (!header.Contains("float32") && !header.Contains("<f4") && !header.Contains("=f4"))
                throw new NotSupportedException($"Only float32 .npy files are supported. Header: {header}");

            // Count total floats from remaining bytes
            long dataStart = fs.Position;
            long dataBytes = fs.Length - dataStart;
            int count = (int)(dataBytes / 4);

            var result = new float[count];
            for (int i = 0; i < count; i++)
                result[i] = reader.ReadSingle();   // little-endian float32

            return result;
        }

        /// <summary>Loads a 2-D float array shaped (rows, cols).</summary>
        public static float[,] Load2D(string path, int rows, int cols)
        {
            float[] flat = LoadFlat(path);
            if (flat.Length < rows * cols)
                throw new InvalidDataException(
                    $"File has {flat.Length} values; expected {rows}×{cols}={rows * cols}");

            var result = new float[rows, cols];
            Buffer.BlockCopy(flat, 0, result, 0, rows * cols * sizeof(float));
            return result;
        }

        /// <summary>Loads a 3-D float array shaped (d0, d1, d2).</summary>
        public static float[,,] Load3D(string path, int d0, int d1, int d2)
        {
            float[] flat = LoadFlat(path);
            if (flat.Length < d0 * d1 * d2)
                throw new InvalidDataException(
                    $"File has {flat.Length} values; expected {d0}×{d1}×{d2}={d0 * d1 * d2}");

            var result = new float[d0, d1, d2];
            Buffer.BlockCopy(flat, 0, result, 0, d0 * d1 * d2 * sizeof(float));
            return result;
        }
    }
}
