#!/usr/bin/env node
/* ADR-003 D5 acceptance gates A1-A4 for the JS codec prototype.
 *
 * Run: node prototype/editor/test.js        (from anywhere; paths are derived)
 * Requires python3 on PATH — A1 and A3 cross-check against the reference
 * Python codec (tools/wacodec.py) via proto-pydump.py / proto-pydiff.py.
 * A5 (in-game import) is a human step; see README.md.
 */
"use strict";
const fs = require("fs");
const os = require("os");
const path = require("path");
const cp = require("child_process");
const wacodec = require("./wacodec.js");

const HERE = __dirname;
const REPO = path.resolve(HERE, "..", "..");
const PACK = path.join(REPO, "docs", "packs", "runemaster", "runemaster-coa.txt");
const EDIT_ID = "RM Riftblade Offense Zenith";

let failures = 0;
function gate(name, ok, evidence) {
  console.log((ok ? "PASS" : "FAIL") + " " + name + " — " + evidence);
  if (!ok) failures += 1;
}
function py(args) {
  const r = cp.spawnSync("python3", args, {
    cwd: REPO, encoding: "utf8", maxBuffer: 64 * 1024 * 1024,
  });
  if (r.status !== 0) throw new Error("python3 failed: " + r.stderr);
  return r.stdout;
}

const packStr = fs.readFileSync(PACK, "utf8");

// ---------------------------------------------------------------- A1 parity
{
  const full = wacodec.waDecodeFull(packStr);
  const rootId = full.data.get("d").get("id");
  const childCount = full.data.get("c").arrayPart().length;
  const jsDump = wacodec.canonicalJson(full.data);

  const out = py([path.join(HERE, "proto-pydump.py"), PACK]);
  const nl = out.indexOf("\n");
  const meta = out.slice(0, nl); // "META <root id>\t<count>"
  const pyDump = out.slice(nl + 1);
  const m = meta.match(/^META (.*)\t(\d+)$/);
  const pyRootId = m[1];
  const pyCount = parseInt(m[2], 10);

  const ok = rootId === pyRootId && childCount === pyCount && jsDump === pyDump;
  gate("A1 decode parity", ok,
       'root id "' + rootId + '" (py: "' + pyRootId + '"), children ' +
       childCount + " (py: " + pyCount + "), canonical JSON " +
       jsDump.length + " chars " +
       (jsDump === pyDump ? "byte-identical" : "DIFFER"));
}

// ------------------------------------------------------- A2 zero-edit fidelity
{
  const full = wacodec.waDecodeFull(packStr);
  const rePayload = wacodec.serialize(full.data);
  const payloadOk = Buffer.from(rePayload).equals(Buffer.from(full.payload));

  const outStr = wacodec.waEncode(full.data);
  const stringOk = outStr === packStr.trim();

  gate("A2 zero-edit payload fidelity", payloadOk,
       "payload " + full.payload.length + " bytes, re-serialized " +
       rePayload.length + " bytes, " +
       (payloadOk ? "byte-identical" : "DIFFER"));
  console.log("  A2 record (UNKNOWN-1): full output string " +
              (stringOk ? "IS" : "is NOT") + " byte-identical to input (" +
              outStr.length + " vs " + packStr.trim().length + " chars)");
}

