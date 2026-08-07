"""Build `<CLS> Probe` -- a WeakAura that WATCHES the client and logs what
CHANGED, so a mechanism question is settled in one in-game trip.

    python3 tools/build_probe.py runemaster
    python3 tools/build_probe.py pyromancer

Why this exists
---------------
Three versions of Runemaster's Elemental Mastery cue shipped and none fired,
because each rested on an assumption about how the server surfaces a mechanic.
None of that is knowable from documentation: the WeakAuras wiki documents a far
newer addon than this 3.3.5 backport, the client is patched, and the core is
custom. The only authority left is the client, in the moment the thing happens.

`/xxdump` takes a SNAPSHOT, which answers "what does the world look like".
That is the wrong question -- half of what it prints is up all the time and
drowns the two lines that matter. This takes a baseline and reports DELTAS, so
the event you are hunting produces a handful of lines and nothing else does.

It also assumes nothing about API signatures. `GetSpellInfo` returns nine
values on stock 3.3.5 and a spellId in slot 7 only from Cataclysm onward;
`build_dump.py` reads slot 7 as an id, which is a Cataclysm-shaped assumption
nobody has checked here. Section 0 prints the raw return list.

Usage
-----
    1. Import the string as its own aura (it draws nothing).
    2. Get into the state the question is about (spec, talent, target).
    3. Make the thing happen.
    4. /<prefix>probe  ->  copy the log.
"""
import os
import sys

import wabuild as B
from wacodec import LuaTable
from classes import build_path, get

SP = os.path.dirname(os.path.abspath(__file__))

# Per-class probe config. `watch_spells` is the set whose IsSpellKnown /
# GetSpellInfo resolution is polled; `actions` are the ids whose action-bar slot
# is followed. Keep these SMALL -- every entry is a line in the delta log.
PROBES = {
    "runemaster": {
        "prefix": "rm",
        "watch_spells": [
            ("Primordial Blast", 800732), ("Ignis", 712668),
            ("Hydros", 713002), ("Lithos", 712858), ("Stratus", 712404),
            ("Zenith", 712325), ("Zenith (2-charge)", 712389),
        ],
        "actions": [800732, 712668, 713002, 712858, 712404],
        "totems": False,
        "pet": False,
    },
    # Every open question from notes/requirements-pyromancer.md §6 that the
    # client can answer, in one trip.
    "pyromancer": {
        "prefix": "py",
        "watch_spells": [
            # §2 -- does the talent REPLACE Explode, and which do you have?
            ("Explode", 800792), ("Echo of Nozdormu", 802174),
            # §3 -- the Phoenix cluster
            ("Phoenix Egg", 707110), ("Phoenix Dive", 706854),
            ("Kael's Command", 680375), ("Phoenix Rebirth", 706867),
            ("Spirit of the Phoenix", 92126),
            # §0 -- is the castable Stoke real on this character?
            ("Stoke", 803952),
            # §1 -- pre-pull buffs the rotation names
            ("Draconic Aspect", 92128), ("Inner Flame", 301974),
            ("Draconic Invocation", 802119), ("Aspect's Blessing", 802168),
            ("Fired Up!", 704823), ("Flamecasting", 804300),
            # the 2026/07/31 rework -- 806736 is the PASSIVE; what lands on the
            # ally is an uncaptured spell, and 806742 is its expiry heal
            ("Inferno", 806736), ("Inferno Explosion", 806742),
        ],
        "actions": [800792, 802174, 706854, 680375, 707110],
        # §3 -- THE question. A 60s "summon at the target location" on 3.3.5 is
        # usually a TOTEM slot, which the fork has a native ["Totem"] prototype
        # for (GetTotemInfo, progressType="timed" -- a duration bar for free).
        # If it is a real pet instead, UnitExists("pet") answers.
        "totems": True,
        "pet": True,
    },
}


