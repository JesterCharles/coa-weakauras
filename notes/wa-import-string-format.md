---
title: WeakAuras !WA:2! import string format (Ascension CoA)
date: 2026-07-27
type: note
status: budding
tags: [weakauras, wow, ascension, conquest-of-azeroth, libserialize, libdeflate, reverse-engineering]
sources:
  - https://github.com/rossnichols/LibSerialize
  - https://github.com/SafeteeWoW/LibDeflate
---

# WeakAuras `!WA:2!` import string format

Verified end-to-end on 2026-07-27 against four live Ascension Conquest of Azeroth
WeakAuras (Templar Pack, 2x Runemaster, Chronomancer). Round-trip decode → re-encode →
decode is **structurally identical** for all four, with output within 0.2% of original size.

Working Python implementation: `../tools/wacodec.py`.

## Pipeline

```
lua table  --LibSerialize v1-->  bytes  --raw DEFLATE-->  bytes  --EncodeForPrint-->  "!WA:2!" .. text
```

Decoding is the exact inverse. `zlib` with `wbits=-15` is byte-compatible with
LibDeflate's `CompressDeflate` / `DecompressDeflate`.

## Layer 1 — LibDeflate `EncodeForPrint`

6-bit alphabet, **index order matters** and is *not* standard base64:

```
abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ 0123456789 ( )
```

Packing is **little-endian**: 3 bytes → 24-bit integer `b0 + b1*256 + b2*65536`,
emitted as 4 chars taking 6 bits at a time from the **least** significant end.
Tail bytes accumulate into a bit cache and flush 6 bits at a time, low bits first.

Getting this wrong is the main trap — a standard base64 alphabet, or MSB-first bit
order, produces bytes that fail deflate with `invalid distance too far back`.

## Layer 2 — LibSerialize v1

First byte of the inflated payload is the serialization version (`0x01`).
Then a stream of objects. Every object is a **type byte** plus payload.

Type byte dispatch, checked in this order:

| Pattern | Meaning |
|---|---|
| `NNNN NNN1` | 7-bit non-negative int, value = `b >> 1` |
| `CCCC TT10` | 2-bit type index + 4-bit count, then payload |
| `NNNN S100` | low 4 bits of a 12-bit int + sign bit; **next byte holds the upper bits** |
| `TTTT T000` | 5-bit type index, then payload (incl. counts) |

Embedded type indices (the `TT` field): `0=STRING`, `1=TABLE`(map), `2=ARRAY`, `3=MIXED`.
For `MIXED` the 4-bit count packs two 2-bit counts that are each **one less** than the
true count: `arrayCount = (c % 4) + 1`, `mapCount = (c // 4) + 1`.

Full 5-bit type index table:

```
0  NIL
1-2   NUM_16_POS / NEG      (2-byte)
3-4   NUM_24_POS / NEG      (3-byte)
5-6   NUM_32_POS / NEG      (4-byte)
7-8   NUM_64_POS / NEG      (7-byte)
9     NUM_FLOAT             (8 bytes, IEEE754 big-endian)
10-11 NUM_FLOATSTR / NEG    (len byte + decimal string)
12-13 BOOL_T / BOOL_F
14-16 STR_8 / STR_16 / STR_24
17-19 TABLE_8 / _16 / _24   (map: count, then key/value pairs)
20-22 ARRAY_8 / _16 / _24   (count, then values)
23-25 MIXED_8 / _16 / _24   (arrayCount, mapCount, then values, then pairs)
26-28 STRINGREF_8 / _16 / _24
29-31 TABLEREF_8 / _16 / _24
```

**All multi-byte integers are big-endian.** (The 12-bit embedded-number form is the
exception: its two bytes are written low-then-high.)

### Reference tracking — the subtle part

Strings **longer than 2 bytes** and *all* tables are appended to per-type reference
lists as they are encountered. A repeat occurrence is emitted as a 1-based index into
that list instead of the value. Encoder and decoder must append in exactly the same
order or the streams desynchronise. Tables are added to the reference list **before**
their contents are serialized, which is what makes recursive self-reference work.

## Layer 3 — the WeakAuras payload

Top-level table:

| Key | Meaning |
|---|---|
| `m` | mode — `"d"` for a display export |
| `d` | the root aura table (a group, for packs) |
| `c` | array of child aura tables (flat, not nested) |
| `s` | WeakAuras version string — Ascension CoA reports `"5.21.2 Beta"` |
| `v` | export format version — `2000` on current auras, `1421` on older ones |
| `wagoID` | optional Wago slug |

Children are stored **flat** in `c`; nesting is expressed by each child's `parent`
field and the parent group's `controlledChildren` array.

## Trigger types confirmed present in Ascension's WA fork

Ascension runs a fork reporting `5.21.2 Beta`, and it supports the **modern generic
trigger schema** (`trigger.type` = `aura2` / `spell` / `item` / `unit`), not the old
3.3.5-era one. Observed in live auras:

- `aura2` — Aura (buff/debuff) by `auraspellids`, incl. stacks and duration
- `spell` — Cooldown Progress (Spell)
- `item` — Weapon Enchant (this is how Runemaster's Weapon Engravings are tracked)
- `unit` — Range Check, Cast, Health, Power, Conditions

Region types observed: `group`, `dynamicgroup`, `icon`, `aurabar`, `texture`.

## Gotcha

`v = 2000` auras and `v = 1421` auras both import. Emit `2000` to match what the
current client produces.
