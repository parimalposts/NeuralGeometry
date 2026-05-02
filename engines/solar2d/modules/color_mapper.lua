-- Maps a displacement magnitude [0,1] to RGB color (COLD=blue → HOT=orange)

local M = {}

local COLD = { 0.1, 0.3, 0.9 }
local HOT  = { 1.0, 0.4, 0.1 }

function M.map(t)
    t = math.max(0, math.min(1, t))
    return
        COLD[1] * (1-t) + HOT[1] * t,
        COLD[2] * (1-t) + HOT[2] * t,
        COLD[3] * (1-t) + HOT[3] * t
end

return M
