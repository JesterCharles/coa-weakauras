/* JS port of tools/wacodec.py — LibDeflate EncodeForPrint + LibSerialize v1
 * codec for WeakAuras `!WA:2!` strings (Ascension CoA fork).
 *
 * Function-for-function twin of the Python reference so the two stay diffable
 * by eye (ADR-003 D1). Lua tables are LuaTable — an insertion-ordered Map with
 * 1-based integer keys for the array part — never plain JSON objects.
 *
 * DEFLATE is pako (vendored, raw mode); everything else is hand-ported.
 * Works in the browser (window.wacodec, expects window.pako) and in node
 * (module.exports, requires ./vendor/pako.min.js).
 */
(function (root, factory) {
  if (typeof module === "object" && module.exports) {
    module.exports = factory(require("./vendor/pako.min.js"));
  } else {
    root.wacodec = factory(root.pako);
  }
})(typeof self !== "undefined" ? self : this, function (pako) {
  "use strict";

  // ---------------------------------------------------------------- print codec
  var ALPHA = "abcdefghijklmnopqrstuvwxyz" +
              "ABCDEFGHIJKLMNOPQRSTUVWXYZ" +
              "0123456789()";
  var IDX = {};
  for (var ai = 0; ai < ALPHA.length; ai++) IDX[ALPHA[ai]] = ai;

  function decodeForPrint(s) {
    var out = [];
    var i = 0, n = s.length;
    while (i + 4 <= n) {
      var c = IDX[s[i]] + IDX[s[i + 1]] * 64 +
              IDX[s[i + 2]] * 4096 + IDX[s[i + 3]] * 262144;
      if (isNaN(c)) throw new Error("bad character in print stream at " + i);
      out.push(c & 0xFF, (c >> 8) & 0xFF, (c >> 16) & 0xFF);
      i += 4;
    }
    var cache = 0, bitlen = 0;
    while (i < n) {
      var v = IDX[s[i]];
      if (v === undefined) throw new Error("bad character in print stream at " + i);
      cache += v * Math.pow(2, bitlen);
      bitlen += 6;
      i += 1;
    }
    while (bitlen >= 8) {
      out.push(cache & 0xFF);
      cache = Math.floor(cache / 256);
      bitlen -= 8;
    }
    return new Uint8Array(out);
  }

  function encodeForPrint(b) {
    var buf = [];
    var i = 0, n = b.length;
    while (i + 3 <= n) {
      var c = b[i] + b[i + 1] * 256 + b[i + 2] * 65536;
      buf.push(ALPHA[c & 63], ALPHA[(c >> 6) & 63],
               ALPHA[(c >> 12) & 63], ALPHA[(c >> 18) & 63]);
      i += 3;
    }
    var cache = 0, bitlen = 0;
    while (i < n) {
      cache += b[i] * Math.pow(2, bitlen);
      bitlen += 8;
      i += 1;
    }
    while (bitlen > 0) {
      buf.push(ALPHA[cache & 63]);
      cache = Math.floor(cache / 64);
      bitlen -= 6;
    }
    return buf.join("");
  }

  function inflate(b) { return pako.inflateRaw(b); }

  function deflate(b, level) {
    return pako.deflateRaw(b, { level: level === undefined ? 9 : level });
  }

  // ------------------------------------------------------------- reader indices
  var NIL = 0;
  var NUM_16_POS = 1, NUM_16_NEG = 2;
  var NUM_24_POS = 3, NUM_24_NEG = 4;
  var NUM_32_POS = 5, NUM_32_NEG = 6;
  var NUM_64_POS = 7, NUM_64_NEG = 8;
  var NUM_FLOAT = 9, NUM_FLOATSTR = 10, NUM_FLOATSTR_NEG = 11;
  var BOOL_T = 12, BOOL_F = 13;
  var STR_8 = 14, STR_16 = 15, STR_24 = 16;
  var TABLE_8 = 17, TABLE_16 = 18, TABLE_24 = 19;
  var ARRAY_8 = 20, ARRAY_16 = 21, ARRAY_24 = 22;
  var MIXED_8 = 23, MIXED_16 = 24, MIXED_24 = 25;
  var STRREF_8 = 26, STRREF_16 = 27, STRREF_24 = 28;
  var TABREF_8 = 29, TABREF_16 = 30, TABREF_24 = 31;

  var NUMBER_IDX = { 2: NUM_16_POS, 3: NUM_24_POS, 4: NUM_32_POS, 7: NUM_64_POS };
  var STR_IDX = { 1: STR_8, 2: STR_16, 3: STR_24 };
  var TAB_IDX = { 1: TABLE_8, 2: TABLE_16, 3: TABLE_24 };
  var ARR_IDX = { 1: ARRAY_8, 2: ARRAY_16, 3: ARRAY_24 };
  var MIX_IDX = { 1: MIXED_8, 2: MIXED_16, 3: MIXED_24 };
  var STRREF_IDX = { 1: STRREF_8, 2: STRREF_16, 3: STRREF_24 };
  var TABREF_IDX = { 1: TABREF_8, 2: TABREF_16, 3: TABREF_24 };

  // LuaTable: insertion-ordered, integer-vs-string key identity preserved
  // (Map distinguishes 1 from "1" natively). Twin of wacodec.py LuaTable.
  function LuaTable() { this.map = new Map(); }
  LuaTable.prototype.get = function (k) { return this.map.get(k); };
  LuaTable.prototype.set = function (k, v) { this.map.set(k, v); return this; };
  LuaTable.prototype.has = function (k) { return this.map.has(k); };
  LuaTable.prototype.delete = function (k) { return this.map.delete(k); };
  LuaTable.prototype.entries = function () { return this.map.entries(); };
  LuaTable.prototype.keys = function () { return this.map.keys(); };
  Object.defineProperty(LuaTable.prototype, "size", {
    get: function () { return this.map.size; }
  });
  LuaTable.prototype.arrayPart = function () {
    var out = [];
    var i = 1;
    while (this.map.has(i)) { out.push(this.map.get(i)); i += 1; }
    return out;
  };

  // ------------------------------------------- UTF-8 with surrogateescape
  // Mirrors Python's "utf-8, surrogateescape": each invalid byte b (>= 0x80)
  // becomes lone surrogate 0xDC00+b on decode and is restored on encode.
  function utf8DecodeSE(bytes) {
    var out = [];
    var i = 0, n = bytes.length;
    while (i < n) {
      var b = bytes[i];
      if (b < 0x80) { out.push(String.fromCharCode(b)); i += 1; continue; }
      var len = 0, v = 0;
      if (b >= 0xC2 && b <= 0xDF) { len = 2; v = b & 0x1F; }
      else if (b >= 0xE0 && b <= 0xEF) { len = 3; v = b & 0x0F; }
      else if (b >= 0xF0 && b <= 0xF4) { len = 4; v = b & 0x07; }
      var ok = len > 0 && i + len <= n;
      if (ok) {
        for (var j = 1; j < len; j++) {
          var cb = bytes[i + j];
          if ((cb & 0xC0) !== 0x80) { ok = false; break; }
          v = (v << 6) | (cb & 0x3F);
        }
      }
      if (ok) {
        if (len === 2 && v < 0x80) ok = false;
        if (len === 3 && (v < 0x800 || (v >= 0xD800 && v <= 0xDFFF))) ok = false;
        if (len === 4 && (v < 0x10000 || v > 0x10FFFF)) ok = false;
      }
      if (ok) { out.push(String.fromCodePoint(v)); i += len; }
      else { out.push(String.fromCharCode(0xDC00 + b)); i += 1; }
    }
    return out.join("");
  }

  function utf8EncodeSE(s) {
    var out = [];
    for (var i = 0; i < s.length; i++) {
      var c = s.charCodeAt(i);
      if (c < 0x80) { out.push(c); }
      else if (c < 0x800) { out.push(0xC0 | (c >> 6), 0x80 | (c & 63)); }
      else if (c >= 0xD800 && c <= 0xDBFF) {
        var c2 = s.charCodeAt(i + 1);
        if (c2 >= 0xDC00 && c2 <= 0xDFFF) {
          var v = 0x10000 + ((c - 0xD800) << 10) + (c2 - 0xDC00);
          out.push(0xF0 | (v >> 18), 0x80 | ((v >> 12) & 63),
                   0x80 | ((v >> 6) & 63), 0x80 | (v & 63));
          i += 1;
        } else { throw new Error("lone high surrogate in string"); }
      } else if (c >= 0xDC80 && c <= 0xDCFF) {
        out.push(c & 0xFF); // surrogateescape restore
      } else if (c >= 0xDC00 && c <= 0xDC7F) {
        throw new Error("unencodable lone low surrogate");
      } else {
        out.push(0xE0 | (c >> 12), 0x80 | ((c >> 6) & 63), 0x80 | (c & 63));
      }
    }
    return new Uint8Array(out);
  }

  // -------------------------------------------------------------- deserializer
  function Reader(data) {
    this.d = data; this.p = 0;
    this.strs = []; this.tabs = [];
  }
  Reader.prototype.byte = function () { return this.d[this.p++]; };
  Reader.prototype.uint = function (n) {
    if (n <= 6) {
      var v = 0;
      for (var i = 0; i < n; i++) v = v * 256 + this.d[this.p++];
      return v;
    }
    var bv = 0n;
    for (var j = 0; j < n; j++) bv = bv * 256n + BigInt(this.d[this.p++]);
    if (bv > BigInt(Number.MAX_SAFE_INTEGER)) {
      throw new Error("integer exceeds 2^53 at offset " + this.p);
    }
    return Number(bv);
  };
  Reader.prototype.raw = function (n) {
    var v = this.d.subarray(this.p, this.p + n);
    this.p += n;
    return v;
  };

  function readString(r, n) {
    var s = utf8DecodeSE(r.raw(n));
    if (n > 2) r.strs.push(s);
    return s;
  }

  function readTable(r, count, tbl) {
    if (tbl === undefined) {
      tbl = new LuaTable();
      r.tabs.push(tbl);
    }
    for (var i = 0; i < count; i++) {
      var k = readObj(r);
      var v = readObj(r);
      tbl.set(k, v);
    }
    return tbl;
  }

  function readArray(r, count, tbl) {
    if (tbl === undefined) {
      tbl = new LuaTable();
      r.tabs.push(tbl);
    }
    for (var i = 1; i <= count; i++) tbl.set(i, readObj(r));
    return tbl;
  }

  function readMixed(r, acount, mcount) {
    var tbl = new LuaTable();
    r.tabs.push(tbl);
    readArray(r, acount, tbl);
    readTable(r, mcount, tbl);
    return tbl;
  }

  function readObj(r) {
    var b = r.byte();
    if (b === undefined) throw new Error("unexpected end of stream");
    if (b % 2 === 1) return (b - 1) / 2;
    if (b % 4 === 2) {
      var t2 = (b - 2) / 4;
      var count = Math.floor(t2 / 4);
      t2 = t2 % 4;
      if (t2 === 0) return readString(r, count);
      if (t2 === 1) return readTable(r, count);
      if (t2 === 2) return readArray(r, count);
      return readMixed(r, (count % 4) + 1, Math.floor(count / 4) + 1);
    }
    if (b % 8 === 4) {
      var packed = r.byte() * 256 + b;
      return b % 16 === 12 ? -Math.floor((packed - 12) / 16)
                           : Math.floor((packed - 4) / 16);
    }
    var t = Math.floor(b / 8);
    var v;
    if (t === NIL) return null;
    if (t === NUM_16_POS || t === NUM_16_NEG) v = r.uint(2);
    else if (t === NUM_24_POS || t === NUM_24_NEG) v = r.uint(3);
    else if (t === NUM_32_POS || t === NUM_32_NEG) v = r.uint(4);
    else if (t === NUM_64_POS || t === NUM_64_NEG) v = r.uint(7);
    else if (t === NUM_FLOAT) {
      var dv = new DataView(r.d.buffer, r.d.byteOffset + r.p, 8);
      r.p += 8;
      return dv.getFloat64(0, false);
    }
    else if (t === NUM_FLOATSTR || t === NUM_FLOATSTR_NEG) {
      var fs = utf8DecodeSE(r.raw(r.byte()));
      var fv = parseFloat(fs);
      return t === NUM_FLOATSTR_NEG ? -fv : fv;
    }
    else if (t === BOOL_T) return true;
    else if (t === BOOL_F) return false;
    else if (t === STR_8 || t === STR_16 || t === STR_24)
      return readString(r, r.uint(t - STR_8 + 1));
    else if (t === TABLE_8 || t === TABLE_16 || t === TABLE_24)
      return readTable(r, r.uint(t - TABLE_8 + 1));
    else if (t === ARRAY_8 || t === ARRAY_16 || t === ARRAY_24)
      return readArray(r, r.uint(t - ARRAY_8 + 1));
    else if (t === MIXED_8 || t === MIXED_16 || t === MIXED_24) {
      var nn = t - MIXED_8 + 1;
      return readMixed(r, r.uint(nn), r.uint(nn));
    }
    else if (t === STRREF_8 || t === STRREF_16 || t === STRREF_24)
      return r.strs[r.uint(t - STRREF_8 + 1) - 1];
    else if (t === TABREF_8 || t === TABREF_16 || t === TABREF_24)
      return r.tabs[r.uint(t - TABREF_8 + 1) - 1];
    else throw new Error("bad type " + t + " at offset " + r.p);
    return (t === NUM_16_NEG || t === NUM_24_NEG ||
            t === NUM_32_NEG || t === NUM_64_NEG) ? -v : v;
  }

  function deserialize(data) {
    var r = new Reader(data);
    var ver = r.byte();
    if (ver !== 1 && ver !== 2)
      throw new Error("unsupported serialization version " + ver);
    var vals = [];
    while (r.p < r.d.length) vals.push(readObj(r));
    return vals.length === 1 ? vals[0] : vals;
  }

  // ---------------------------------------------------------------- serializer
  function reqBytes(v) {
    if (v < 256) return 1;
    if (v < 65536) return 2;
    if (v < 16777216) return 3;
    throw new Error("object limit exceeded");
  }

  function reqBytesNum(v) {
    if (v < 256) return 1;
    if (v < 65536) return 2;
    if (v < 16777216) return 3;
    if (v < 4294967296) return 4;
    return 7;
  }

  function Writer() {
    this.out = [];
    this.strs = new Map();  // string value -> ref index
    this.tabs = new Map();  // LuaTable object -> ref index
  }
  Writer.prototype.byte = function (b) { this.out.push(b); };
  Writer.prototype.uint = function (v, n) {
    for (var i = n - 1; i >= 0; i--)
      this.out.push(Math.floor(v / Math.pow(256, i)) % 256);
  };
  Writer.prototype.raw = function (bytes) {
    for (var i = 0; i < bytes.length; i++) this.out.push(bytes[i]);
  };
  Writer.prototype.bytes = function () { return new Uint8Array(this.out); };

  // Python repr() twin for positive finite doubles. LibSerialize's FLOATSTR
  // path (via wacodec.py) emits repr(a) when it is < 7 chars; JS String()
  // formatting thresholds differ from Python's (e.g. 1e-05 vs 0.00001), so
  // the port formats explicitly by Python's rules: fixed notation for
  // -4 <= exp10 < 16, else scientific with a two-digit-minimum exponent.
  function pyFloatRepr(a) {
    var es = a.toExponential(); // shortest digits per spec when arg omitted
    var m = es.match(/^(\d)(?:\.(\d+))?e([+-]\d+)$/);
    if (!m) throw new Error("unexpected exponential form " + es);
    var digits = m[1] + (m[2] || "");
    var exp = parseInt(m[3], 10);
    if (exp >= -4 && exp < 16) {
      if (exp >= digits.length - 1) {
        return digits + new Array(exp - (digits.length - 1) + 1).join("0") + ".0";
      }
      if (exp >= 0) {
        return digits.slice(0, exp + 1) + "." + digits.slice(exp + 1);
      }
      return "0." + new Array(-exp).join("0") + digits;
    }
    var mant = digits[0];
    if (digits.length > 1) mant += "." + digits.slice(1);
    var esign = exp < 0 ? "-" : "+";
    var eabs = String(Math.abs(exp));
    if (eabs.length < 2) eabs = "0" + eabs;
    return mant + "e" + esign + eabs;
  }

  function writeNumber(w, num) {
    if (!Number.isFinite(num)) throw new Error("non-finite number");
    if (!Number.isInteger(num) || Math.abs(num) >= Math.pow(2, 53)) {
      // float path (Python: isinstance(num, float) after integral conversion)
      var sign = 0, a = num;
      if (num < 0) { sign = 8; a = -num; }
      var s = pyFloatRepr(a);
      if (s.length < 7 && parseFloat(s) === a) {
        w.byte(sign + 8 * NUM_FLOATSTR);
        w.byte(s.length);
        w.raw(utf8EncodeSE(s));
      } else {
        w.byte(8 * NUM_FLOAT);
        var buf = new Uint8Array(8);
        new DataView(buf.buffer).setFloat64(0, num, false);
        w.raw(buf);
      }
      return;
    }
    if (num > -4096 && num < 4096) {
      if (num >= 0 && num < 128) {
        w.byte(num * 2 + 1);
      } else {
        var sg = 0, n = num;
        if (n < 0) { sg = 8; n = -n; }
        n = n * 16 + sg + 4;
        w.byte(n % 256);
        w.byte(Math.floor(n / 256));
      }
      return;
    }
    var sgn = 0, nn = num;
    if (nn < 0) { sgn = 8; nn = -nn; }
    var req = reqBytesNum(nn);
    w.byte(sgn + 8 * NUMBER_IDX[req]);
    w.uint(nn, req);
  }

  function writeString(w, s) {
    var ref = w.strs.get(s);
    if (ref !== undefined) {
      var rq = reqBytes(ref);
      w.byte(8 * STRREF_IDX[rq]);
      w.uint(ref, rq);
      return;
    }
    var b = utf8EncodeSE(s);
    var n = b.length;
    if (n < 16) {
      w.byte(16 * n + 4 * 0 + 2);
    } else {
      var req = reqBytes(n);
      w.byte(8 * STR_IDX[req]);
      w.uint(n, req);
    }
    w.raw(b);
    if (n > 2) w.strs.set(s, w.strs.size + 1);
  }

  // (array_values, map_pairs) matching LibSerialize's layout rules.
  function splitTable(t) {
    var acount = 0;
    while (t.has(acount + 1) && t.get(acount + 1) !== null &&
           t.get(acount + 1) !== undefined) {
      acount += 1;
    }
    var arr = [];
    for (var i = 1; i <= acount; i++) arr.push(t.get(i));
    var mp = [];
    for (var e of t.entries()) {
      var k = e[0];
      if (typeof k === "number" && Number.isInteger(k) && k >= 1 && k <= acount)
        continue;
      mp.push(e);
    }
    return [arr, mp];
  }

  function writeTable(w, t) {
    var ref = w.tabs.get(t);
    if (ref !== undefined) {
      var rq = reqBytes(ref);
      w.byte(8 * TABREF_IDX[rq]);
      w.uint(ref, rq);
      return;
    }
    w.tabs.set(t, w.tabs.size + 1);

    var sp = splitTable(t);
    var arr = sp[0], mp = sp[1];
    var ac = arr.length, mc = mp.length;
    var i, req;

    if (mc === 0) {
      if (ac < 16) {
        w.byte(16 * ac + 4 * 2 + 2);
      } else {
        req = reqBytes(ac);
        w.byte(8 * ARR_IDX[req]);
        w.uint(ac, req);
      }
      for (i = 0; i < ac; i++) writeObj(w, arr[i]);
    } else if (ac !== 0) {
      if (mc < 5 && ac < 5) {
        var combined = (mc - 1) * 4 + ac - 1;
        w.byte(16 * combined + 4 * 3 + 2);
      } else {
        req = Math.max(reqBytes(mc), reqBytes(ac));
        w.byte(8 * MIX_IDX[req]);
        w.uint(ac, req);
        w.uint(mc, req);
      }
      for (i = 0; i < ac; i++) writeObj(w, arr[i]);
      for (i = 0; i < mc; i++) {
        writeObj(w, mp[i][0]);
        writeObj(w, mp[i][1]);
      }
    } else {
      if (mc < 16) {
        w.byte(16 * mc + 4 * 1 + 2);
      } else {
        req = reqBytes(mc);
        w.byte(8 * TAB_IDX[req]);
        w.uint(mc, req);
      }
      for (i = 0; i < mc; i++) {
        writeObj(w, mp[i][0]);
        writeObj(w, mp[i][1]);
      }
    }
  }

  function writeObj(w, v) {
    if (v === null || v === undefined) w.byte(8 * NIL);
    else if (typeof v === "boolean") w.byte(8 * (v ? BOOL_T : BOOL_F));
    else if (typeof v === "number") writeNumber(w, v);
    else if (typeof v === "string") writeString(w, v);
    else if (v instanceof LuaTable) writeTable(w, v);
    else if (Array.isArray(v)) {
      var t = new LuaTable();
      for (var i = 0; i < v.length; i++) t.set(i + 1, v[i]);
      writeTable(w, t);
    }
    else throw new Error("unserializable " + typeof v);
  }

  function serialize() {
    var w = new Writer();
    w.byte(1);
    for (var i = 0; i < arguments.length; i++) writeObj(w, arguments[i]);
    return w.bytes();
  }

  // ------------------------------------------------------------------ WA glue
  function waDecodeFull(s) {
    s = s.trim();
    if (s.indexOf("!WA:2!") === 0) s = s.slice(6);
    var payload = inflate(decodeForPrint(s));
    return { data: deserialize(payload), payload: payload };
  }

  function waDecode(s) { return waDecodeFull(s).data; }

  function waEncode(data, level) {
    return "!WA:2!" + encodeForPrint(deflate(serialize(data), level));
  }

  // -------------------------------------------------------------- validator
  // Prototype stub of ADR-003 D4: the two cheapest Tier-1/Tier-2 invariants —
  // unique display ids across the payload, and every leaf keeps its class
  // load gate (tests/run.py check 7's spirit). Full set is plan step 4.
  function waValidate(tree) {
    var errors = [];
    var d = tree.get("d");
    var c = tree.get("c");
    if (!(d instanceof LuaTable)) return ["payload has no root display (d)"];
    var all = [d].concat(c instanceof LuaTable ? c.arrayPart() : []);
    var seen = new Set();
    var i, a, id;
    for (i = 0; i < all.length; i++) {
      a = all[i];
      id = a.get("id");
      if (typeof id !== "string" || id === "") {
        errors.push("display #" + i + " has no id");
        continue;
      }
      if (seen.has(id)) errors.push('duplicate id: "' + id + '"');
      seen.add(id);
    }
    for (i = 0; i < all.length; i++) {
      a = all[i];
      if (a.has("controlledChildren")) continue; // groups/bands, not leaves
      id = a.get("id");
      var load = a.get("load");
      var cls = load instanceof LuaTable ? load.get("class") : undefined;
      var multi = cls instanceof LuaTable ? cls.get("multi") : undefined;
      var gated = load instanceof LuaTable &&
        load.get("use_class") === true &&
        cls instanceof LuaTable &&
        (typeof cls.get("single") === "string" ||
         (multi instanceof LuaTable && multi.size > 0));
      if (!gated) errors.push('leaf missing class load gate: "' + id + '"');
    }
    return errors;
  }

  // -------------------------------------------------------------- uid re-salt
  // wabuild.uid recipe: sha256(salt|seed) -> first 11 bytes through the
  // 62-char alphabet. Editor salts as "editor|<user-salt>|<original-uid>"
  // (ADR-003 D1) so an export takes WA's clean-import path.
  var UID_ALPHA = "abcdefghijklmnopqrstuvwxyz" +
                  "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";

  // Compact synchronous SHA-256 (FIPS 180-4), so re-salt works identically in
  // node and browser without async crypto.subtle plumbing.
  var SHA_K = [
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1,
    0x923f82a4, 0xab1c5ed5, 0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
    0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174, 0xe49b69c1, 0xefbe4786,
    0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147,
    0x06ca6351, 0x14292967, 0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
    0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85, 0xa2bfe8a1, 0xa81a664b,
    0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a,
    0x5b9cca4f, 0x682e6ff3, 0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
    0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
  ];

  function sha256(msgBytes) {
    var h = [0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
             0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19];
    var len = msgBytes.length;
    var withOne = len + 1;
    var total = Math.ceil((withOne + 8) / 64) * 64;
    var m = new Uint8Array(total);
    m.set(msgBytes);
    m[len] = 0x80;
    var bitLen = len * 8;
    var dvTail = new DataView(m.buffer);
    dvTail.setUint32(total - 8, Math.floor(bitLen / 4294967296), false);
    dvTail.setUint32(total - 4, bitLen >>> 0, false);
    var w = new Array(64);
    for (var off = 0; off < total; off += 64) {
      var dv = new DataView(m.buffer, off, 64);
      for (var t = 0; t < 16; t++) w[t] = dv.getUint32(t * 4, false);
      for (t = 16; t < 64; t++) {
        var x = w[t - 15], y = w[t - 2];
        var s0 = ((x >>> 7) | (x << 25)) ^ ((x >>> 18) | (x << 14)) ^ (x >>> 3);
        var s1 = ((y >>> 17) | (y << 15)) ^ ((y >>> 19) | (y << 13)) ^ (y >>> 10);
        w[t] = (w[t - 16] + s0 + w[t - 7] + s1) >>> 0;
      }
      var a = h[0], b = h[1], c = h[2], d = h[3];
      var e = h[4], f = h[5], g = h[6], hh = h[7];
      for (t = 0; t < 64; t++) {
        var S1 = ((e >>> 6) | (e << 26)) ^ ((e >>> 11) | (e << 21)) ^
                 ((e >>> 25) | (e << 7));
        var ch = (e & f) ^ (~e & g);
        var t1 = (hh + S1 + ch + SHA_K[t] + w[t]) >>> 0;
        var S0 = ((a >>> 2) | (a << 30)) ^ ((a >>> 13) | (a << 19)) ^
                 ((a >>> 22) | (a << 10));
        var maj = (a & b) ^ (a & c) ^ (b & c);
        var t2 = (S0 + maj) >>> 0;
        hh = g; g = f; f = e; e = (d + t1) >>> 0;
        d = c; c = b; b = a; a = (t1 + t2) >>> 0;
      }
      h[0] = (h[0] + a) >>> 0; h[1] = (h[1] + b) >>> 0;
      h[2] = (h[2] + c) >>> 0; h[3] = (h[3] + d) >>> 0;
      h[4] = (h[4] + e) >>> 0; h[5] = (h[5] + f) >>> 0;
      h[6] = (h[6] + g) >>> 0; h[7] = (h[7] + hh) >>> 0;
    }
    var out = new Uint8Array(32);
    var odv = new DataView(out.buffer);
    for (var k = 0; k < 8; k++) odv.setUint32(k * 4, h[k], false);
    return out;
  }

  function saltedUid(userSalt, originalUid) {
    var seed = "editor|" + userSalt + "|" + originalUid;
    var digest = sha256(utf8EncodeSE(seed));
    var out = "";
    for (var i = 0; i < 11; i++) out += UID_ALPHA[digest[i] % UID_ALPHA.length];
    return out;
  }

  function resaltUids(tree, userSalt) {
    var d = tree.get("d");
    var c = tree.get("c");
    var all = [d].concat(c instanceof LuaTable ? c.arrayPart() : []);
    for (var i = 0; i < all.length; i++) {
      var a = all[i];
      if (a instanceof LuaTable && typeof a.get("uid") === "string") {
        a.set("uid", saltedUid(userSalt, a.get("uid")));
      }
    }
    return tree;
  }

  // -------------------------------------- canonical JSON (A1 parity oracle)
  // Byte-identical twin of the Python dump in proto-pydump.py: arrays for
  // pure array parts, prefixed sorted keys otherwise, Python json.dumps
  // ensure_ascii escaping, Python repr() float formatting.
  function jsonEscape(s) {
    var out = '"';
    for (var i = 0; i < s.length; i++) {
      var c = s.charCodeAt(i);
      if (c === 0x22) out += '\\"';
      else if (c === 0x5C) out += "\\\\";
      else if (c === 0x08) out += "\\b";
      else if (c === 0x09) out += "\\t";
      else if (c === 0x0A) out += "\\n";
      else if (c === 0x0C) out += "\\f";
      else if (c === 0x0D) out += "\\r";
      else if (c < 0x20 || c > 0x7E)
        out += "\\u" + ("0000" + c.toString(16)).slice(-4);
      else out += s[i];
    }
    return out + '"';
  }

  function jsonNumber(v) {
    if (Number.isInteger(v)) return String(v);
    return v < 0 ? "-" + pyFloatRepr(-v) : pyFloatRepr(v);
  }

  function canonicalJson(v) {
    if (v === null || v === undefined) return "null";
    if (typeof v === "boolean") return v ? "true" : "false";
    if (typeof v === "number") return jsonNumber(v);
    if (typeof v === "string") return jsonEscape(v);
    if (v instanceof LuaTable) {
      var sp = splitTable(v);
      var arr = sp[0], mp = sp[1];
      var parts = [], i;
      if (mp.length === 0) {
        for (i = 0; i < arr.length; i++) parts.push(canonicalJson(arr[i]));
        return "[" + parts.join(",") + "]";
      }
      var keyed = [];
      for (i = 0; i < arr.length; i++)
        keyed.push(["n:" + (i + 1), arr[i]]);
      for (i = 0; i < mp.length; i++) {
        var k = mp[i][0], kk;
        if (typeof k === "boolean") kk = k ? "b:true" : "b:false";
        else if (typeof k === "number")
          kk = "n:" + (Number.isInteger(k) ? String(k)
                       : (k < 0 ? "-" + pyFloatRepr(-k) : pyFloatRepr(k)));
        else kk = "s:" + k;
        keyed.push([kk, mp[i][1]]);
      }
      keyed.sort(function (a, b) { return a[0] < b[0] ? -1 : a[0] > b[0] ? 1 : 0; });
      for (i = 0; i < keyed.length; i++)
        parts.push(jsonEscape(keyed[i][0]) + ":" + canonicalJson(keyed[i][1]));
      return "{" + parts.join(",") + "}";
    }
    throw new Error("uncanonicalizable " + typeof v);
  }

  return {
    ALPHA: ALPHA,
    LuaTable: LuaTable,
    decodeForPrint: decodeForPrint,
    encodeForPrint: encodeForPrint,
    inflate: inflate,
    deflate: deflate,
    deserialize: deserialize,
    serialize: serialize,
    waDecode: waDecode,
    waDecodeFull: waDecodeFull,
    waEncode: waEncode,
    waValidate: waValidate,
    saltedUid: saltedUid,
    resaltUids: resaltUids,
    canonicalJson: canonicalJson,
    pyFloatRepr: pyFloatRepr,
    utf8DecodeSE: utf8DecodeSE,
    utf8EncodeSE: utf8EncodeSE
  };
});
