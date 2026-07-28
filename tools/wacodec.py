"""LibDeflate EncodeForPrint + LibSerialize v1 codec for WeakAuras `!WA:2!` strings.

Verified against LibSerialize.lua (MINOR 6) and LibDeflate EncodeForPrint.
Lua tables are represented in Python as `LuaTable` (an ordered dict with 1-based
integer keys for the array part).
"""
import struct
import zlib

# ---------------------------------------------------------------- print codec
ALPHA = ("abcdefghijklmnopqrstuvwxyz"
         "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
         "0123456789()")
IDX = {c: i for i, c in enumerate(ALPHA)}


def decode_for_print(s):
    out = bytearray()
    i, n = 0, len(s)
    while i + 4 <= n:
        c = (IDX[s[i]] + IDX[s[i + 1]] * 64
             + IDX[s[i + 2]] * 4096 + IDX[s[i + 3]] * 262144)
        out += bytes([c & 0xFF, (c >> 8) & 0xFF, (c >> 16) & 0xFF])
        i += 4
    cache = bitlen = 0
    while i < n:
        cache += IDX[s[i]] << bitlen
        bitlen += 6
        i += 1
    while bitlen >= 8:
        out.append(cache & 0xFF)
        cache >>= 8
        bitlen -= 8
    return bytes(out)


def encode_for_print(b):
    buf = []
    i, n = 0, len(b)
    while i + 3 <= n:
        c = b[i] + b[i + 1] * 256 + b[i + 2] * 65536
        buf += [ALPHA[c & 63], ALPHA[(c >> 6) & 63],
                ALPHA[(c >> 12) & 63], ALPHA[(c >> 18) & 63]]
        i += 3
    cache = bitlen = 0
    while i < n:
        cache += b[i] << bitlen
        bitlen += 8
        i += 1
    while bitlen > 0:
        buf.append(ALPHA[cache & 63])
        cache >>= 6
        bitlen -= 6
    return "".join(buf)


def inflate(b):
    return zlib.decompress(b, -15)


def deflate(b, level=9):
    c = zlib.compressobj(level, zlib.DEFLATED, -15)
    return c.compress(b) + c.flush()


# ------------------------------------------------------------- reader indices
NIL = 0
NUM_16_POS, NUM_16_NEG = 1, 2
NUM_24_POS, NUM_24_NEG = 3, 4
NUM_32_POS, NUM_32_NEG = 5, 6
NUM_64_POS, NUM_64_NEG = 7, 8
NUM_FLOAT, NUM_FLOATSTR, NUM_FLOATSTR_NEG = 9, 10, 11
BOOL_T, BOOL_F = 12, 13
STR_8, STR_16, STR_24 = 14, 15, 16
TABLE_8, TABLE_16, TABLE_24 = 17, 18, 19
ARRAY_8, ARRAY_16, ARRAY_24 = 20, 21, 22
MIXED_8, MIXED_16, MIXED_24 = 23, 24, 25
STRREF_8, STRREF_16, STRREF_24 = 26, 27, 28
TABREF_8, TABREF_16, TABREF_24 = 29, 30, 31

NUMBER_IDX = {2: NUM_16_POS, 3: NUM_24_POS, 4: NUM_32_POS, 7: NUM_64_POS}
STR_IDX = {1: STR_8, 2: STR_16, 3: STR_24}
TAB_IDX = {1: TABLE_8, 2: TABLE_16, 3: TABLE_24}
ARR_IDX = {1: ARRAY_8, 2: ARRAY_16, 3: ARRAY_24}
MIX_IDX = {1: MIXED_8, 2: MIXED_16, 3: MIXED_24}
STRREF_IDX = {1: STRREF_8, 2: STRREF_16, 3: STRREF_24}
TABREF_IDX = {1: TABREF_8, 2: TABREF_16, 3: TABREF_24}


class LuaTable(dict):
    """dict preserving insertion order; keys may be ints (1-based) or strings."""

    def array_part(self):
        out = []
        i = 1
        while i in self:
            out.append(self[i])
            i += 1
        return out


# -------------------------------------------------------------- deserializer
class _Reader:
    def __init__(self, data):
        self.d, self.p = data, 0
        self.strs, self.tabs = [], []

    def byte(self):
        v = self.d[self.p]
        self.p += 1
        return v

    def uint(self, n):
        v = int.from_bytes(self.d[self.p:self.p + n], "big")
        self.p += n
        return v

    def raw(self, n):
        v = self.d[self.p:self.p + n]
        self.p += n
        return v