def build(slug):
    cfg = PROBES[slug]
    cls = get(slug)
    pfx = cfg["prefix"]

    spells = ", ".join('[%d] = "%s"' % (i, n) for n, i in cfg["watch_spells"])
    actions = ", ".join(str(i) for i in cfg["actions"])

    lua = """function()
    if %(FRAME)s then return end

    local WATCH = {%(SPELLS)s}
    local ACTIONS = {%(ACTIONS)s}

    local log, last = {}, nil
    local function say(s)
        log[table.getn(log) + 1] = s
        if table.getn(log) > 400 then table.remove(log, 1) end
    end

    -- 0. What this client's API actually returns, so nothing below is assumed.
    say("===== %(TITLE)s =====")
    local probe = nil
    for id in pairs(WATCH) do probe = probe or id end
    local r = { GetSpellInfo(probe) }
    local parts = {}
    for i = 1, 12 do parts[i] = tostring(r[i]) end
    say("GetSpellInfo(" .. tostring(probe) .. ") -> " .. table.concat(parts, " | "))
    say("api: IsSpellKnown=" .. tostring(IsSpellKnown ~= nil)
        .. " GetTotemInfo=" .. tostring(GetTotemInfo ~= nil)
        .. " GetSpellBookItemName=" .. tostring(GetSpellBookItemName ~= nil)
        .. " GetSpellName=" .. tostring(GetSpellName ~= nil)
        .. " FindSpellOverrideByID=" .. tostring(FindSpellOverrideByID ~= nil))
    say("-- watching. make it happen, then /%(PFX)sprobe --")

    local function snapshot()
        local s = {}

        -- every player buff: the catch-all, and how a hidden proc gets found
        for i = 1, 40 do
            local n, _, _, c, _, d, _, _, _, _, id = UnitBuff("player", i)
            if not n then break end
            s["buff:" .. n] = "id=" .. tostring(id) .. " dur=" .. tostring(d)
                .. " stacks=" .. tostring(c)
        end

        -- does each watched spell resolve / is it known
        for id, nm in pairs(WATCH) do
            s["resolves:" .. nm] = tostring(GetSpellInfo(id) ~= nil)
            if IsSpellKnown then
                s["known:" .. nm] = tostring(IsSpellKnown(id))
            end
        end

        -- which action slot holds a watched spell, and what it casts NOW
        for slot = 1, 120 do
            local kind, id = GetActionInfo(slot)
            if kind == "spell" and id then
                for i = 1, table.getn(ACTIONS) do
                    if id == ACTIONS[i] then
                        s["action:" .. slot] = "id=" .. tostring(id)
                            .. " name=" .. tostring(GetSpellInfo(id))
                    end
                end
            end
        end
%(TOTEMS)s%(PET)s
        -- power types, so a second resource ("Breath Charges") cannot hide
        for pt = 0, 6 do
            local cur = UnitPower and UnitPower("player", pt)
            local max = UnitPowerMax and UnitPowerMax("player", pt)
            if max and max > 0 then
                s["power:" .. pt] = tostring(cur) .. "/" .. tostring(max)
            end
        end

        return s
    end

    -- Report only what MOVED, so the event costs a handful of lines and
    -- everything that is simply always true costs none.
    local function diff(a, b)
        for k, v in pairs(b) do
            if a[k] ~= v then
                say(string.format("%%.1f  + %%s = %%s", GetTime() %% 1000, k, v))
            end
        end
        for k, v in pairs(a) do
            if b[k] == nil then
                say(string.format("%%.1f  - %%s (was %%s)", GetTime() %% 1000, k, v))
            end
        end
    end

    local f = CreateFrame("Frame", "%(FRAME)s", UIParent)
    f:SetWidth(680)
    f:SetHeight(500)
    f:SetPoint("CENTER", UIParent, "CENTER", 0, 0)
    f:SetFrameStrata("DIALOG")
    f:SetBackdrop({
        bgFile = "Interface\\\\DialogFrame\\\\UI-DialogBox-Background",
        edgeFile = "Interface\\\\DialogFrame\\\\UI-DialogBox-Border",
        tile = true, tileSize = 32, edgeSize = 32,
        insets = { left = 11, right = 12, top = 12, bottom = 11 },
    })
    f:SetMovable(true)
    f:EnableMouse(true)
    f:RegisterForDrag("LeftButton")
    f:SetScript("OnDragStart", function() f:StartMoving() end)
    f:SetScript("OnDragStop", function() f:StopMovingOrSizing() end)
    f:Hide()

    local title = f:CreateFontString(nil, "OVERLAY", "GameFontNormal")
    title:SetPoint("TOP", f, "TOP", 0, -16)
    title:SetText("%(TITLE)s - Ctrl+A, Ctrl+C, Esc to close")

    local sf = CreateFrame("ScrollFrame", "%(FRAME)sScroll", f,
                           "UIPanelScrollFrameTemplate")
    sf:SetPoint("TOPLEFT", f, "TOPLEFT", 18, -40)
    sf:SetPoint("BOTTOMRIGHT", f, "BOTTOMRIGHT", -38, 18)

    local eb = CreateFrame("EditBox", "%(FRAME)sEdit", sf)
    eb:SetMultiLine(true)
    eb:SetAutoFocus(false)
    eb:SetFontObject(ChatFontNormal)
    eb:SetWidth(610)
    eb:SetScript("OnEscapePressed", function() f:Hide() end)
    sf:SetScrollChild(eb)

    local acc = 0
    f:SetScript("OnUpdate", function(self, elapsed)
        acc = acc + (elapsed or 0.1)
        if acc < 0.1 then return end
        acc = 0
        local now = snapshot()
        if last then diff(last, now) end
        last = now
    end)

    SLASH_%(SLASH)s1 = "/%(PFX)sprobe"
    SlashCmdList["%(SLASH)s"] = function()
        eb:SetText(table.concat(log, "\\n"))
        f:Show()
        eb:SetFocus()
        eb:HighlightText()
    end

    DEFAULT_CHAT_FRAME:AddMessage("%(TITLE)s armed. /%(PFX)sprobe to read")
end""" % {
        "FRAME": f"{pfx.upper()}ProbeFrame",
        "SLASH": f"{pfx.upper()}PROBE",
        "PFX": pfx,
        "TITLE": f"{cls.name} Probe",
        "SPELLS": spells,
        "ACTIONS": actions,
        # A 3.3.5 ground summon is usually a TOTEM slot, not a pet. This is the
        # question the Phoenix turns on, so both are read rather than assumed.
        "TOTEMS": """
        if GetTotemInfo then
            for t = 1, 4 do
                local have, name, start, dur, icon = GetTotemInfo(t)
                if have and name and name ~= "" then
                    s["totem:" .. t] = tostring(name) .. " dur=" .. tostring(dur)
                end
            end
        end
""" if cfg["totems"] else "",
        "PET": """
        if UnitExists("pet") then
            s["pet"] = tostring(UnitName("pet"))
                .. " hp=" .. tostring(UnitHealthMax("pet"))
            for i = 1, 40 do
                local n = UnitBuff("pet", i)
                if not n then break end
                s["petbuff:" .. n] = "up"
            end
        end
""" if cfg["pet"] else "",
    }

    trigger = B.T({
        "type": "custom", "custom_type": "status", "check": "update",
        "custom": "function()\n    return false\nend",
        "unit": "player", "debuffType": "HELPFUL",
        "names": LuaTable(), "spellIds": LuaTable(),
        "auranames": LuaTable(), "auraspellids": LuaTable(),
        "subeventPrefix": "SPELL", "subeventSuffix": "_CAST_START",
    })

    a = B.icon(f"{cls.name} Probe", None, [trigger],
               "Interface\\Icons\\inv_misc_spyglass_02", x=0, y=0, size=32)
    a.pop("parent", None)
    a["actions"] = B.T({
        "init": B.T({"do_custom": True, "custom": lua}),
        "start": LuaTable(),
        "finish": LuaTable(),
    })
    return a


if __name__ == "__main__":
    slug = sys.argv[1] if len(sys.argv) > 1 else "runemaster"
    if slug not in PROBES:
        raise SystemExit(f"no probe config for {slug!r}. "
                         f"Known: {', '.join(sorted(PROBES))}")
    B.set_salt(f"{slug}-probe-2")
    a = build(slug)
    s = B.export_string(a, [])
    out = build_path("_diag", f"{slug}-probe")
    open(out, "w").write(s)
    print(f"{len(s)} chars -> {out}")
