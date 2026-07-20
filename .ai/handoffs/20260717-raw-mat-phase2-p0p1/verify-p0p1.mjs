/**
 * Lightweight verification for Phase 2 pure helpers and contracts.
 * Does not read real business Excel files.
 */
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const htmlPath = path.resolve(__dirname, "../../..", "vlookup-web.html");
const html = fs.readFileSync(htmlPath, "utf8");

assert.match(html, /Version: 1\.1\.0/);
assert.match(html, /function markResultDirty\(/);
assert.match(html, /function downloadXlsx\(/);
assert.match(html, /elements\.exportXlsx\.addEventListener\("click", downloadXlsx\)/);
assert.match(html, /if \(!key\) continue;/);
assert.match(html, /\\uFEFF/);
assert.match(html, /function formatCellDate\(/);
assert.match(html, /elements\.caseSensitive\.addEventListener\("change", markResultDirty\)/);
assert.match(html, /elements\.firstOnly\.addEventListener\("change", markResultDirty\)/);

function csvEscape(value) {
  let text = String(value ?? "");
  if (/^[=+\-@\t\r]/.test(text)) text = `'${text}`;
  return /[",\r\n]/.test(text) ? `"${text.replace(/"/g, '""')}"` : text;
}

function formatCellDate(value) {
  const text = String(value ?? "").trim();
  if (!text) return "";
  const serial = Number(text);
  if (Number.isFinite(serial) && serial >= 20000 && serial < 100000) {
    const whole = Math.floor(serial);
    const fraction = serial - whole;
    const date = new Date(Date.UTC(1899, 11, 30 + whole));
    const y = date.getUTCFullYear();
    const m = String(date.getUTCMonth() + 1).padStart(2, "0");
    const d = String(date.getUTCDate()).padStart(2, "0");
    if (fraction < 1e-10) return `${y}-${m}-${d}`;
    const totalSeconds = Math.round(fraction * 86400);
    const hh = String(Math.floor(totalSeconds / 3600) % 24).padStart(2, "0");
    const mm = String(Math.floor((totalSeconds % 3600) / 60)).padStart(2, "0");
    const ss = String(totalSeconds % 60).padStart(2, "0");
    return `${y}-${m}-${d} ${hh}:${mm}:${ss}`;
  }
  return text;
}

assert.equal(csvEscape("=cmd"), "'=cmd");
assert.equal(csvEscape("ok"), "ok");
assert.equal(formatCellDate("46204"), "2026-07-01");
assert.match(formatCellDate("46204.4416666667"), /^2026-07-01 /);

function normalize(value, caseSensitive = false) {
  const text = String(value ?? "").trim();
  return caseSensitive ? text : text.toLowerCase();
}

function buildIndex(rows, keyIndex) {
  const map = new Map();
  for (const row of rows) {
    const key = normalize(row[keyIndex]);
    if (!key) continue;
    if (!map.has(key)) map.set(key, []);
    map.get(key).push(row);
  }
  return map;
}

const index = buildIndex(
  [
    ["", "A"],
    ["SO1", "M1"],
    ["  ", "B"]
  ],
  0
);
assert.equal(index.has(""), false);
assert.equal(index.get("so1")?.length, 1);
assert.equal(index.get(normalize("")) || undefined, undefined);

console.log("verify-p0p1: OK");
