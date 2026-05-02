-- Orthographic projection of 3D vertex positions into Solar2D screen coordinates.
-- Camera looks along -Z; project XY plane to screen.

local M = {}

local CX = display.contentCenterX or 640
local CY = display.contentCenterY or 360
local SCALE = 240   -- world units → pixels

function M.project(v)
    -- v.x, v.y are in [-1.35, 1.35] range (icosphere radius ~1 + max displacement 0.35)
    return {
        x = CX + v.x * SCALE,
        y = CY - v.y * SCALE,   -- flip Y (screen Y grows downward)
    }
end

function M.get_top_vertices(vertices, n)
    -- vertices: array of {x,y,mag,r,g,b} already pre-sorted by pipeline
    local result = {}
    local count = math.min(n, #vertices)
    for i = 1, count do
        result[i] = vertices[i]
    end
    return result
end

return M
