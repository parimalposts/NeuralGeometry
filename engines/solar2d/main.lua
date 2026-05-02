-- Neural Geometry — Solar2D entry point
-- Controls: R = reset | Escape = quit

local NR  = require("modules.neural_renderer")
local HUD = require("modules.hud_overlay")

-- Track time for delta calculation
local last_time = 0

-- ------------------------------------------------------------------ init

local function init()
    display.setStatusBar(display.HiddenStatusBar)
    display.setDefault("background", 0.05, 0.05, 0.08)

    NR.init()
    HUD.init()

    print("[NeuralGeometry] Solar2D demo initialized.")
    print("  Press R to reset, Escape to quit.")
end

-- ------------------------------------------------------------------ frame loop

local function on_enter_frame(event)
    local dt = event.time - last_time
    last_time = event.time

    local fd = NR.update(dt)
    if fd then
        HUD.update(fd.frame, fd.latent)
    end
end

-- ------------------------------------------------------------------ input

local function on_key(event)
    if event.phase == "down" then
        if event.keyName == "escape" then
            native.requestExit()
        end
    end
end

-- ------------------------------------------------------------------ bootstrap

init()
Runtime:addEventListener("enterFrame", on_enter_frame)
Runtime:addEventListener("key",        on_key)