// ----------------------------------------------------------- A3 edit locality
{
  const tree = wacodec.waDecode(packStr);
  const kids = tree.get("c").arrayPart();
  const leaf = kids.find((k) => k.get("id") === EDIT_ID);
  if (!leaf) throw new Error("edit target not found: " + EDIT_ID);
  const w0 = leaf.get("width"), h0 = leaf.get("height");
  if (w0 !== 26 || h0 !== 26 || !Number.isInteger(w0) || !Number.isInteger(h0))
    throw new Error("edit target not 26x26 int: " + w0 + "x" + h0);
  leaf.set("width", 34);
  leaf.set("height", 34);
  const editedStr = wacodec.waEncode(tree);

  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "proto-editor-"));
  const editedFile = path.join(tmp, "proto-edited.txt");
  fs.writeFileSync(editedFile, editedStr);
  const diffOut = py([path.join(HERE, "proto-pydiff.py"), PACK, editedFile])
    .trim();
  const lines = diffOut === "" ? [] : diffOut.split("\n");
  const want = new Set([
    "c[" + EDIT_ID + "].width\t26\t34",
    "c[" + EDIT_ID + "].height\t26\t34",
  ]);
  const ok = lines.length === 2 && lines.every((l) => want.has(l));
  gate("A3 edit locality (python cross-decode)", ok,
       lines.length + " differing field(s): " +
       (lines.length ? lines.map((l) => l.replace(/\t/g, " ")).join("; ")
                     : "none"));
  fs.rmSync(tmp, { recursive: true, force: true });

  // the edited tree must still validate clean (feeds A4's positive case)
  const errs = wacodec.waValidate(tree);
  gate("A4a validator passes edited tree", errs.length === 0,
       errs.length === 0 ? "0 errors on edited tree" : errs.join("; "));
}

// -------------------------------------------------------------- A4 validator
{
  const pristine = wacodec.waDecode(packStr);
  const clean = wacodec.waValidate(pristine);
  gate("A4b validator passes shipped pack", clean.length === 0,
       clean.length === 0 ? "0 errors on pristine decode" : clean.join("; "));

  const dup = wacodec.waDecode(packStr);
  const dupKids = dup.get("c");
  dupKids.get(2).set("id", dupKids.get(1).get("id"));
  const dupErrs = wacodec.waValidate(dup);
  const dupOk = dupErrs.some((e) => e.indexOf("duplicate id") === 0);
  gate("A4c validator refuses duplicated id", dupOk,
       dupErrs.length + " error(s): " + (dupErrs[0] || "none"));

  const ungated = wacodec.waDecode(packStr);
  const uLeaf = ungated.get("c").arrayPart()
    .find((k) => k.get("id") === EDIT_ID);
  uLeaf.get("load").delete("use_class");
  const uErrs = wacodec.waValidate(ungated);
  const uOk = uErrs.some((e) => e.indexOf("leaf missing class load gate") === 0);
  gate("A4d validator refuses missing class gate", uOk,
       uErrs.length + " error(s): " + (uErrs[0] || "none"));
}

// ------------------------- corpus sweep (plan step 1: settles UNKNOWN-2 broadly)
{
  const globs = [];
  const packRoot = path.join(REPO, "docs", "packs");
  for (const cls of fs.readdirSync(packRoot)) {
    const dir = path.join(packRoot, cls);
    if (!fs.statSync(dir).isDirectory()) continue;
    for (const f of fs.readdirSync(dir))
      if (f.endsWith(".txt")) globs.push(path.join(dir, f));
  }
  const community = path.join(REPO, "resources", "import-strings");
  if (fs.existsSync(community))
    for (const f of fs.readdirSync(community))
      if (f.endsWith(".txt")) globs.push(path.join(community, f));

  let payloadFail = [], stringSame = 0;
  for (const f of globs) {
    const s = fs.readFileSync(f, "utf8");
    const full = wacodec.waDecodeFull(s);
    const re = wacodec.serialize(full.data);
    if (!Buffer.from(re).equals(Buffer.from(full.payload)))
      payloadFail.push(path.relative(REPO, f));
    if (wacodec.waEncode(full.data) === s.trim()) stringSame += 1;
  }
  gate("A2-corpus payload fidelity (" + globs.length + " strings)",
       payloadFail.length === 0,
       payloadFail.length === 0
         ? "payload byte-identical on all " + globs.length +
           "; full-string identical on " + stringSame + "/" + globs.length
         : "FAILED on: " + payloadFail.join(", "));
}

console.log(failures === 0 ? "\nall gates green" : "\n" + failures + " gate(s) FAILED");
process.exit(failures === 0 ? 0 : 1);
