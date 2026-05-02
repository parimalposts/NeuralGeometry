-- HUD text overlay: title, frame counter, latent vector

local M = {}

local _title_text
local _frame_text
local _latent_text

local TEXT_OPTS = {
    font   = native.systemFontBold,
    align  = "left",
}

function M.init()
    _title_text = display.newText(
        "NEURAL GEOMETRY", 20, 26, native.systemFontBold, 22)
    _title_text.anchorX = 0
    _title_text:setFillColor(0.4, 0.8, 1.0)

    _frame_text = display.newText(
        "Frame: 0 / 60", 20, 56, native.systemFont, 16)
    _frame_text.anchorX = 0
    _frame_text:setFillColor(1, 1, 1, 0.9)

    _latent_text = display.newText(
        "z = [0.00, 0.00, 0.00, 0.00]", 20, 80, native.systemFont, 14)
    _latent_text.anchorX = 0
    _latent_text:setFillColor(0.8, 0.9, 1.0, 0.9)
end

function M.update(frame_idx, latent)
    if _frame_text then
        _frame_text.text = string.format("Frame: %02d / 60", frame_idx)
    end
    if _latent_text and latent then
        _latent_text.text = string.format(
            "z = [%.2f, %.2f, %.2f, %.2f]",
            latent[1] or 0, latent[2] or 0,
            latent[3] or 0, latent[4] or 0)
    end
end

return M
