"""Build `RM Dump` -- a WeakAura that dumps ground-truth spell/aura data into a
selectable copy box.

Two constraints drove this design:
  * A WoW macro (and the chat edit box) caps at 255 characters, so the script
    ships as an aura -- WeakAuras runs `actions.init.custom` once on load with
    no length limit.
  * `/chatlog` only records real CHAT_MSG_* events. Text written with
    DEFAULT_CHAT_FRAME:AddMessage never reaches WoWChatLog.txt, so printing to
    chat produces an empty log file. The dump therefore goes into a scrollable
    EditBox that can be selected and copied.

Re-run with /rmdump, or /reload.
"""
import os

import wabuild as B
from wacodec import LuaTable
from classes import build_path

SP = os.path.dirname(os.path.abspath(__file__))

TRACKED = [
    "Runeblade", "Smolder", "Fracture", "Hoarfrost", "Hurricane",
    "Primordial Blast", "Elemental Burst", "Glyphic Ruin", "Thaumaturgy",
    "Runic Obliteration", "Fist of the Ancients", "Runic Brand",
    "Runic Explosion", "Zenith", "Power Engraving", "Granite Resolve",
    "Warding Rune", "Phase Out", "Ley Lock", "Speed Rune", "Runic Tempest",
    "Fists of Power", "Genesis", "Guarding Rune", "Ley Power", "Wild Steam",
    "Turbulence", "Primordial Fury", "Warpdagger", "Echo Rune", "Magebreaker",
    "Manuscription", "Silencing Rune", "Frigid Blast", "Glyphic Overload",
    "Eye of the Beholder", "Runeshroud", "Arcane Blade", "Fire Blade",
    "Frost Blade", "Runecarve",
]


def lua_list(items):
    return "{" + ", ".join(f'"{i}"' for i in items) + "}"


