"""Derive a per-class accent colour from that class's own icon art.

    python3 tools/iconcolor.py            # every class, as a table
    python3 tools/iconcolor.py runemaster # one

The site gives each class a colour. Hand-assigning 21 of them would be one more
list to drift out of step with `classes.py` -- and it would not match the art.
So the colour is READ OUT OF THE ICON: decode the PNG, throw away the pixels
that carry no hue, and take the dominant one.

Why a hand-rolled PNG reader: Pillow is not installed and this is the only
image work in the repo, so a dependency (and a wheel per CI platform) to read
21 files of 36x36 is a bad trade. The class icons are all 8-bit non-interlaced
RGB, which is the easy corner of the format -- inflate, unfilter, done.
Palette (3) and RGBA (6) are handled too so a re-scrape in another encoding
does not silently break the site.

Interlaced (Adam7) PNGs are NOT supported and raise, rather than returning a
plausible-but-wrong colour from mis-read scanlines.
"""
import colorsys
import json
import math
import os
import struct
import sys
import zlib

SP = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SP)
ICONS = os.path.join(ROOT, "docs", "assets", "class-icons")

# Pixels that carry no usable hue. Icon art sits on a black or near-black
# border and most have a metallic grey mass; both would drag any average
# towards mud, which is how every "dominant colour" script ends up beige.
V_FLOOR = 0.18     # near-black: the border, shadow
V_CEIL = 0.97      # blown-out white: glare, sparkles
S_FLOOR = 0.18     # grey: steel, stone, bone

HUE_BINS = 36      # 10 degrees each

# WoW icon art is framed in an ornate gold-brown border that is IDENTICAL on
# every icon. Sampling the whole image therefore returns "amber" for most of
# the roster -- the first run of this script put 8 of 21 classes inside a 40
# degree wedge, all of it border. Dropping the outer ring leaves the subject,
# which is what a player actually recognises the class by.
CROP = 0.20        # fraction of width/height discarded from each edge

# Only the HUE is trusted from the art; a card border needs predictable weight
# against the page. But pinning S and L to constants flattened deep blood-red
# and bright gold into the same washed mid-tone, so the source saturation is
# carried through -- rescaled into a band that stays legible on the dark page.
S_RANGE = (0.48, 0.86)
L_RANGE = (0.54, 0.68)
DEEP_S = 0.55
DEEP_L = 0.22

FALLBACK = "#8a94a6"   # steel, for art with no chromatic pixels at all


def _paeth(a, b, c):
    p = a + b - c
    pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    if pb <= pc:
        return b
    return c


def read_png(path):
    """-> (width, height, [(r,g,b), ...]). 8-bit, non-interlaced only."""
    raw = open(path, "rb").read()
    if raw[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"{path}: not a PNG")

    pos = 8
    ihdr = None
    idat = bytearray()
    palette = None
    while pos < len(raw):
        (length,) = struct.unpack(">I", raw[pos:pos + 4])
        kind = raw[pos + 4:pos + 8]
        body = raw[pos + 8:pos + 8 + length]
        pos += 12 + length          # 4 len + 4 type + body + 4 crc
        if kind == b"IHDR":
            ihdr = struct.unpack(">IIBBBBB", body)
        elif kind == b"PLTE":
            palette = [tuple(body[i:i + 3]) for i in range(0, len(body), 3)]
        elif kind == b"IDAT":
            idat += body
        elif kind == b"IEND":
            break

    if not ihdr:
        raise ValueError(f"{path}: no IHDR")
    w, h, depth, ctype, _comp, _filt, interlace = ihdr
    if interlace:
        raise ValueError(f"{path}: interlaced PNGs are not supported")
    if depth != 8:
        raise ValueError(f"{path}: bit depth {depth}, only 8 is supported")

    channels = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}.get(ctype)
    if channels is None:
        raise ValueError(f"{path}: unknown colour type {ctype}")
    if ctype == 3 and not palette:
        raise ValueError(f"{path}: palette image with no PLTE")

    data = zlib.decompress(bytes(idat))
    stride = w * channels
    out = []
    prev = bytearray(stride)
    at = 0
    for _ in range(h):
        ftype = data[at]
        at += 1
        line = bytearray(data[at:at + stride])
        at += stride
        # Unfilter in place. bpp is the byte distance to the pixel on the
        # left; for the leftmost pixel that operand is defined as zero.
        bpp = channels
        for i in range(stride):
            a = line[i - bpp] if i >= bpp else 0
            b = prev[i]
            if ftype == 1:
                line[i] = (line[i] + a) & 0xFF
            elif ftype == 2:
                line[i] = (line[i] + b) & 0xFF
            elif ftype == 3:
                line[i] = (line[i] + ((a + b) >> 1)) & 0xFF
            elif ftype == 4:
                c = prev[i - bpp] if i >= bpp else 0
                line[i] = (line[i] + _paeth(a, b, c)) & 0xFF
            elif ftype != 0:
                raise ValueError(f"{path}: bad filter type {ftype}")
        for x in range(w):
            o = x * channels
            if ctype == 2 or ctype == 6:
                out.append((line[o], line[o + 1], line[o + 2]))
            elif ctype == 3:
                out.append(palette[line[o]])
            else:                     # 0 grey, 4 grey+alpha
                g = line[o]
                out.append((g, g, g))
        prev = line
    return w, h, out


