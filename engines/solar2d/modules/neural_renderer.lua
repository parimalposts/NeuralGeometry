-- Neural Geometry — Solar2D renderer
-- Draws: animated activation background + morphing constellation of projected vertices

local json        = require("json")
local projector   = require("modules.mesh_projector")
local color_map   = require("modules.color_mapper")

local M = {}

-- Config
local ASSETS_BASE = "../../shared_assets/"
local DOT_RADIUS  = 5
local LINE_WIDTH  = 1.5
local SPRITE_FPS  = 8      -- activation texture frame rate
local FPS         = 30     -- animation frame rate

-- State
local manifest    = nil
local dots        = {}
local lines       = {}
local bg_sprite   = nil
local sheet       = nil
local frame_idx   = 0
local elapsed     = 0.0
local sprite_elapsed = 0.0
local sprite_frame   = 0
local sprite_interval = 1.0 / SPRITE_FPS

-- ------------------------------------------------------------------ load

local function load_manifest()
    -- Solar2D can read files from the project or system.pathForFile
    local path = system.pathForFile(
        ASSETS_BASE .. "metadata/solar2d_metadata.json",
        system.ResourceDirectory)
    if not path then
        -- Try relative path from project root in simulator
        path = ASSETS_BASE .. "metadata/solar2d_metadata.json"
    end

    local file = io.open(path, "r")
    if not file then
        print("[neural_renderer] ERROR: Cannot open solar2d_metadata.json")
        print("  Expected at: " .. tostring(path))
        return nil
    end
    local content = file:read("*a")
    file:close()
    return json.decode(content)
end


local function load_background()
    local sheet_path = ASSETS_BASE .. "textures/activation_map_spritesheet.png"
    local options = {
        width        = 512,
        height       = 512,
        numFrames    = 64,
        sheetContentWidth  = 4096,
        sheetContentHeight = 4096,
    }
    local ok, s = pcall(graphics.newImageSheet, sheet_path, options)
    if not ok then
        print("[neural_renderer] WARNING: Could not load spritesheet: " .. tostring(s))
        return nil, nil
    end

    local seq = { { name = "activation", start = 1, count = 64, time = 125, loopCount = 0 } }
    local sprite = display.newSprite(s, seq)
    if sprite then
        sprite.x = display.contentCenterX
        sprite.y = display.contentCenterY
        -- Scale to fill the screen
        local sw = display.contentWidth  / 512
        local sh = display.contentHeight / 512
        sprite.xScale = math.max(sw, sh) * 1.0
        sprite.yScale = math.max(sw, sh) * 1.0
        sprite.alpha  = 0.35   -- dim background
        sprite:play()
    end
    return s, sprite
end

-- ------------------------------------------------------------------ drawing

local function create_dots(n)
    for i = 1, n do
        local d = display.newCircle(display.contentCenterX, display.contentCenterY, DOT_RADIUS)
        d:setFillColor(0.3, 0.6, 1.0)
        d.strokeWidth = 0
        dots[i] = d
    end
end

local function create_lines(edges, n_edges)
    for i = 1, n_edges do
        local ln = display.newLine(0, 0, 10, 10)
        ln:setStrokeColor(0.3, 0.6, 1.0, 0.5)
        ln.strokeWidth = LINE_WIDTH
        lines[i] = ln
    end
end

local function update_frame(fd)
    local verts  = fd.vertices
    local edges  = fd.edges or {}
    local n      = math.min(#verts, #dots)

    for i = 1, n do
        local v  = verts[i]
        local pt = projector.project(v)
        dots[i].x = pt.x
        dots[i].y = pt.y

        -- Scale dot by magnitude
        local s = 0.6 + (v.mag or 0.5) * 1.4
        dots[i].xScale = s
        dots[i].yScale = s

        -- Color
        local r = v.r or 0.3
        local g = v.g or 0.6
        local b = v.b or 1.0
        dots[i]:setFillColor(r, g, b, 0.9)
    end

    -- Update edge lines
    for i, e in ipairs(edges) do
        if lines[i] and e[1] and e[2] then
            local vi1 = e[1] + 1  -- Lua 1-indexed
            local vi2 = e[2] + 1
            if verts[vi1] and verts[vi2] then
                local p1 = projector.project(verts[vi1])
                local p2 = projector.project(verts[vi2])
                local ln = lines[i]
                -- Solar2D lines are immutable after creation; remove and recreate
                ln:removeSelf()
                local new_ln = display.newLine(p1.x, p1.y, p2.x, p2.y)
                new_ln:setStrokeColor(
                    (verts[vi1].r or 0.3) * 0.7,
                    (verts[vi1].g or 0.6) * 0.7,
                    (verts[vi1].b or 1.0) * 0.7,
                    0.4)
                new_ln.strokeWidth = LINE_WIDTH
                lines[i] = new_ln
            end
        end
    end
end

-- ------------------------------------------------------------------ public

function M.init()
    manifest = load_manifest()
    if not manifest then return end

    -- Background
    sheet, bg_sprite = load_background()

    -- Get first frame to determine layout
    local first = manifest.frames[1]
    create_dots(#first.vertices)
    if first.edges then
        create_lines(first.edges, #first.edges)
    end

    update_frame(first)
end

function M.update(time_ms)
    if not manifest then return end

    local dt = time_ms / 1000.0
    elapsed = elapsed + dt

    -- Hack: Solar2D passes absolute time, track delta ourselves
    -- Actually we get called from enterFrame so dt is just since last frame (~0.033s at 30fps)
    -- Re-derive from elapsed
    local new_idx = math.floor(elapsed * FPS) % manifest.num_frames + 1
    if new_idx ~= frame_idx then
        frame_idx = new_idx
        update_frame(manifest.frames[frame_idx])
        return manifest.frames[frame_idx]
    end
    return nil
end

return M