def _read_string(r, n):
    s = r.raw(n).decode("utf-8", "surrogateescape")
    if n > 2:
        r.strs.append(s)
    return s


def _read_table(r, count, tbl=None):
    if tbl is None:
        tbl = LuaTable()
        r.tabs.append(tbl)
    for _ in range(count):
        k = _read_obj(r)
        v = _read_obj(r)
        tbl[k] = v
    return tbl


def _read_array(r, count, tbl=None):
    if tbl is None:
        tbl = LuaTable()
        r.tabs.append(tbl)
    for i in range(1, count + 1):
        tbl[i] = _read_obj(r)
    return tbl


def _read_mixed(r, acount, mcount):
    tbl = LuaTable()
    r.tabs.append(tbl)
    _read_array(r, acount, tbl)
    _read_table(r, mcount, tbl)
    return tbl


def _read_obj(r):
    b = r.byte()
    if b % 2 == 1:
        return (b - 1) // 2
    if b % 4 == 2:
        t = (b - 2) // 4
        count = t // 4
        t = t % 4
        if t == 0:
            return _read_string(r, count)
        if t == 1:
            return _read_table(r, count)
        if t == 2:
            return _read_array(r, count)
        return _read_mixed(r, (count % 4) + 1, (count // 4) + 1)
    if b % 8 == 4:
        packed = r.byte() * 256 + b
        return -((packed - 12) // 16) if b % 16 == 12 else (packed - 4) // 16
    t = b // 8
    if t == NIL:
        return None
    if t in (NUM_16_POS, NUM_16_NEG):
        v = r.uint(2)
    elif t in (NUM_24_POS, NUM_24_NEG):
        v = r.uint(3)
    elif t in (NUM_32_POS, NUM_32_NEG):
        v = r.uint(4)
    elif t in (NUM_64_POS, NUM_64_NEG):
        v = r.uint(7)
    elif t == NUM_FLOAT:
        return struct.unpack(">d", r.raw(8))[0]
    elif t in (NUM_FLOATSTR, NUM_FLOATSTR_NEG):
        v = float(r.raw(r.byte()).decode())
        return -v if t == NUM_FLOATSTR_NEG else v
    elif t == BOOL_T:
        return True
    elif t == BOOL_F:
        return False
    elif t in (STR_8, STR_16, STR_24):
        return _read_string(r, r.uint(t - STR_8 + 1))
    elif t in (TABLE_8, TABLE_16, TABLE_24):
        return _read_table(r, r.uint(t - TABLE_8 + 1))
    elif t in (ARRAY_8, ARRAY_16, ARRAY_24):
        return _read_array(r, r.uint(t - ARRAY_8 + 1))
    elif t in (MIXED_8, MIXED_16, MIXED_24):
        n = t - MIXED_8 + 1
        return _read_mixed(r, r.uint(n), r.uint(n))
    elif t in (STRREF_8, STRREF_16, STRREF_24):
        return r.strs[r.uint(t - STRREF_8 + 1) - 1]
    elif t in (TABREF_8, TABREF_16, TABREF_24):
        return r.tabs[r.uint(t - TABREF_8 + 1) - 1]
    else:
        raise ValueError(f"bad type {t} at offset {r.p}")
    return -v if t in (NUM_16_NEG, NUM_24_NEG, NUM_32_NEG, NUM_64_NEG) else v


def deserialize(data):
    r = _Reader(data)
    ver = r.byte()
    if ver not in (1, 2):
        raise ValueError(f"unsupported serialization version {ver}")
    vals = []
    while r.p < len(r.d):
        vals.append(_read_obj(r))
    return vals[0] if len(vals) == 1 else vals


# ---------------------------------------------------------------- serializer
def _req_bytes(v):
    if v < 256:
        return 1
    if v < 65536:
        return 2
    if v < 16777216:
        return 3
    raise ValueError("object limit exceeded")


def _req_bytes_num(v):
    if v < 256:
        return 1
    if v < 65536:
        return 2
    if v < 16777216:
        return 3
    if v < 4294967296:
        return 4
    return 7


class _Writer:
    def __init__(self):
        self.out = bytearray()
        self.strs = {}   # str -> ref index
        self.tabs = {}   # id(table) -> ref index

    def byte(self, b):
        self.out.append(b)

    def uint(self, v, n):
        self.out += int(v).to_bytes(n, "big")

    def raw(self, b):
        self.out += b


def _is_float(v):
    return isinstance(v, float) and not v.is_integer()


def _write_number(w, num):
    if isinstance(num, float) and (num.is_integer() and abs(num) < 2 ** 53):
        num = int(num)
    if isinstance(num, float):
        sign = 0
        a = num
        if num < 0:
            sign, a = 8, -num
        s = repr(a)
        if len(s) < 7 and float(s) == a:
            w.byte(sign + 8 * NUM_FLOATSTR)
            w.byte(len(s))
            w.raw(s.encode())
        else:
            w.byte(8 * NUM_FLOAT)
            w.raw(struct.pack(">d", num))
        return
    if -4096 < num < 4096:
        if 0 <= num < 128:
            w.byte(num * 2 + 1)
        else:
            sign = 0
            n = num
            if n < 0:
                sign, n = 8, -n
            n = n * 16 + sign + 4
            w.byte(n % 256)
            w.byte(n // 256)
        return
    sign = 0
    n = num
    if n < 0:
        sign, n = 8, -n
    req = _req_bytes_num(n)
    w.byte(sign + 8 * NUMBER_IDX[req])
    w.uint(n, req)


def _write_string(w, s):
    ref = w.strs.get(s)
    if ref is not None:
        req = _req_bytes(ref)
        w.byte(8 * STRREF_IDX[req])
        w.uint(ref, req)
        return
    b = s.encode("utf-8", "surrogateescape")
    n = len(b)
    if n < 16:
        w.byte(16 * n + 4 * 0 + 2)
    else:
        req = _req_bytes(n)
        w.byte(8 * STR_IDX[req])
        w.uint(n, req)
    w.raw(b)
    if n > 2:
        w.strs[s] = len(w.strs) + 1


def _split_table(t):
    """Return (array_values, map_pairs) matching LibSerialize's layout rules."""
    acount = 0
    while (acount + 1) in t and t[acount + 1] is not None:
        acount += 1
    arr = [t[i] for i in range(1, acount + 1)]
    mp = [(k, v) for k, v in t.items()
          if not (isinstance(k, int) and not isinstance(k, bool) and 1 <= k <= acount)]
    return arr, mp


def _write_table(w, t):
    key = id(t)
    ref = w.tabs.get(key)
    if ref is not None:
        req = _req_bytes(ref)
        w.byte(8 * TABREF_IDX[req])
        w.uint(ref, req)
        return
    w.tabs[key] = len(w.tabs) + 1

    arr, mp = _split_table(t)
    ac, mc = len(arr), len(mp)

    if mc == 0:
        if ac < 16:
            w.byte(16 * ac + 4 * 2 + 2)
        else:
            req = _req_bytes(ac)
            w.byte(8 * ARR_IDX[req])
            w.uint(ac, req)
        for v in arr:
            _write_obj(w, v)
    elif ac != 0:
        if mc < 5 and ac < 5:
            combined = (mc - 1) * 4 + ac - 1
            w.byte(16 * combined + 4 * 3 + 2)
        else:
            req = max(_req_bytes(mc), _req_bytes(ac))
            w.byte(8 * MIX_IDX[req])
            w.uint(ac, req)
            w.uint(mc, req)
        for v in arr:
            _write_obj(w, v)
        for k, v in mp:
            _write_obj(w, k)
            _write_obj(w, v)
    else:
        if mc < 16:
            w.byte(16 * mc + 4 * 1 + 2)
        else:
            req = _req_bytes(mc)
            w.byte(8 * TAB_IDX[req])
            w.uint(mc, req)
        for k, v in mp:
            _write_obj(w, k)
            _write_obj(w, v)


def _write_obj(w, v):
    if v is None:
        w.byte(8 * NIL)
    elif isinstance(v, bool):
        w.byte(8 * (BOOL_T if v else BOOL_F))
    elif isinstance(v, (int, float)):
        _write_number(w, v)
    elif isinstance(v, str):
        _write_string(w, v)
    elif isinstance(v, dict):
        _write_table(w, v)
    elif isinstance(v, (list, tuple)):
        t = LuaTable()
        for i, x in enumerate(v):
            t[i + 1] = x
        _write_table(w, t)
    else:
        raise TypeError(f"unserializable {type(v)}")


def serialize(*values):
    w = _Writer()
    w.byte(1)
    for v in values:
        _write_obj(w, v)
    return bytes(w.out)


# ------------------------------------------------------------------ WA glue
def wa_decode(s):
    s = s.strip()
    if s.startswith("!WA:2!"):
        s = s[6:]
    return deserialize(inflate(decode_for_print(s)))


def wa_encode(data, level=9):
    return "!WA:2!" + encode_for_print(deflate(serialize(data), level))


if __name__ == "__main__":
    import json
    import sys
    d = wa_decode(open(sys.argv[1]).read())
    print(json.dumps(d, indent=1, default=str)[:6000])
