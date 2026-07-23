"use strict";
const fs = require("fs");
const path = require("path");
const vm = require("vm");

const csvPath = path.join("20260723", "Copy of COOIS.csv");
const xlsxPath = path.join("20260723", "Copy of COOIS.xlsx");

function splitLine(line, delimiter) {
  const cells = [];
  let current = "";
  let inQuotes = false;
  for (let i = 0; i < line.length; i += 1) {
    const char = line[i];
    if (char === '"') {
      if (inQuotes && line[i + 1] === '"') {
        current += '"';
        i += 1;
      } else {
        inQuotes = !inQuotes;
      }
      continue;
    }
    if (char === delimiter && !inQuotes) {
      cells.push(current);
      current = "";
      continue;
    }
    current += char;
  }
  cells.push(current);
  return cells;
}

function detectDelimiter(text) {
  const sample = text.slice(0, 4000);
  const counts = { "\t": 0, ",": 0, ";": 0 };
  for (const ch of sample) {
    if (ch in counts) counts[ch] += 1;
  }
  if (counts["\t"] >= counts[","] && counts["\t"] >= counts[";"]) return "\t";
  if (counts[";"] > counts[","]) return ";";
  return ",";
}

function parseTextTable(text) {
  const trimmed = String(text || "").replace(/^\uFEFF/, "").trim();
  if (!trimmed) return { headers: [], rows: [] };
  const delimiter = detectDelimiter(trimmed);
  const lines = trimmed.split(/\r?\n/).filter((line) => line.length);
  const rawRows = lines.map((line) => splitLine(line, delimiter));
  return { delimiter, lineCount: lines.length, cols: rawRows[0]?.length || 0, rawRows };
}

console.log("=== CSV ===");
const t0 = Date.now();
const text = fs.readFileSync(csvPath, "utf8");
console.log("read ms", Date.now() - t0, "chars", text.length);
try {
  const t1 = Date.now();
  const parsed = parseTextTable(text);
  console.log(
    "parseTextTable ms",
    Date.now() - t1,
    "lines",
    parsed.lineCount,
    "cols",
    parsed.cols,
    "heapMB",
    Math.round(process.memoryUsage().heapUsed / 1048576)
  );
} catch (err) {
  console.error("CSV FAIL", err && err.stack ? err.stack : err);
}

console.log("=== XLSX SheetJS ===");
const code = fs.readFileSync(path.join("vendor", "xlsx.full.min.js"), "utf8");
const sandbox = {
  console,
  Buffer,
  ArrayBuffer,
  Uint8Array,
  DataView,
  TextDecoder,
  setTimeout,
  clearTimeout,
};
sandbox.global = sandbox;
sandbox.window = sandbox;
sandbox.self = sandbox;
vm.createContext(sandbox);
vm.runInContext(code, sandbox);
const XLSX = sandbox.XLSX;
const buf = fs.readFileSync(xlsxPath);
console.log("xlsx bytes", buf.length);
try {
  const t2 = Date.now();
  const wb = XLSX.read(buf, { type: "buffer", cellDates: false, raw: false });
  const name = wb.SheetNames[0];
  const matrix = XLSX.utils.sheet_to_json(wb.Sheets[name], {
    header: 1,
    defval: "",
    blankrows: false,
  });
  console.log("xlsx ok ms", Date.now() - t2, "rows", matrix.length, "sheet", name);
} catch (err) {
  console.error("XLSX FAIL", err && err.message ? err.message : err);
}
