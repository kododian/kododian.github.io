-- format-numbers.lua
-- Automatically add thousands separators to numbers in paragraphs

function Str(el)
    local s = el.text
    -- Match integers of 5 or more digits, don't confuse with years 2025 etc.
    if s:match("^%d%d%d%d%d+$") then
      -- Reverse the string, insert commas every 3 digits, then reverse back
      local formatted = s:reverse():gsub("(%d%d%d)", "%1,"):reverse():gsub("^,", "")
      return pandoc.Str(formatted)
    end
    return el
end