DUMP_LUA = f"""function()
    local out = {{}}
    local function say(s) out[table.getn(out) + 1] = s end

    say("===== RM DUMP =====")

    -- 1. Which names the WeakAura tracks actually resolve, and which collide.
    say("-- 1. TRACKED NAMES --")
    local tracked = {lua_list(TRACKED)}
    local seen = {{}}
    for _, n in ipairs(tracked) do
        local nm, _, icon, _, _, _, id = GetSpellInfo(n)
        if nm then
            local dup = seen[tostring(id)]
            say("OK|" .. n .. "|id=" .. tostring(id) .. "|" .. tostring(icon)
                .. (dup and ("|DUPLICATE_OF=" .. dup) or ""))
            seen[tostring(id)] = n
        else
            say("MISS|" .. n)
        end
    end

    -- 2. Full spellbook. This is the ground truth: every real name and rank.
    say("-- 2. SPELLBOOK --")
    local i = 1
    while true do
        local n, rank = GetSpellBookItemName(i, "spell")
        if not n then break end
        local _, _, _, _, _, _, id = GetSpellInfo(n)
        say(i .. "|" .. n .. "|" .. tostring(rank) .. "|" .. tostring(id))
        i = i + 1
    end

    -- 3. Player buffs -- run with your tattoo, engraving and procs up.
    say("-- 3. PLAYER BUFFS --")
    for j = 1, 40 do
        local n, _, _, c, _, d, e, _, _, _, id = UnitBuff("player", j)
        if not n then break end
        say(n .. "|stacks=" .. tostring(c) .. "|dur=" .. tostring(d)
            .. "|id=" .. tostring(id))
    end

    -- 4. Target debuffs -- run with your DoTs ticking on a dummy.
    say("-- 4. TARGET DEBUFFS --")
    for j = 1, 40 do
        local n, _, _, c, _, d, e, src, _, _, id = UnitDebuff("target", j)
        if not n then break end
        say(n .. "|stacks=" .. tostring(c) .. "|dur=" .. tostring(d)
            .. "|src=" .. tostring(src) .. "|id=" .. tostring(id))
    end

    -- 5. Weapon engravings surface as temporary weapon enchants.
    say("-- 5. WEAPON ENCHANTS --")
    local mh, mhExp, mhCh, oh, ohExp, ohCh = GetWeaponEnchantInfo()
    say("MainHand=" .. tostring(mh) .. "|expires=" .. tostring(mhExp))
    say("OffHand=" .. tostring(oh) .. "|expires=" .. tostring(ohExp))

    say("===== END =====")

    local text = table.concat(out, "\\n")

    if not RMDumpFrame then
        local f = CreateFrame("Frame", "RMDumpFrame", UIParent)
        f:SetWidth(640)
        f:SetHeight(480)
        f:SetPoint("CENTER", UIParent, "CENTER", 0, 0)
        f:SetFrameStrata("DIALOG")
        f:SetBackdrop({{
            bgFile = "Interface\\\\DialogFrame\\\\UI-DialogBox-Background",
            edgeFile = "Interface\\\\DialogFrame\\\\UI-DialogBox-Border",
            tile = true, tileSize = 32, edgeSize = 32,
            insets = {{ left = 11, right = 12, top = 12, bottom = 11 }},
        }})
        f:SetMovable(true)
        f:EnableMouse(true)
        f:RegisterForDrag("LeftButton")
        f:SetScript("OnDragStart", function() f:StartMoving() end)
        f:SetScript("OnDragStop", function() f:StopMovingOrSizing() end)

        local title = f:CreateFontString(nil, "OVERLAY", "GameFontNormal")
        title:SetPoint("TOP", f, "TOP", 0, -16)
        title:SetText("RM Dump - Ctrl+A then Ctrl+C, Esc to close")

        local sf = CreateFrame("ScrollFrame", "RMDumpScroll", f,
                               "UIPanelScrollFrameTemplate")
        sf:SetPoint("TOPLEFT", f, "TOPLEFT", 18, -40)
        sf:SetPoint("BOTTOMRIGHT", f, "BOTTOMRIGHT", -38, 18)

        local eb = CreateFrame("EditBox", "RMDumpEdit", sf)
        eb:SetMultiLine(true)
        eb:SetAutoFocus(false)
        eb:SetFontObject(ChatFontNormal)
        eb:SetWidth(570)
        eb:SetScript("OnEscapePressed", function() f:Hide() end)
        sf:SetScrollChild(eb)
        f.eb = eb

        SLASH_RMDUMP1 = "/rmdump"
        SlashCmdList["RMDUMP"] = function()
            f:Show()
            f.eb:SetFocus()
            f.eb:HighlightText()
        end
    end

    RMDumpFrame.eb:SetText(text)
    RMDumpFrame:Show()
    RMDumpFrame.eb:SetFocus()
    RMDumpFrame.eb:HighlightText()

    DEFAULT_CHAT_FRAME:AddMessage("RM Dump ready - /rmdump to reopen")
end"""

trigger = B.T({
    "type": "custom", "custom_type": "status", "check": "event",
    "events": "PLAYER_ENTERING_WORLD",
    "custom": "function()\n    return false\nend",
    "unit": "player", "debuffType": "HELPFUL",
    "names": LuaTable(), "spellIds": LuaTable(),
    "auranames": LuaTable(), "auraspellids": LuaTable(),
    "subeventPrefix": "SPELL", "subeventSuffix": "_CAST_START",
})

a = B.icon("RM Dump", None, [trigger],
           "Interface\\Icons\\inv_misc_note_01", x=0, y=0, size=32)
a.pop("parent", None)
a["actions"] = B.T({
    "init": B.T({"do_custom": True, "custom": DUMP_LUA}),
    "start": LuaTable(),
    "finish": LuaTable(),
})

if __name__ == "__main__":
    s = B.export_string(a, [])
    out = build_path("_diag", "rm-dump")
    open(out, "w").write(s)
    print(f"{len(s)} chars -> {out}")