def crop_center(w, h, pixels, frac=CROP):
    """Drop `frac` of each edge. See CROP -- the discarded ring is the shared
    icon border, which is the same colour on every class."""
    dx, dy = int(w * frac), int(h * frac)
    if w - 2 * dx < 4 or h - 2 * dy < 4:
        return pixels                      # too small to crop meaningfully
    return [pixels[y * w + x]
            for y in range(dy, h - dy)
            for x in range(dx, w - dx)]


def dominant(pixels):
    """-> (hue in turns, mean saturation of the winning hue), or None if
    nothing chromatic survives.

    A plain mean over hue is wrong twice: hue is circular (a red icon with
    pixels at 0.02 and 0.98 averages to cyan), and a broad dull background
    outvotes the small vivid subject that actually reads as "the colour". So:
    histogram first to find where the colour lives, then take a circular mean
    of just that neighbourhood.
    """
    bins = [0.0] * HUE_BINS
    kept = []
    for r, g, b in pixels:
        h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
        v = max(r, g, b) / 255
        if v < V_FLOOR or v > V_CEIL or s < S_FLOOR:
            continue
        weight = s * v          # vivid and bright pixels carry the identity
        bins[int(h * HUE_BINS) % HUE_BINS] += weight
        kept.append((h, s, weight))
    if not kept:
        return None

    peak = max(range(HUE_BINS), key=lambda i: bins[i])
    # Circular mean over the peak bin and its two neighbours, so a hue sitting
    # on a bin boundary is not split in half and lost.
    near = {(peak - 1) % HUE_BINS, peak, (peak + 1) % HUE_BINS}
    x = y = 0.0
    sat_sum = sat_w = 0.0
    for h, s, weight in kept:
        if int(h * HUE_BINS) % HUE_BINS in near:
            ang = h * 2 * math.pi
            x += math.cos(ang) * weight
            y += math.sin(ang) * weight
            sat_sum += s * weight
            sat_w += weight
    sat = (sat_sum / sat_w) if sat_w else 0.6
    if x == 0 and y == 0:
        return peak / HUE_BINS, sat
    return (math.atan2(y, x) / (2 * math.pi)) % 1.0, sat


def _rescale(v, lo, hi):
    return lo + (hi - lo) * max(0.0, min(1.0, v))


def _hex(h, s, l):
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return "#%02x%02x%02x" % (round(r * 255), round(g * 255), round(b * 255))


def accent_for(icon_path):
    """-> (accent, deep). Both hex. Deep is the same hue, dark and dull, for
    fills behind text."""
    w, h, px = read_png(icon_path)
    got = dominant(crop_center(w, h, px))
    if got is None:
        return FALLBACK, "#232a33"
    hue, sat = got
    # Source saturation runs roughly 0.2-0.9; map that span onto the legible
    # band so muted art stays muted relative to vivid art without either end
    # becoming unreadable.
    t = (sat - 0.25) / 0.55
    s = _rescale(t, *S_RANGE)
    # Saturated hues read heavier, so drop lightness slightly as S climbs to
    # keep perceived weight even across the roster.
    l = _rescale(1 - t, *L_RANGE)
    return _hex(hue, s, l), _hex(hue, DEEP_S, DEEP_L)


def class_icon(slug):
    return os.path.join(ICONS, slug, f"_class-{slug}.png")


def colors_for(slugs):
    """-> {slug: {"accent": ..., "deep": ...}}. A class whose icon is missing
    gets the fallback rather than killing the site build -- a new class lands
    in classes.py before its art is scraped."""
    out = {}
    for slug in slugs:
        path = class_icon(slug)
        if not os.path.exists(path):
            out[slug] = {"accent": FALLBACK, "deep": "#232a33"}
            continue
        accent, deep = accent_for(path)
        out[slug] = {"accent": accent, "deep": deep}
    return out


if __name__ == "__main__":
    sys.path.insert(0, SP)
    from classes import CLASSES

    want = sys.argv[1:]
    slugs = [c.slug for c in sorted(CLASSES.values(), key=lambda c: c.name)]
    if want:
        slugs = [s for s in slugs if s in want]
        if not slugs:
            raise SystemExit(f"no such class: {' '.join(want)}")

    cols = colors_for(slugs)
    for slug in slugs:
        c = cols[slug]
        print(f"  {slug:<18} {c['accent']}  {c['deep']}")
    print(f"\n{len(slugs)} classes")
    if os.environ.get("JSON"):
        print(json.dumps(cols, indent=2))
