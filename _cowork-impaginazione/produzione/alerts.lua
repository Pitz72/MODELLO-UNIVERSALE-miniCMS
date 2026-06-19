-- Converte le GitHub alerts (Div .warning/.tip/.note/.important/.caution)
-- in chiamate Typst #admonition("tipo")[ corpo ].
local kinds = { warning=true, tip=true, note=true, important=true, caution=true }

function Div(el)
  for _, c in ipairs(el.classes) do
    if kinds[c] then
      local body = {}
      for _, b in ipairs(el.content) do
        local is_title = false
        if b.t == "Div" then
          for _, bc in ipairs(b.classes) do
            if bc == "title" then is_title = true end
          end
        end
        if not is_title then body[#body+1] = b end
      end
      local inner = pandoc.write(pandoc.Pandoc(body), 'typst')
      return pandoc.RawBlock('typst', '#admonition("'..c..'")[\n'..inner..'\n]')
    end
  end
end
